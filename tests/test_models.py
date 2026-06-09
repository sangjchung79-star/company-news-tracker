from src.models import Article


def test_article_fields() -> None:
    article = Article(
        date="2026-06-09",
        source="TechCrunch",
        title="RapidSOS Raises $50M",
        description="A major funding round.",
        url="https://techcrunch.com/example",
    )
    assert article.date == "2026-06-09"
    assert article.source == "TechCrunch"
    assert article.title == "RapidSOS Raises $50M"
