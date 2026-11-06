from src.parser import canonical_url, extract_article_text, extract_articles


RSS = """<?xml version="1.0"?>
<rss version="2.0"><channel>
  <item><title>Acme raises £50m in funding round</title>
    <link>https://news.example.com/articles/acme?utm_source=email</link>
    <description><![CDATA[<p>Acme secures a funding round.</p>]]></description>
    <pubDate>Wed, 04 Nov 2026 09:00:00 GMT</pubDate>
  </item>
  <item><title>Acme raises £50m in funding round</title>
    <link>https://news.example.com/articles/acme?utm_source=another</link></item>
  <item><title>External offsite article</title>
    <link>https://other.example.net/news/story</link></item>
</channel></rss>"""

SOURCE_RSS = {
    "name": "Example News",
    "url": "https://news.example.com/feed",
    "kind": "rss",
}

SOURCE_HTML = {
    "name": "Example News",
    "url": "https://news.example.com/news-and-insight",
    "kind": "html",
    "article_path_prefix": "/news-and-insight/",
}


def test_rss_extracts_real_articles_and_deduplicates():
    articles = extract_articles(RSS, SOURCE_RSS)

    assert len(articles) == 1
    assert articles[0]["article_url"] == (
        "https://news.example.com/articles/acme"
    )
    assert articles[0]["description"] == (
        "Acme secures a funding round."
    )
    assert articles[0]["published"].startswith("Wed")


def test_atom_feed():
    xml = """<feed xmlns="http://www.w3.org/2005/Atom">
      <entry><title>Bank announces structured derivatives project</title>
      <link rel="alternate" href="https://news.example.com/bank-story" />
      <summary>New derivatives initiative</summary></entry></feed>"""

    articles = extract_articles(xml, SOURCE_RSS)

    assert articles[0]["title"].startswith("Bank")


def test_html_ignores_navigation_footer_external_links():
    html = """<html><body>
    <a href="/contact-us">Contact us</a>
    <a href="/news-and-insight/">News and insight</a>
    <a href="https://outside.example.net/news-and-insight/something">Offsite finance story</a>
    <article><h2><a href="/news-and-insight/blog/bond-issue">Issuer explores debt financing solutions</a></h2>
    <p>The issuer is reviewing new financing routes.</p></article>
    <a href="/news-and-insight/blog/bond-issue#top">Issuer explores debt financing solutions</a>
    </body></html>"""

    articles = extract_articles(html, SOURCE_HTML)

    assert len(articles) == 1
    assert articles[0]["description"] == (
        "The issuer is reviewing new financing routes."
    )


def test_zero_limit_yields_no_articles():
    assert extract_articles(RSS, SOURCE_RSS, limit=0) == []


def test_html_empty_or_bad_rss_does_not_crash():
    assert extract_articles("<not xml", SOURCE_RSS) == []
    assert extract_articles("", SOURCE_HTML) == []


def test_canonical_url_rejects_non_http_schemes_and_removes_trackers():
    assert canonical_url(
        "mailto:abc@test.com",
        "https://news.example.com",
    ) == ""

    assert canonical_url(
        "javascript:alert(1)",
        "https://news.example.com",
    ) == ""

    assert canonical_url(
        "/item/?utm_campaign=x&ref=123#section",
        "https://news.example.com",
    ) == "https://news.example.com/item?ref=123"


def test_article_body_strips_chrome_and_prefers_article():
    html = """<html><body>
    <header><p>Navigation controls for our website</p></header>
    <article>
      <p>The issuer is preparing a capital raising programme that may involve advisers.</p>
      <p>Management says the financing process is still preliminary and under review.</p>
    </article>
    <footer><p>Important footer information not part of the article</p></footer>
    </body></html>"""

    body = extract_article_text(html)

    assert "capital raising" in body
    assert "footer" not in body