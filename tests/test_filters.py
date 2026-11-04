from filters import classify_article, describe_opportunity
from summarizer import summarise_article


def test_classification_matches_two_fusion_service_areas():
    article = {
        "title": "Company considers interest rate risk strategy and debt financing",
        "description": "Treasury team will examine hedging options.",
        "content": "The issuer plans debt financing to support its operations.",
    }

    matches = classify_article(article)

    assert "Independent hedging" in matches
    assert "Capital raising" in matches
    assert "hedging" in matches["Independent hedging"]
    assert "Requires human review" in describe_opportunity(matches)


def test_does_not_match_partial_words():
    article = {
        "title": "A supermarket makes an announcement",
        "description": "",
        "content": "",
    }

    assert classify_article(article) == {}


def test_classifies_from_body_when_title_is_neutral():
    article = {
        "title": "Company announces treasury update",
        "description": "",
        "content": "The business plans a private credit facility to expand.",
    }

    assert "Illiquid financing solutions" in classify_article(article)


def test_summary_selects_evidence_sentences_in_source_order():
    article = {
        "content": (
            "The company employs hundreds of people across Europe. "
            "Management is reviewing a debt financing plan to support new investment. "
            "The proposal remains subject to approval."
        )
    }

    matches = {
        "Capital raising": ["debt financing"]
    }

    summary = summarise_article(article, matches)

    assert "debt financing" in summary
    assert "approval" not in summary
    assert len(summary) <= 290


def test_summary_has_fallback_for_unavailable_article():
    summary = summarise_article(
        {"content": "", "description": ""},
        {},
    )

    assert "review" in summary.lower()