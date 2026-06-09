import subprocess

from src.display import print_articles
from src.fetcher import fetch_articles, fetch_rss_articles
from src.html_export import export_html
from src.models import Article
from src.storage import save_articles
from src.summarizer import summarize_company_news

COMPANIES = [
    "RapidSOS",
    "Unity Software",
    "Google Cloud",
]

# These companies also query NewsAPI in addition to Google News RSS.
# RapidSOS is excluded because NewsAPI returns nothing for it.
NEWSAPI_COMPANIES = {"Unity Software", "Google Cloud"}


def deduplicate(articles: list[Article]) -> list[Article]:
    seen_urls: set[str] = set()
    seen_titles: set[str] = set()
    unique = []
    for article in articles:
        url_key = article.url.strip()
        title_key = article.title.lower().strip()
        if url_key in seen_urls or title_key in seen_titles:
            continue
        seen_urls.add(url_key)
        seen_titles.add(title_key)
        unique.append(article)
    return unique


def main() -> None:
    articles_by_company: dict[str, list[Article]] = {}

    for company in COMPANIES:
        print(f"Fetching news for: {company}...")
        query = f'"{company}"'
        articles: list[Article] = []
        if company in NEWSAPI_COMPANIES:
            articles += fetch_articles(query)
        articles += fetch_rss_articles(query)
        articles_by_company[company] = deduplicate(articles)

    summaries: dict[str, str] = {}
    for company, articles in articles_by_company.items():
        print(f"Summarizing news for: {company}...")
        summaries[company] = summarize_company_news(company, articles)

    save_articles(articles_by_company)
    print_articles(articles_by_company)
    export_html(articles_by_company, summaries)
    subprocess.run(["open", "index.html"])


if __name__ == "__main__":
    main()
