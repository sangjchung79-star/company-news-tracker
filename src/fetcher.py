import os
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate

import requests
from dotenv import load_dotenv

from src.models import Article

load_dotenv()

NEWSAPI_URL = "https://newsapi.org/v2/everything"


def fetch_articles(company: str, max_results: int = 5) -> list[Article]:
    api_key = os.getenv("NEWSAPI_KEY")
    if not api_key or api_key == "your_key_here":
        raise ValueError("NEWSAPI_KEY is not set in your .env file")

    params = {
        "q": company,
        "sortBy": "publishedAt",
        "pageSize": max_results,
        "language": "en",
        "apiKey": api_key,
    }

    response = requests.get(NEWSAPI_URL, params=params, timeout=10)
    response.raise_for_status()

    articles = []
    for item in response.json().get("articles", []):
        articles.append(
            Article(
                date=item.get("publishedAt", "")[:10],
                source=item.get("source", {}).get("name", "Unknown"),
                title=item.get("title") or "",
                description=item.get("description") or "",
                url=item.get("url") or "",
            )
        )
    return articles


GOOGLE_NEWS_RSS = "https://news.google.com/rss/search"


def fetch_rss_articles(company: str, max_results: int = 5) -> list[Article]:
    url = f"{GOOGLE_NEWS_RSS}?q={urllib.parse.quote(company)}&hl=en-US&gl=US&ceid=US:en"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    channel = root.find("channel")
    if channel is None:
        return []

    articles = []
    for item in channel.findall("item")[:max_results]:
        raw_title = item.findtext("title") or ""
        title = raw_title.rsplit(" - ", 1)[0].strip()
        link = item.findtext("link") or ""
        pub_date_str = item.findtext("pubDate") or ""
        source_el = item.find("source")
        source = source_el.text if source_el is not None else "Google News"
        description = ""

        date = ""
        if pub_date_str:
            parsed = parsedate(pub_date_str)
            if parsed:
                date = datetime(*parsed[:6]).strftime("%Y-%m-%d")

        articles.append(
            Article(
                date=date, source=source, title=title, description=description, url=link
            )
        )

    return articles
