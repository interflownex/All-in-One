FROM python:3.12-slim
WORKDIR /app
COPY workers/outbox_dispatcher/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY modules /app/modules
COPY workers /app/workers
CMD ["python", "-m", "workers.outbox_dispatcher.main", "--loop"]
