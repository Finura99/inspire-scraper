import re
import xml.etree.ElementTree as ET

from urllib.parse import (
    parse_qsl,
    urlencode,
    urljoin,
    urlsplit,
    urlunsplit,
)

from bs4 import BeautifulSoup


TRACKING_PARAMETERS = {
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
}


def clean_text(value):

    soup = BeautifulSoup(
        value or "",
        "html.parser",
    )

    text = soup.get_text(" ", strip=True)

    return re.sub(r"\s+", " ", text).strip()


def canonical_url(href, base_url):

    absolute = urljoin(base_url, href or "")

    parts = urlsplit(absolute)

    if parts.scheme not in {"http", "https"} or not parts.hostname:
        return ""

    query = urlencode([
        (key, value)
        for key, value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if not key.lower().startswith("utm_")
        and key.lower() not in TRACKING_PARAMETERS
    ])

    path = parts.path.rstrip("/") or "/"

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            path,
            query,
            "",
        )
    )


def same_website(url, source_url):

    first = (
        urlsplit(url).hostname or ""
    ).removeprefix("www.")

    second = (
        urlsplit(source_url).hostname or ""
    ).removeprefix("www.")

    return bool(first and first == second)


def _item(source, title, href, description="", published=""):

    url = canonical_url(
        href,
        source["url"],
    )

    title = clean_text(title)

    if (
        not url
        or not same_website(url, source["url"])
        or len(title) < 12
    ):
        return None

    return {
        "source": source["name"],
        "title": title,
        "article_url": url,
        "description": clean_text(description),
        "published": clean_text(published),
    }


def _parse_rss(xml_text, source):

    try:
        root = ET.fromstring(xml_text)

    except ET.ParseError:
        return []

    articles = []

    for item in root.findall(".//item"):

        article = _item(
            source,
            item.findtext("title", default=""),
            item.findtext("link", default=""),
            item.findtext("description", default=""),
            item.findtext("pubDate", default=""),
        )

        if article:
            articles.append(article)

    for entry in root.findall(".//{*}entry"):

        link = next(
            (
                node.get("href", "")
                for node in entry.findall("{*}link")
                if node.get("rel", "alternate") == "alternate"
            ),
            "",
        )

        article = _item(
            source,
            entry.findtext("{*}title", default=""),
            link,
            entry.findtext("{*}summary", default=""),
            entry.findtext("{*}published", default=""),
        )

        if article:
            articles.append(article)

    return articles


def _parse_html(html, source):

    soup = BeautifulSoup(html, "html.parser")

    prefix = source.get("article_path_prefix", "")

    articles = []

    for link in soup.select("a[href]"):

        href = link.get("href", "")

        url = canonical_url(
            href,
            source["url"],
        )

        if not url or not same_website(url, source["url"]):
            continue

        path = urlsplit(url).path

        if prefix and (
            not path.startswith(prefix)
            or path.rstrip("/") == prefix.rstrip("/")
        ):
            continue

        title = link.get_text(" ", strip=True)

        if len(title) < 18 or len(title) > 180:
            continue

        container = link.find_parent("article")

        paragraph = (
            container.find("p")
            if container
            else None
        )

        if paragraph is None and link.parent:
            paragraph = link.parent.find_next_sibling("p")

        article = _item(
            source,
            title,
            url,
            (
                paragraph.get_text(" ", strip=True)
                if paragraph
                else ""
            ),
        )

        if article:
            articles.append(article)

    return articles


def extract_articles(content, source, limit=None):

    if limit is not None and limit <= 0:
        return []

    if source["kind"] == "rss":
        discovered = _parse_rss(content, source)

    else:
        discovered = _parse_html(content, source)

    seen = set()
    unique = []

    for article in discovered:

        if article["article_url"] in seen:
            continue

        seen.add(article["article_url"])

        unique.append(article)

        if limit is not None and len(unique) >= limit:
            break

    return unique


def extract_article_text(html):

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup.select(
        "script, style, nav, footer, header, aside, form, noscript"
    ):
        tag.decompose()

    for root in (
        soup.find("article"),
        soup.find("main"),
        soup.body,
    ):

        if not root:
            continue

        paragraphs = [
            p.get_text(" ", strip=True)
            for p in root.find_all("p")
        ]

        paragraphs = [
            p
            for p in paragraphs
            if len(p) >= 45
        ]

        if paragraphs:
            return " ".join(paragraphs[:18])[:7000]

    description = soup.find(
        "meta",
        attrs={"name": "description"},
    )

    return (
        description.get("content", "").strip()
        if description
        else ""
    )