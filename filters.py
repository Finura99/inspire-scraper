def match_keywords(results, keywords):
    filtered_results = []

    for result in results:
        text = result["text"].lower()
        matched_keywords = []

        for keyword in keywords:
            if keyword in text:
                matched_keywords.append(keyword)

        if matched_keywords:
            result["matched_keywords"] = matched_keywords
            filtered_results.append(result)

    return filtered_results

def filter_emails(results):

    relevant_prefixes = (
        "careers",
        "employers",
        "partnerships",
        "business",
        "training",
        "recruitment",
        "enquiries",
        "info",
        "contact",
        "enterprise",
        "engagement",
        "outreach",
    )

    filtered = []

    for result in results:
        email = result["email"].lower()
        local_part = email.split("@")[0]

        if local_part.startswith(relevant_prefixes):
            filtered.append(result)

    return filtered