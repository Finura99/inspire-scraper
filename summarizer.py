import re

from filters import _contains_phrase


def summarise_article(article, matches, max_chars=290):

    content = (
        article.get("content")
        or article.get("description")
        or ""
    ).strip()

    if not content:
        return (
            "No readable article text available; "
            "review the original link."
        )

    sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z0-9£€\"'])",
        content,
    )

    sentences = [
        sentence.strip()
        for sentence in sentences
        if len(sentence.strip()) >= 30
    ]

    if not sentences:
        sentences = [content]

    terms = {
        term
        for group in matches.values()
        for term in group
    }

    ranked = sorted(
        enumerate(sentences),
        key=lambda pair: (
            -sum(
                _contains_phrase(pair[1], term)
                for term in terms
            ),
            pair[0],
        ),
    )

    selected_indexes = sorted(
        index
        for index, _ in ranked[:2]
    )

    selected = " ".join(
        sentences[index]
        for index in selected_indexes
    )

    if len(selected) <= max_chars:
        return selected

    shortened = (
        selected[:max_chars - 1]
        .rsplit(" ", 1)[0]
    )

    return (
        shortened or selected[:max_chars - 1]
    ) + "…"