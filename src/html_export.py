import html
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models import Article

COMPANY_DOMAINS: dict[str, str] = {
    "RapidSOS": "rapidsos.com",
    "Unity Software": "unity.com",
    "Google Cloud": "cloud.google.com",
}

_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Company News Tracker</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-50 min-h-screen font-sans">

  <header class="bg-slate-900 text-white px-6 py-5 shadow-md">
    <div class="max-w-4xl mx-auto flex items-baseline justify-between">
      <h1 class="text-2xl font-bold tracking-tight">Company News Tracker</h1>
      <span class="text-slate-400 text-sm">Updated {updated}</span>
    </div>
  </header>

  <main class="max-w-4xl mx-auto px-6 py-10 space-y-12">
    {sections}
  </main>

</body>
</html>"""

_SECTION = """
<section>
  <div class="flex items-center gap-3 mb-4 pb-3 border-b-2 border-blue-200">
    <img src="https://www.google.com/s2/favicons?domain={domain}&sz=64"
         alt="{company}" class="h-8 w-8 object-contain rounded"
         onerror="this.style.display='none'">
    <h2 class="text-lg font-semibold text-slate-700 uppercase
               tracking-widest">{company}</h2>
  </div>
  {summary_block}
  <div class="space-y-4">{cards}</div>
</section>"""

_SUMMARY = (
    '<div class="bg-blue-50 border border-blue-100 rounded-lg p-4 mb-5 '
    'text-sm text-slate-600 leading-relaxed">{text}</div>'
)

_CARD = """
<article class="bg-white rounded-xl border border-slate-100 shadow-sm p-5
                hover:shadow-md transition-shadow duration-150">
  <div class="flex items-center gap-2 mb-2 flex-wrap">
    <span class="text-xs font-semibold bg-blue-50 text-blue-700
                 px-2.5 py-0.5 rounded-full">{source}</span>
    <span class="text-xs text-slate-400">{date}</span>
  </div>
  <h3 class="font-semibold text-slate-900 leading-snug mb-1 text-base">
    <a href="{url}" target="_blank" rel="noopener noreferrer"
       class="hover:text-blue-600 transition-colors">{title}</a>
  </h3>
  {description_block}
</article>"""

_DESCRIPTION = '<p class="text-sm text-slate-500 leading-relaxed mt-1">{text}</p>'
_NO_ARTICLES = '<p class="text-slate-400 text-sm italic">No articles found.</p>'


def export_html(
    articles_by_company: dict[str, list[Article]],
    summaries: Optional[dict[str, str]] = None,
    path: str = "index.html",
) -> None:
    if summaries is None:
        summaries = {}

    sections_html = ""
    for company, articles in articles_by_company.items():
        if not articles:
            cards_html = _NO_ARTICLES
        else:
            cards_html = ""
            for article in sorted(articles, key=lambda a: a.date, reverse=True):
                desc_block = ""
                if article.description:
                    truncated = article.description[:200]
                    if len(article.description) > 200:
                        truncated += "…"
                    desc_block = _DESCRIPTION.format(text=html.escape(truncated))

                cards_html += _CARD.format(
                    source=html.escape(article.source),
                    date=html.escape(article.date),
                    url=html.escape(article.url),
                    title=html.escape(article.title),
                    description_block=desc_block,
                )

        summary_text = summaries.get(company, "")
        summary_block = (
            _SUMMARY.format(text=html.escape(summary_text)) if summary_text else ""
        )
        domain = COMPANY_DOMAINS.get(company, "")
        sections_html += _SECTION.format(
            company=html.escape(company),
            domain=domain,
            summary_block=summary_block,
            cards=cards_html,
        )

    updated = datetime.now().strftime("%B %d, %Y at %I:%M %p")
    page = _PAGE.format(updated=updated, sections=sections_html)
    Path(path).write_text(page, encoding="utf-8")
    print(f"Saved to {path}")
