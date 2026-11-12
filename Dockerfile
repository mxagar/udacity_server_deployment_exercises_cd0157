# Post-approval runtime: match Python 3.13 used locally and in CodeBuild.
FROM python:3.13-slim

# Pin uv and install the project's locked runtime dependencies without pip.
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache
COPY main.py .

# Preserve the Gunicorn app and port contract.
ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]
