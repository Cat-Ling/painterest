@lint:
    uv run ruff check --fix --unsafe-fixes
    uv run ruff format

@typing:
    uv run basedpyright

@css:
    uvx --from pytailwindcss tailwindcss -o static/css/tailwind.css

dev $DEV="1":
    uv run uvicorn src.main:app --reload --reload-include "src/**/*.py" \
        --reload-include "templates/**/*.html" --reload-include "static/**/*.css" --port 8889
