import re

from config import OPPORTUNITY_CATEGORIES


def _contains_phrase(text, phrase):

    pattern = (
        r"(?<!\w)"
        + re.escape(phrase)
        + r"(?!\w)"
    )

    return re.search(
        pattern,
        text,
        re.IGNORECASE,
    ) is not None


def classify_article(article, categories=None):

    categories = (
        categories
        if categories is not None
        else OPPORTUNITY_CATEGORIES
    )

    title = article.get("title", "")
    description = article.get("description", "")
    body = article.get("content", "")

    matches = {}

    for category, phrases in categories.items():

        found = [
            phrase
            for phrase in phrases
            if any(
                _contains_phrase(segment, phrase)
                for segment in (
                    title,
                    description,
                    body,
                )
            )
        ]

        if found:
            matches[category] = found

    return matches


def describe_opportunity(matches):

    parts = [
        f"{category} (mentions: {', '.join(terms[:2])})"
        for category, terms in matches.items()
    ]

    return (
        "Possible relevance to "
        + "; ".join(parts)
        + ". Requires human review."
    )