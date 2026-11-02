from fetcher import fetch_page
from parser import extract_links
from filters import match_keywords
from output import save_to_csv


# Websites we want to scrape
urls = [
    "https://www.bbc.com/news",
    "https://www.reuters.com/technology",
    "https://www.ft.com/technology"
]

# Store results collected across every website
results = []

# Keep track of URLs already collected across every website
seen_urls = set()


# Fetch and parse every configured website
for url in urls:
    html = fetch_page(url)

    if not html:
        continue

    page_results = extract_links(html, url, seen_urls)
    results.extend(page_results)


# Keywords used to decide whether a result is relevant
keywords = ["business", "technology"]

# Filter the collected results
filtered_results = match_keywords(results, keywords)

# Export the relevant results
save_to_csv(filtered_results)

print(f"Collected: {len(results)} results")
print(f"Matched: {len(filtered_results)} results")