from src.models import Article


def print_articles(articles_by_company: dict[str, list[Article]]) -> None:
    for company, articles in articles_by_company.items():
        print(f"\n{'=' * 50}")
        print(f"  {company}")
        print(f"{'=' * 50}")

        if not articles:
            print("  No articles found.")
            continue

        for article in articles:
            print(f"\n[{article.date}] {article.source}")
            print(f"  {article.title}")
            if article.description:
                print(f"  {article.description[:120]}...")
            print(f"  {article.url}")
