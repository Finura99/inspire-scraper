import logging

from config import (
    MAX_ARTICLES_PER_SOURCE,
    REQUEST_DELAY_SECONDS,
    SOURCES,
)

from src.fetcher import Fetcher

from src.filters import (
    classify_article,
    describe_opportunity,
)

from src.output import save_to_csv

from src.parser import (
    extract_article_text,
    extract_articles,
)

from src.summarizer import summarise_article


LOGGER = logging.getLogger(__name__)


def run_pipeline(
    sources=None,
    fetcher=None,
    per_source_limit=MAX_ARTICLES_PER_SOURCE,
):

    sources = SOURCES if sources is None else sources

    owns_fetcher = fetcher is None

    fetcher = (
        fetcher
        if fetcher is not None
        else Fetcher(REQUEST_DELAY_SECONDS)
    )

    results = []
    seen_urls = set()

    try:

        for source in sources:

            LOGGER.info(
                "Checking %s",
                source["name"],
            )

            listing = fetcher.fetch_page(
                source["url"]
            )

            if not listing:
                continue

            articles = extract_articles(
                listing,
                source,
                limit=per_source_limit,
            )

            LOGGER.info(
                "Discovered %d candidate articles at %s",
                len(articles),
                source["name"],
            )

            for article in articles:

                url = article["article_url"]

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                article_html = fetcher.fetch_page(url)

                article["content"] = (
                    extract_article_text(article_html)
                    if article_html
                    else ""
                )

                matched = classify_article(article)

                if not matched:
                    continue

                results.append({
                    "source": article["source"],
                    "title": article["title"],
                    "published": article["published"],

                    "categories": "; ".join(
                        matched
                    ),

                    "matched_terms": "; ".join(
                        f"{name}: {', '.join(terms)}"
                        for name, terms in matched.items()
                    ),

                    "summary": summarise_article(
                        article,
                        matched,
                    ),

                    "why_relevant": describe_opportunity(
                        matched
                    ),

                    "article_url": url,

                    "review_status":
                        "Unverified - review original article",
                })

    finally:

        if owns_fetcher:
            fetcher.close()

    return results


def main():

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    results = run_pipeline()

    save_to_csv(results)

    print(
        f"Found {len(results)} potential "
        "opportunity articles. Saved to results.csv"
    )

    if not results:

        print(
            "No matches this run. Review source "
            "accessibility, log messages and keywords."
        )


if __name__ == "__main__":
    main()