FROM python:3.12-slim

WORKDIR /app
COPY workers/retention_worker/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY config /app/config
COPY modules /app/modules
COPY workers /app/workers

CMD ["python", "-m", "workers.retention_worker.main", "--help"]
