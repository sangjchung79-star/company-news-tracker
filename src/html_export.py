import html
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from src.models import Article

COMPANY_DOMAINS: dict[str, str] = {
    "RapidSOS": "rapidsos.com",
    "Unity Software": "unity.com",
    "Google Cloud": "cloud.google.com",
}


def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
  <title>News Intelligence</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-white font-sans antialiased">
<div class="flex h-screen overflow-hidden">

  <!-- Sidebar -->
  <aside class="w-52 shrink-0 bg-slate-900 flex flex-col h-screen fixed left-0 top-0 z-10">

    <div class="px-5 pt-6 pb-4 border-b border-slate-700/50">
      <p class="text-white text-sm font-semibold tracking-tight">News Intelligence</p>
      <p class="text-slate-500 text-xs mt-1">{updated}</p>
    </div>

    <nav class="flex-1 overflow-y-auto px-3 py-4 space-y-0.5">
      <p class="text-slate-600 text-xs font-semibold uppercase tracking-widest px-2 mb-3">
        Companies
      </p>
      {nav_items}
    </nav>

    <div class="px-3 py-3 border-t border-slate-700/50">
      <button onclick="location.reload()"
              class="w-full flex items-center gap-2 px-3 py-2 rounded-md text-xs
                     text-slate-500 hover:text-white hover:bg-slate-800 transition-colors duration-150">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-3.5 w-3.5 shrink-0" viewBox="0 0 20 20" fill="currentColor">
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd"/>
        </svg>
        Refresh page
      </button>
    </div>

  </aside>

  <!-- Main content -->
  <main class="ml-52 flex-1 overflow-y-auto bg-white" id="main-scroll">
    <div class="px-12 py-12 space-y-16">
      {sections}
    </div>
  </main>

</div>

<script>
  /* ---------- sidebar scroll spy ---------- */
  var navLinks = document.querySelectorAll('.nav-link');
  var sectionEls = document.querySelectorAll('section[id]');

  function activate(id) {{
    navLinks.forEach(function(l) {{
      var isActive = l.dataset.section === id;
      l.classList.toggle('bg-slate-800', isActive);
      l.classList.toggle('text-white', isActive);
      l.classList.toggle('text-slate-400', !isActive);
    }});
  }}

  var scrollObserver = new IntersectionObserver(
    function(entries) {{
      entries.forEach(function(e) {{
        if (e.isIntersecting) activate(e.target.id);
      }});
    }},
    {{ rootMargin: '-10% 0px -80% 0px', threshold: 0 }}
  );

  sectionEls.forEach(function(s) {{ scrollObserver.observe(s); }});
  if (sectionEls.length) activate(sectionEls[0].id);

  /* ---------- read-state tracking ---------- */
  var READ_KEY = 'ni_read';

  var ICON_UNREAD = '<svg title="Seen, not opened" class="h-3 w-3 text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="8"/></svg>';
  var ICON_READ   = '<svg title="Opened" class="h-3 w-3 text-blue-400" viewBox="0 0 20 20" fill="currentColor"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/></svg>';

  function getRead() {{
    try {{ return new Set(JSON.parse(localStorage.getItem(READ_KEY) || '[]')); }}
    catch(e) {{ return new Set(); }}
  }}

  function saveRead(s) {{
    localStorage.setItem(READ_KEY, JSON.stringify([...s]));
  }}

  var readUrls = getRead();

  document.querySelectorAll('[data-url]').forEach(function(row) {{
    var stateEl = row.querySelector('.article-state');
    if (!stateEl) return;
    stateEl.innerHTML = readUrls.has(row.dataset.url) ? ICON_READ : ICON_UNREAD;
  }});

  document.querySelectorAll('.article-link').forEach(function(link) {{
    link.addEventListener('click', function() {{
      var row = this.closest('[data-url]');
      if (!row) return;
      var url = row.dataset.url;
      readUrls.add(url);
      saveRead(readUrls);
      var stateEl = row.querySelector('.article-state');
      if (stateEl) stateEl.innerHTML = ICON_READ;
    }});
  }});
