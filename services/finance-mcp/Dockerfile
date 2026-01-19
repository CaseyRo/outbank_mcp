FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY app.py /app/app.py

ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=6668

CMD ["python", "/app/app.py"]
