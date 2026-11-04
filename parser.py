from bs4 import BeautifulSoup
from urllib.parse import urljoin

import re

def extract_emails(html, source_url, source_name):
    soup = BeautifulSoup(html, "html.parser")

    # Remove scripts and styles before searching page text
    for element in soup(["script", "style"]):
        element.decompose()

    emails = set()

    # Extract email addresses from mailto links
    for link in soup.find_all("a", href=True):
        href = link["href"]

        if href.lower().startswith("mailto:"):
            email = href[7:].split("?")[0].strip().lower()
            emails.add(email)

    # Extract email addresses visible in page text
    pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"

    for email in re.findall(pattern, soup.get_text(" ")):
        emails.add(email.lower())

    results = []

    for email in sorted(emails):
        results.append({
            "source": source_name,
            "email": email,
            "url": source_url
        })

    return results