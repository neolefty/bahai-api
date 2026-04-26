# Sources

Per-source notes for the corpus we ingest. Each section is what a
scraper or parser author needs to know that isn't obvious from the
site itself. Expect this to grow source-by-source as we add works.

The near-term use case is **casual daily reading and semantic search**,
not scholarly cross-language alignment. When in doubt, prefer
"available right now and good enough" over "comprehensive but
blocked on finding a better source."

## bahai.org Reference Library

Landing page: <https://www.bahai.org/library/>

### What's available

Each authoritative work has a "single HTML download" page that bundles
the entire work onto one URL. Fetching the bundle once is the right
ingestion strategy — per-passage fetches are unnecessary.

| Work | Languages on bahai.org |
|------|------------------------|
| Hidden Words | en, fa |

The site has a `/fa/` (Persian) parallel tree but **no `/ar/`**:
`https://www.bahai.org/ar/library/...` 301-redirects back to English.
Arabic-original text for works whose original language is Arabic
(e.g. the Arabic Hidden Words) is therefore **not** available from
this source and would need a different upstream.

### Bundle URL pattern

```
https://www.bahai.org/library/<work-path>/<slug>.xhtml?<hash>
https://www.bahai.org/fa/library/<work-path>/<slug>.xhtml?<hash>
```

The trailing `?<hash>` query string is a cache-buster and changes
when bahai.org republishes. The hash is not stable across time, so
treat the bundle URL as resolved-at-scrape-time, not as a permanent
identifier.

### Passage IDs and canonical permalinks

Each passage carries the canonical numeric ID inline as an empty
anchor:

```html
<a class="sf" id="986635113"></a>
```

The literal short-link form `/r/986635113` is **not** present in the
bundle — synthesize it from the ID:

```
https://www.bahai.org/r/<id>
```

`/r/<id>` 302-redirects to a section page with the ID as a fragment
(e.g. `/library/.../hidden-words/2#986635113`). Cheap to follow at
runtime if a user pastes a short link, but unnecessary for ingestion.

**IDs are per-translation, not per-work.** The English passage and
its Persian counterpart have *different* `/r/` IDs. Do not try to
map across languages by ID.

### Parser fragility

Class names in the bundle are obfuscated and minified
(`db`, `if`, `zd`, `dd`, `kf`, `sf`, `td ff gf`, ...). They look like
build output and probably change when the bundle is republished —
that's also why the URL has a `?<hash>` query string.

Implications for the parser:

- Don't pin selectors to class names alone. Use structural position
  (passage container under section heading, anchor preceding
  opening-phrase span) with class names as a secondary hint.
- Add a fixture-replay test that fails loudly if the count or shape
  of extracted passages drifts. A silent miscount would be worse
  than a noisy break.

### Translation linking

Since `/r/` IDs don't cross languages and there are no `hreflang`
links between bundles, translations are aligned by **section +
ordinal**: the Nth passage of the Arabic-section in the English
bundle is the same work as the Nth passage of the Arabic-section in
the Persian bundle.

This is enough for daily-reading and "show me this passage in another
language" features. It is not enough for verse-level scholarly
alignment of long works, but Hidden Words is short and stanzaic, so
ordinal alignment is unambiguous here. Re-evaluate per work as we
expand the corpus.

### robots.txt

```
User-agent: *
Disallow:
```

No `Crawl-delay`, no `Sitemap`. Be polite anyway with a small
self-imposed delay and a `User-Agent` that identifies the project.
