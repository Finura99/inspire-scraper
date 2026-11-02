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