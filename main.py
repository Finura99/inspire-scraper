import httpx
import csv
from bs4 import BeautifulSoup
from urllib.parse import urljoin


#url we want to scrape
url = "https://www.bbc.com/news"

def fetch_page(url):
    try:
        #send an HTTP GET request and store the server response
        response = httpx.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    except httpx.RequestError as error:
        print(f"Request failed: {error}")
        return None
        #no normal HTTP response was completed, raises for timeouts, dns failures, connection refused

    except httpx.HTTPStatusError as error:
        print(f"Bad response: {error.response.status_code}")
        return None
        #HTTP response came back, but status was an error


#parse the returned HTML into a structure BeautifulSoup can search
html = fetch_page(url)
if html:
    soup = BeautifulSoup(html, "html.parser")

#find every anchor tag (<a>) on the page
links = soup.find_all("a")

#store the scraped link data in memory
results = []

#set for uniqueness
seen_urls = set()




#extract readable text and destination URL from the first 10 links
for link in links[:10]:
    text = link.text.strip()
    href = link.get("href")
    
    if not text:
        continue

    if not href:
        continue

    full_url = urljoin(url, href)

    if full_url in seen_urls:
        continue

    seen_urls.add(full_url)

    results.append({
        "text": text,
        "url": full_url
    })

    #each scraped link becomes one structured dictionary


#keywords used to decide whether a result is relevant
keywords = ["business", "technology"]


def match_keywords(results, keywords):
    #store only results that match at least one keyword
    filtered_results = []

    #process each scraped result individually
    for result in results:
        text = result["text"].lower()

        #keep track of every keyword found in this result
        matched_keywords = []

        for keyword in keywords:
            if keyword in text:
                matched_keywords.append(keyword)

        #only keep the result if at least one keyword matched
        if matched_keywords:
            result["matched_keywords"] = matched_keywords
            filtered_results.append(result)

    return filtered_results


#run the filtering function and store its returned results
filtered_results = match_keywords(results, keywords)


#convert the keyword list into cleaner text for the CSV
for result in filtered_results:
    result["matched_keywords"] = ", ".join(result["matched_keywords"])


#export the filtered data into a CSV file
with open("results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["text", "url", "matched_keywords"]
    )

    #write the CSV column names, then write each result as a row
    writer.writeheader()
    writer.writerows(filtered_results)