from fetcher import fetch_page
from parser import extract_emails
from filters import filter_emails
from output import save_to_csv
from config import SOURCES


def main():

    results = []

    for source in SOURCES:

        print(f"Scanning: {source['name']}")

        html = fetch_page(source["url"])

        if not html:
            continue

        contacts = extract_emails(
            html,
            source["url"],
            source["name"]
        )

        results.extend(contacts)

    # Keep only relevant departmental contacts
    filtered_results = filter_emails(results)

    # Remove duplicate email addresses
    unique_results = {
        result["email"]: result
        for result in filtered_results
    }

    final_results = list(unique_results.values())

    save_to_csv(final_results)

    print(f"Total extracted: {len(results)}")
    print(f"Relevant unique contacts: {len(final_results)}")


if __name__ == "__main__":
    main()