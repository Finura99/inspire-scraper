import csv


FIELDNAMES = [
    "source",
    "title",
    "published",
    "categories",
    "matched_terms",
    "summary",
    "why_relevant",
    "article_url",
    "review_status",
]


def _safe_csv_value(value):

    text = str(
        value if value is not None else ""
    )

    if text.lstrip().startswith(
        ("=", "+", "-", "@")
    ):
        return "'" + text

    return text


def save_to_csv(results, filename="results.csv"):

    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8-sig",
    ) as handle:

        writer = csv.DictWriter(
            handle,
            fieldnames=FIELDNAMES,
        )

        writer.writeheader()

        for result in results:

            writer.writerow({
                name: _safe_csv_value(
                    result.get(name, "")
                )
                for name in FIELDNAMES
            })