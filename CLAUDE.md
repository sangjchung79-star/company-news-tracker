# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Company news tracker — fetch, monitor, aggregate, and analyze news articles about target companies. May include alerting (email/Slack), a feed/dashboard, and a data pipeline for research.

## Stack

- **Language**: Python 3.11+
- **Likely frameworks**: FastAPI (API/server), or standalone scripts for scraping/pipeline tasks
- **Package manager**: pip + `requirements.txt`, or migrate to `uv` if adopted

## Type Annotations

All functions and methods must have type annotations. Use `mypy` or `pyright` for static type checking.

```python
# Good
def fetch_articles(company: str, limit: int = 10) -> list[Article]:
    ...

# Bad — no annotations
def fetch_articles(company, limit=10):
    ...
```

Run type checking with:
```
mypy .
# or
pyright
```

## Testing

Use `pytest`. Run tests with:
```
pytest
pytest -k "test_name"   # single test
pytest -x               # stop on first failure
```

## Code Style

- Follow PEP 8; use `ruff` for linting and formatting (`ruff check .` / `ruff format .`)
- Prefer explicit over implicit — avoid magic, keep functions focused
- Use dataclasses or Pydantic models for structured data (not raw dicts)

## Project Structure (intended)

```
company-news-tracker/
  src/               # application source
  tests/             # pytest tests
  scripts/           # one-off or scheduled scripts
  pyproject.toml     # project metadata and tool config
```

## Subdirectory CLAUDE.md files

Add `src/CLAUDE.md` or `tests/CLAUDE.md` for module-specific instructions as the project grows — they're loaded automatically when Claude works in those directories.

## Learning Mode

The project owner is an experienced finance and accounting professional but a beginner software engineer.

When proposing changes:

1. Explain every command before running it.
2. Explain every file before creating it.
3. Explain architecture decisions before implementation.
4. Prefer the simplest working solution.
5. Optimize for teaching and understanding over sophistication.
6. Do not introduce new frameworks unless there is a clear benefit.
7. Wait for approval before making major architectural changes.
