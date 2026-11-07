# Use the same Python 3.13 runtime as the local environment and CodeBuild.
FROM python:3.13-slim

# Copy the pinned uv executable into the image.
COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv
# Disable bytecode files, stream logs immediately, and use the image's Python and project environment.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

# Set up an app directory for the code and install locked runtime dependencies.
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-cache
# Copy the application after dependencies so code changes can reuse their cached layer.
COPY main.py .

# Run the Flask application with the Gunicorn WSGI server on container port 8080.
ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]
