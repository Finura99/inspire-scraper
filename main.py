import httpx
import csv
from bs4 import BeautifulSoup

url = "https://www.bbc.com/news"

response = httpx.get(url)

soup = BeautifulSoup(response.text, "html.parser")

links = soup.find_all("a")

results = []
# gives us somewhere to store the data
# each result is a dictionary


for link in links[:10]:
    text = link.text.strip()
    # removes messy spaces

    href = link.get("href")

    results.append({
        "text": text,
        "url": href
    })

print(results)



keywords = ["business", "technology"]


        # iterates over our structured resutls and applies a condition to keep only entries
        # whose text contains a target keyword.


# results = all scraped links
# text = visible text from one link
# keywords = words we care about


filtered_results = []

def match_keyword(results, keywords):

    for result in results:
        text = result["text"].lower()
        matched_keywords = []

        for keyword in keywords:
            if keyword in text:
                matched_keywords.append(keyword)
                filtered_results.append(result)

        if matched_keywords:
            result["matched_keywords"] = matched_keywords
            filtered_results.append(result)

    return filtered_results

##list
##└── dictionary
##    ├── text
##    ├── url
##    └── matched_keywords
##        ├── ai
##        ├── banking
##        └── technology


with open("results.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(
        file,
        fieldnames=["text", "url", "matched_keywords"]
    )

    writer.writeheader
    writer.writerows(filtered_results)