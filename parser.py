from bs4 import BeautifulSoup
from urllib.parse import urljoin


def extract_links(html, base_url, seen_urls):
    soup = BeautifulSoup(html, "html.parser")
    links = soup.find_all("a")

    results = []

    for link in links[:10]:
        text = link.text.strip()
        href = link.get("href")

        if not text:
            continue

        if not href:
            continue

        full_url = urljoin(base_url, href)

        if full_url in seen_urls:
            continue

        seen_urls.add(full_url)

        results.append({
            "text": text,
            "url": full_url
        })

    return results