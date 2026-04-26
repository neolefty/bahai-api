# Agent Workflow

This project is in early scaffolding. The README describes the intended
shape; only a small slice (project layout, tooling, the discovery root)
is implemented so far. Work is sliced into GitHub Issues and picked up
one ticket at a time.

## Tickets

Treat an issue as the unit of work.

- Read the issue and any linked issues before starting. If scope is
  unclear, ask on the issue rather than expanding it silently.
- Reference the issue number in commit messages (`#42`) so GitHub links
  the work back.
- Keep the PR scoped to the ticket. Don't bundle drive-by refactors.

**Follow-on tickets.** When you notice adjacent work — a refactor, a
related bug, a gap in fixtures — weigh it before filing:

- File it if it's concrete, actionable, and someone would pick it up
  (a clear title, a rough acceptance criterion).
- Don't file if it's vague ("improve error handling"), speculative
  ("might want X someday"), or duplicative of an existing issue.
- If in doubt, mention it on the parent issue rather than creating a
  new one. The backlog should stay small enough that a human can scan
  it in one sitting.

## Testing Workflow

TDD is the default loop.

1. Pick the issue.
2. Write or extend a test that describes the desired behavior, using
   real committed fixtures (not mocks).
3. Implement until `just test` passes.
4. Run `just check` before committing.
5. Run `just e2e` only if the change touches the full stack. It's
   on-demand, not every-push.

### Fixtures

- Database and corpus tests run against real scraped passages committed
  to the repo — use those fixtures directly.
- Scraper tests replay recorded vcrpy cassettes, so the suite stays
  offline.
- When a test needs new fixture data or a new network interaction,
  capture it from the real source and commit the passage or cassette
  alongside the test.

## Conventions

- HTTP endpoints return typed Pydantic response models, not bare
  `dict`s. The OpenAPI schema is a primary deliverable — clients,
  agents, and the MCP surface all rely on it — so response shapes
  must be discoverable from the schema alone.
- The wire-protocol version (`API_VERSION` in `src/bahai_api/main.py`)
  bumps only on breaking changes. Additive changes ship under the
  current version.
- Tests take the shared `client` fixture from `tests/conftest.py`
  rather than constructing `TestClient(app)` themselves.

## Cost posture

Per-query LLM cost dominates variable spend; operator time dominates
fixed cost. Don't optimize hosting or infra choices for small dollar
savings — prefer operational simplicity, agent-friendliness, and
architectural fit. The README's cost-transparency feature is about
honest disclosure of per-query LLM cost to users, not about minimizing
the operator's bill.

## Before declaring a task done

- `just check` is clean.
- `just test` is green.
- New behavior has a test that would have failed before the change.
- The issue's acceptance criteria are met, or any deviation is called
  out on the issue.
