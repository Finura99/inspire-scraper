import csv


def save_to_csv(results, filename="results.csv"):

    fieldnames = [
        "source",
        "email",
        "url"
    ]

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(results)