</script>
</body>
</html>"""


_NAV_ITEM = """<a href="#{slug}" data-section="{slug}"
   class="nav-link flex items-center gap-2.5 px-3 py-2 rounded-md text-sm
          text-slate-400 hover:text-white hover:bg-slate-800 transition-colors duration-150">
  <img src="https://www.google.com/s2/favicons?domain={domain}&sz=32"
       alt="" class="h-4 w-4 rounded-sm shrink-0" onerror="this.style.display='none'">
  <span class="truncate">{company}</span>
</a>"""


_SECTION = """<section id="{slug}" class="scroll-mt-10">
  <div class="flex items-center gap-2.5 mb-5 pb-3 border-b border-slate-150">
    <img src="https://www.google.com/s2/favicons?domain={domain}&sz=64"
         alt="" class="h-5 w-5 rounded shrink-0" onerror="this.style.display='none'">
    <h2 class="text-xs font-semibold text-slate-400 uppercase tracking-widest">{company}</h2>
  </div>
  {summary_block}
  <div>{articles}</div>
</section>"""


_SUMMARY = (
    '<div class="bg-slate-50 border border-slate-200 rounded-lg p-4 mb-5'
    ' text-xs text-slate-500 leading-relaxed">{text}</div>'
)


_ARTICLE_ROW = """<div class="group py-3.5 border-b border-slate-100 last:border-0{row_extra_class}" data-url="{url}">
  <div class="flex items-start justify-between gap-6">
    <h3 class="text-sm font-medium text-slate-800 leading-snug">
      <a href="{url}" target="_blank" rel="noopener noreferrer"
         class="article-link hover:text-blue-600 transition-colors">{title}</a>
    </h3>
    <span class="text-xs text-slate-400 whitespace-nowrap shrink-0 pt-0.5">{date}</span>
  </div>
  <div class="flex items-center gap-1.5 mt-1.5">
    <span class="article-state inline-flex items-center"></span>
    <span class="text-xs bg-slate-100 text-slate-500 px-2 py-0.5 rounded">{source}</span>
    {new_badge}
  </div>
  {description_block}
</div>"""


_NEW_BADGE = (
    '<span class="text-xs bg-green-50 text-green-600 px-2 py-0.5 rounded font-medium">New</span>'
)

_DESCRIPTION = '<p class="text-xs text-slate-400 leading-relaxed mt-1.5">{text}</p>'
_NO_ARTICLES = '<p class="text-slate-400 text-xs italic py-3">No articles found.</p>'


def export_html(
    articles_by_company: dict[str, list[Article]],
    summaries: Optional[dict[str, str]] = None,
    previous_urls: Optional[set[str]] = None,
    path: str = "index.html",
) -> None:
    if summaries is None:
        summaries = {}
    if previous_urls is None:
        previous_urls = set()

    nav_html = ""
    sections_html = ""

    for company, articles in articles_by_company.items():
        slug = _slugify(company)
        domain = COMPANY_DOMAINS.get(company, "")

        nav_html += _NAV_ITEM.format(
            slug=slug,
            domain=domain,
            company=html.escape(company),
        )

        if not articles:
            articles_html = _NO_ARTICLES
        else:
            articles_html = ""
            for article in sorted(articles, key=lambda a: a.date, reverse=True):
                desc_block = ""
                if article.description:
                    truncated = article.description[:200]
                    if len(article.description) > 200:
                        truncated += "…"
                    desc_block = _DESCRIPTION.format(text=html.escape(truncated))

                is_new = article.url not in previous_urls
                articles_html += _ARTICLE_ROW.format(
                    url=html.escape(article.url),
                    title=html.escape(article.title),
                    date=html.escape(article.date),
                    source=html.escape(article.source),
                    description_block=desc_block,
                    new_badge=_NEW_BADGE if is_new else "",
                    row_extra_class=" border-l-2 border-l-green-400 pl-3" if is_new else "",
                )

        summary_text = summaries.get(company, "")
        summary_block = (
            _SUMMARY.format(text=html.escape(summary_text)) if summary_text else ""
        )

        sections_html += _SECTION.format(
            slug=slug,
            domain=domain,
            company=html.escape(company),
            summary_block=summary_block,
            articles=articles_html,
        )

    updated = datetime.now().strftime("%b %d, %Y at %I:%M %p")
    page = _PAGE.format(updated=updated, nav_items=nav_html, sections=sections_html)
    Path(path).write_text(page, encoding="utf-8")
    print(f"Saved to {path}")
