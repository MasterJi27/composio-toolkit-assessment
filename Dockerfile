FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy project files
COPY pyproject.toml .
COPY .env.example .env
COPY backend/ backend/
COPY agents/ agents/
COPY research/ research/
COPY verification/ verification/
COPY cli/ cli/
COPY reports/ reports/

# Install dependencies
RUN uv sync --system

# Default command
CMD ["composio-research", "--help"]
