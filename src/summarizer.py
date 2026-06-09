import os

import anthropic
from dotenv import load_dotenv

from src.models import Article

load_dotenv()


def summarize_company_news(company: str, articles: list[Article]) -> str:
    if not articles:
        return ""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_key_here":
        return ""

    client = anthropic.Anthropic(api_key=api_key)
    article_lines = "\n".join(
        f"- [{a.date}] {a.source}: {a.title}"
        + (f" — {a.description}" if a.description else "")
        for a in articles
    )
    prompt = (
        f"Summarize the recent news about {company} below in 2-3 sentences. "
        "Cover the key themes and most important developments. "
        "Eliminate any redundant information. Write in plain prose, "
        "no bullet points.\n\n"
        f"{article_lines}"
    )
    try:
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}],
        )
        for block in message.content:
            if block.type == "text":
                return block.text
    except Exception as e:
        print(f"Warning: could not summarize {company}: {e}")
    return ""
