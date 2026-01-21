FROM python:3.11-slim

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY app.py ./

# Install dependencies using uv
RUN uv sync --frozen

# Default to 0.0.0.0 for HTTP transport (if used)
ENV MCP_HOST=0.0.0.0

CMD ["uv", "run", "python", "app.py"]
