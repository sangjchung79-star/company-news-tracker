import dataclasses
import json
from pathlib import Path

from src.models import Article


def save_articles(
    articles_by_company: dict[str, list[Article]], path: str = "articles.json"
) -> None:
    serializable = {
        company: [dataclasses.asdict(a) for a in articles]
        for company, articles in articles_by_company.items()
    }
    Path(path).write_text(json.dumps(serializable, indent=2))
    print(f"Saved to {path}")


def load_articles(path: str = "articles.json") -> dict[str, list[Article]]:
    data = json.loads(Path(path).read_text())
    return {
        company: [Article(**item) for item in items]
        for company, items in data.items()
    }
