FROM python:3.14-slim

WORKDIR /app

# Create data directory for CSV exports
RUN mkdir -p /data/outbank_exports

# Copy project files and install
COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN pip install --no-cache-dir .

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=6668
ENV MCP_TRANSPORT=http

EXPOSE 6668

CMD ["mcp-outbank"]
