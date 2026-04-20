# bahai-api

Open-source APIs for accessing, searching, and sharing the Baha'i writings.
Designed for AI assistants, personal agents, and developers.

## Overview

This project provides RESTful APIs for:
- **Text search** across the Baha'i writings (BM25, semantic/vector, and hybrid retrieval)
- **Daily quotes** and subscription-based delivery
- **Compilations** — user-curated collections of passages to study and share

Primary consumers are AI assistants (coding agents, personal agents, chatbots)
and developers building Baha'i study tools. The API prioritizes machine
readability, predictable structure, and context-window efficiency.

## API Design

### Discovery

```
GET  /api/v1                                # API root — lists endpoints, versions, capabilities
```

### Texts & Search — *active*

The foundational layer. Collections align with the
[Baha'i Reference Library](https://www.bahai.org/library/authoritative-texts/)
hierarchy (Bahaullah, the Bab, Abdul-Baha, Shoghi Effendi, Universal House of
Justice, Compilations, Prayers).

```
GET  /api/v1/texts                          # list available collections
GET  /api/v1/texts/{collection}             # metadata for a collection
GET  /api/v1/texts/{collection}/search?q=   # search within a collection
GET  /api/v1/search?q=                      # search across all texts
```

Common query parameters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `lang`    | `en`    | ISO 639 language code (default: `en`) |
| `limit`   | `10`    | Max results to return |
| `offset`  | `0`     | Pagination offset |
| `fields`  | `id,text,work` | Return only specified fields |

Search-specific parameters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `q`       | `pure heart` | Search query |
| `method`  | `bm25`  | Retrieval method (`bm25`, `semantic`, `hybrid`) |

Example search response:

```json
{
  "query": "pure heart",
  "method": "bm25",
  "total": 42,
  "limit": 10,
  "offset": 0,
  "results": [
    {
      "score": 0.87,
      "highlights": ["...Possess a pure, kindly and radiant heart..."],
      "passage": {
        "id": "hidden-words-arabic-1-en",
        "lang": "en",
        "work": "hidden-words-arabic-1",
        "text": "O Son of Spirit! My first counsel is this: Possess a pure..."
      }
    }
  ]
}
```

### Passages — *active*

The atomic citable unit. Each passage links back to one or more canonical
sources (see [Canonical Links](#canonical-links)).

```
GET  /api/v1/passages/{id}                  # a specific passage
GET  /api/v1/passages?ids=abc,def,ghi       # batch retrieval
GET  /api/v1/passages/random                # random quote
GET  /api/v1/passages/daily                 # deterministic daily quote
```

Example response:

```json
{
  "id": "hidden-words-arabic-1-en",
  "lang": "en",
  "work": "hidden-words-arabic-1",
  "text": "O Son of Spirit! My first counsel is this: Possess a pure...",
  "canonical_urls": ["https://www.bahai.org/r/..."],
  "translations": [
    {"lang": "ar", "id": "hidden-words-arabic-1-ar"},
    {"lang": "fa", "id": "hidden-words-arabic-1-fa"}
  ]
}
```

### Subscriptions — *tentative*

```
POST /api/v1/subscriptions                  # e.g. "send me a daily quote at 7am"
GET  /api/v1/subscriptions/{id}
```

### Compilations — *tentative*

```
POST /api/v1/compilations                   # create a compilation
GET  /api/v1/compilations/{id}
GET  /api/v1/compilations/{id}/passages
```

## Data Model

### Works and Translations

A **work** is a language-independent identity (e.g. "Hidden Words, Arabic, #1").
Each work has one or more **passages**, where each passage is a specific
translation or the original text. This keeps the default API experience simple
— most consumers just request a language — while preserving the intrinsic
relationship between an original and its translations.

- `work` — groups passages that are translations of the same source text
- `lang` — ISO 639 language code (`en`, `ar`, `fa`, `es`, ...)
- `translations` — sibling passages in other languages

### Canonical Links

Passages include links to canonical sources. The primary canonical source is the
[Baha'i Reference Library](https://www.bahai.org/library/) at bahai.org, which
provides stable short permalinks (e.g. `https://www.bahai.org/r/070299751`) that
resolve to the full library path.

Canonical links live at the passage (translation) level, not the work level,
since each translation has its own permalink. The model supports multiple
parallel sets of canonical links per passage, so additional authoritative
sources can be added over time.

## Data Sourcing

The initial text corpus is English, ingested from the
[Baha'i Reference Library](https://www.bahai.org/library/) at bahai.org.
Translations in major world languages (French, Spanish, Russian, Chinese, etc.)
are a priority but depend on finding structured, authoritative digital sources;
this is tracked in GitHub Issues.

The work/translation data model is in place from day one so that translations
can be added incrementally and correlated with existing English passages as
sources become available.

## Copyright Notice

The Baha'i writings are copyrighted by the Baha'i World Centre and various
National Spiritual Assemblies. This project provides **access tooling** — the
API code and infrastructure are open source under Apache 2.0, but the texts
themselves are used in accordance with the terms of their respective copyright
holders. This project is not affiliated with or endorsed by the Baha'i World
Centre.

## Authentication and Cost Transparency

*TBD.* Read-only endpoints (texts, search, passages) may be available without
authentication. Endpoints that create resources (subscriptions, compilations)
will require some form of identity.

Search — especially semantic/RAG search — has real infrastructure cost. The
intended model is radical transparency: track usage at a granular level and
surface it honestly to consumers, e.g.:

> "In the last month, you have used $0.55 worth of services. Approximately 2%
> of users contribute. If you chose to contribute $25/month, you would help
> maintain full funding of this service."

This implies lightweight usage tracking even for unauthenticated calls, without
necessarily requiring strong auth on every request. Design details are TBD.

## AI Integration

The primary consumers of this API are AI assistants. The project provides
multiple integration paths:

### OpenAPI Specification

An `openapi.yaml` file describes every endpoint, parameter, and response
schema. Agent frameworks (LangChain, CrewAI, OpenAI function calling, etc.)
can auto-generate tool definitions from this spec.

### MCP Server

A [Model Context Protocol](https://modelcontextprotocol.io/) server exposes the
API as native tools for Claude and other MCP-compatible assistants. This is a
first-class deliverable, not a wrapper.

### Design for Context Windows

- **`fields` parameter** — request only the fields you need to keep responses lean
- **`highlights`** in search results — agents can present relevant snippets without
  including full passage text
- **Batch retrieval** — fetch multiple passages in one call instead of N sequential requests
- **Pagination** — bounded responses by default

## Development

The project is designed so the full system can be exercised end-to-end in a
local container environment at any time — not necessarily on every push, but
on demand. A fast tier of tests runs without containers so that tight
write-test-iterate loops stay snappy. Tooling is chosen to make AI coding
agents productive with high autonomy, and humans comfortable too.

### Stack

| Layer | Tool | Why |
|-------|------|-----|
| Package / env / Python manager | [`uv`](https://docs.astral.sh/uv/) | Fast, deterministic lockfile; replaces pip, poetry, virtualenv, pyenv |
| Lint + format | [`ruff`](https://docs.astral.sh/ruff/) | One tool, millisecond feedback, configured in `pyproject.toml` |
| Type checker | [`pyright`](https://microsoft.github.io/pyright/) | Fast, strict mode, readable errors |
| Test runner | [`pytest`](https://pytest.org/) | Universal |
| Task runner | [`just`](https://just.systems/) | Language-agnostic; recipes shared across bahai-api and Immerse Library |
| API framework | [`FastAPI`](https://fastapi.tiangolo.com/) + [`pydantic`](https://docs.pydantic.dev/) | Auto-generates OpenAPI from type hints |
| Scraper | [`httpx`](https://www.python-httpx.org/) + [`vcrpy`](https://vcrpy.readthedocs.io/) | Async HTTP, recorded cassettes for tests |
| Datastore | SQLite + FTS5 | Embedded, fast, no extra container in dev |

Configuration lives in `pyproject.toml` alongside a `justfile` and
`compose.yml`. Pre-commit hooks are deliberately avoided — `just check` runs
lint + format + typecheck explicitly. Migrations are hand-written numbered
SQL files rather than Alembic until schema complexity warrants otherwise.

### Local Stack

A `compose.yml` brings up the API against a committed fixture database. The
[Immerse Library](https://immerselibrary.org) repo references the same
compose setup (or a tagged image) for its own e2e tests, so there is a
single source of truth for how the API is run locally.

### Test Tiers

| Tier | Scope | Runtime | When |
|------|-------|---------|------|
| **unit** | pure logic, no I/O | ms | every push |
| **integration** | API process + SQLite against fixture DB, no containers | seconds | every push |
| **e2e** | full compose stack + Playwright (once the PWA lands) | tens of seconds | on demand |

- `just test` — unit + integration
- `just e2e` — full compose stack
- `just check` — lint + format + typecheck

### Test Data

Fixtures are **real scraped passages**, not mock data — a small, stable
slice of the corpus committed to the repo so tests reflect real content
shape and edge cases without hitting bahai.org. The scraper itself is tested
against recorded HTTP cassettes.

The goal is a fast, deterministic, offline TDD loop that AI coding agents
can drive on their own. LLM-output evals are planned but out of scope for
the initial test story.

## Contributing

Task tracking uses [GitHub Issues](../../issues). Look for issues labeled
`good first issue` or `help wanted`.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
