import csv


def save_to_csv(results, filename="results.csv"):
    for result in results:
        result["matched_keywords"] = ", ".join(result["matched_keywords"])

    with open(filename, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=["text", "url", "matched_keywords"]
        )

        writer.writeheader()
        writer.writerows(results)