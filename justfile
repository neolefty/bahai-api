_default:
    @just --list

# Lint, format check, and typecheck.
check:
    uv run ruff check .
    uv run ruff format --check .
    uv run pyright

# Unit + integration tests (no containers).
test:
    uv run pytest

# Full compose stack (on demand). See issue #13.
e2e:
    @echo "e2e: compose.yml not yet wired up (tracked in #13)"
    @exit 1

# Run the API locally with autoreload.
dev:
    uv run uvicorn bahai_api.main:app --reload
