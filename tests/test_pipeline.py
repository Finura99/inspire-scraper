import csv

from src.main import run_pipeline
from src.output import save_to_csv


class FakeFetcher:

    def __init__(self, pages):
        self.pages = pages
        self.called = []

    def fetch_page(self, url):
        self.called.append(url)
        return self.pages.get(url)


def test_full_pipeline_generates_relevant_reviewable_results(tmp_path):

    source = {
        "name": "Business Feed",
        "url": "https://example.org/rss",
        "kind": "rss",
    }

    feed = """<rss><channel>
      <item><title>Acme explores private credit financing</title>
        <link>https://example.org/articles/credit</link>
        <description>Acme considers private credit to support its expansion.</description>
      </item>
      <item><title>New office opening in the city</title>
        <link>https://example.org/articles/office</link>
      </item>
    </channel></rss>"""

    credit_page = """
    <article>
      <p>Acme is evaluating private credit to fund its next expansion.</p>
      <p>Its plans remain preliminary and may not result in any transaction.</p>
    </article>
    """

    fake = FakeFetcher({
        source["url"]: feed,
        "https://example.org/articles/credit": credit_page,
        "https://example.org/articles/office":
            "<article><p>Our new office has opened in the capital city.</p></article>",
    })

    results = run_pipeline(
        sources=[source],
        fetcher=fake,
        per_source_limit=3,
    )

    assert len(results) == 1

    assert results[0]["title"] == (
        "Acme explores private credit financing"
    )

    assert results[0]["categories"] == (
        "Illiquid financing solutions"
    )

    assert "private credit" in results[0]["summary"]

    assert results[0]["article_url"] == (
        "https://example.org/articles/credit"
    )

    assert results[0]["review_status"].startswith("Unverified")

    output = tmp_path / "results.csv"

    save_to_csv(results, output)

    with open(
        output,
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        rows = list(csv.DictReader(handle))

    assert len(rows) == 1

    assert rows[0]["article_url"] == (
        results[0]["article_url"]
    )


def test_missing_source_is_skipped():

    source = {
        "name": "Down",
        "url": "https://example.org/rss",
        "kind": "rss",
    }

    assert run_pipeline(
        sources=[source],
        fetcher=FakeFetcher({}),
    ) == []


def test_csv_does_not_mutate_and_escapes_excel_formulas(tmp_path):

    data = [{
        "title": '=HYPERLINK("bad")',
        "source": "Test",
        "article_url": "https://example.org",
    }]

    original = data[0].copy()

    path = tmp_path / "test.csv"

    save_to_csv(data, path)

    assert data[0] == original

    with open(
        path,
        encoding="utf-8-sig",
        newline="",
    ) as handle:
        first = next(csv.DictReader(handle))

    assert first["title"].startswith("'=")