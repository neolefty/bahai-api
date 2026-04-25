# bahai-api

Open-source APIs for accessing, searching, and sharing the Baha'i writings.
Designed for AI assistants, personal agents, and developers.

> **Status:** early scaffolding. The discovery root (`GET /api/v1`) is
> live and publishes a typed schema; everything else below describes the
> intended API surface and is not implemented yet. Work is tracked in
> [GitHub Issues](../../issues).

## Overview

Three capabilities make up the mission:

- **Text search** across the Baha'i writings (BM25, semantic, and hybrid
  retrieval)
- **Daily quotes** and subscription-based delivery
- **Compilations** — user-curated collections of passages to study and share

The primary audience is AI assistants and developers building Baha'i study
tools, so the API is shaped around machine readability, predictable
structure, and context-window efficiency.

## API Design

### Discovery

`GET /api/v1` — API root. Lists endpoints, versions, capabilities.

### Texts & Search

Collections align with the
[Baha'i Reference Library](https://www.bahai.org/library/authoritative-texts/)
hierarchy (Bahaullah, the Bab, Abdul-Baha, Shoghi Effendi, Universal House of
Justice, Compilations, Prayers).

```
GET  /api/v1/texts                          # list available collections
GET  /api/v1/texts/{collection}             # metadata for a collection
GET  /api/v1/texts/{collection}/search?q=   # search within a collection
GET  /api/v1/search?q=                      # search across all texts
```

Common query parameters (apply to most endpoints):

| Parameter | Notes |
|-----------|-------|
| `lang`    | ISO 639 code (default `en`) |
| `fields`  | Return only named fields, e.g. `id,text,work` |
| `limit`, `offset` | Standard pagination |

Search-specific:

| Parameter | Notes |
|-----------|-------|
| `q`       | Query string |
| `method`  | `bm25`, `semantic`, or `hybrid` |

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

### Passages

The atomic citable unit. Each passage links to one or more canonical sources
(see [Canonical Links](#canonical-links)).

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

### Subscriptions

```
POST /api/v1/subscriptions                  # e.g. "send me a daily quote at 7am"
GET  /api/v1/subscriptions/{id}
```

### Compilations

```
POST /api/v1/compilations                   # create a compilation
GET  /api/v1/compilations/{id}
GET  /api/v1/compilations/{id}/passages
```

## Data Model

### Works and Translations

A **work** is a language-independent identity (e.g. "Hidden Words, Arabic,
#1"). Each work has one or more **passages** — specific translations or the
original text. Most consumers just request a language; the work/translation
link is preserved for when it matters.

- `work` — groups passages that are translations of the same source text
- `lang` — ISO 639 code (`en`, `ar`, `fa`, `es`, ...)
- `translations` — sibling passages in other languages

### Canonical Links

Passages include links to canonical sources. The primary canonical source is
the [Baha'i Reference Library](https://www.bahai.org/library/), which
provides stable short permalinks (e.g. `https://www.bahai.org/r/070299751`).

Canonical links live at the passage (translation) level, not the work level,
since each translation has its own permalink. The model supports multiple
parallel sets of canonical links per passage so additional authoritative
sources can be added over time.

## Data Sourcing

The initial corpus is English, ingested from the
[Baha'i Reference Library](https://www.bahai.org/library/). Translations in
major world languages are a priority but depend on finding structured,
authoritative digital sources (tracked in GitHub Issues). The
work/translation model is in place from day one so translations can be
correlated with existing English passages as sources become available.

## Copyright Notice

The Baha'i writings are copyrighted by the Baha'i World Centre and various
National Spiritual Assemblies. This project provides **access tooling** —
the API code and infrastructure are open source under Apache 2.0, but the
texts themselves are used in accordance with the terms of their respective
copyright holders. This project is not affiliated with or endorsed by the
Baha'i World Centre.

## Authentication and Cost Transparency

Read-only endpoints (texts, search, passages) are intended to be available
without authentication. Endpoints that create resources (subscriptions,
compilations) will require identity.

Search — especially semantic/RAG — has real infrastructure cost. The
intended model is radical transparency: track usage at a granular level and
surface it honestly to consumers, e.g.:

> "In the last month, you have used $0.55 worth of services. Approximately
> 2% of users contribute. If you chose to contribute $25/month, you would
> help maintain full funding of this service."

This implies lightweight usage tracking even for unauthenticated calls.
Exact mechanism is open.

## AI Integration

Primary consumers are AI assistants, so the project ships two integration
paths alongside the REST API:

- **`openapi.yaml`** — generated from FastAPI; usable by any framework that
  consumes OpenAPI.
- **MCP server** — a first-class [Model Context Protocol](https://modelcontextprotocol.io/)
  surface for Claude and other MCP clients, not a thin wrapper.

Additional agent-discoverability conventions (well-known URLs, registries,
emerging protocols) are tracked as they stabilize.

Responses are designed for context-window efficiency: `fields` trims
payloads, `highlights` lets agents cite without including full passage
text, batch passage retrieval replaces N sequential calls, and pagination
is bounded by default.

## Development

The full system can be exercised end-to-end in a local container
environment on demand. A fast tier of tests runs without containers so
tight TDD loops stay snappy. Tooling is chosen to make AI coding agents
productive with high autonomy.

### Stack

| Layer | Tool | Why |
|-------|------|-----|
| Package / env | [`uv`](https://docs.astral.sh/uv/) | Replaces pip + poetry + virtualenv + pyenv |
| Lint + format | [`ruff`](https://docs.astral.sh/ruff/) | |
| Type checker | [`pyright`](https://microsoft.github.io/pyright/) | |
| Test runner | [`pytest`](https://pytest.org/) | |
| Task runner | [`just`](https://just.systems/) | Recipes shared across bahai-api and Immerse Library |
| API framework | [`FastAPI`](https://fastapi.tiangolo.com/) + [`pydantic`](https://docs.pydantic.dev/) | Auto-generates OpenAPI from type hints |
| Scraper | [`httpx`](https://www.python-httpx.org/) + [`vcrpy`](https://vcrpy.readthedocs.io/) | Recorded cassettes keep scraper tests offline |
| Datastore | SQLite + FTS5 | Embedded; no extra container in dev |

Configuration lives in `pyproject.toml` alongside a `justfile` and
`compose.yml`. Pre-commit hooks are deliberately avoided — `just check`
runs lint + format + typecheck explicitly. Migrations are hand-written
numbered SQL files rather than Alembic until schema complexity warrants
otherwise.

### Local Stack

A `compose.yml` brings up the API against a committed fixture database.
The [Immerse Library](https://immerselibrary.org) repo references the same
compose setup (or a tagged image) for its own e2e tests, so there is a
single source of truth for how the API is run locally.

### Test Tiers

| Tier | Scope | Runtime | Command |
|------|-------|---------|---------|
| unit | pure logic, no I/O | ms | `just test` |
| integration | API process + SQLite fixture DB, no containers | seconds | `just test` |
| e2e | full compose stack + Playwright (once the PWA lands) | tens of seconds | `just e2e` |

`just check` runs lint + format + typecheck.

### Test Data

Fixtures are **real scraped passages**, not mock data — a small, stable
slice of the corpus committed to the repo so tests reflect real content
shape without hitting bahai.org. The scraper itself is tested against
recorded HTTP cassettes.

The goal is a fast, deterministic, offline TDD loop that AI coding agents
can drive on their own. LLM-output evals are planned but out of scope for
the initial test story.

## Contributing

Task tracking uses [GitHub Issues](../../issues). Look for issues labeled
`good first issue` or `help wanted`. Agent workflow conventions live in
[CLAUDE.md](CLAUDE.md).

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
