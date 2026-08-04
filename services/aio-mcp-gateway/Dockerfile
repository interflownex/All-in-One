FROM python:3.12.13-alpine3.23 AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /build

COPY pyproject.toml ./
RUN python -m venv /opt/venv \
    && /opt/venv/bin/python -m pip install --upgrade pip==26.1.2 \
    && /opt/venv/bin/pip install --no-cache-dir .

FROM python:3.12.13-alpine3.23 AS runtime

ENV PATH="/opt/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

RUN addgroup -S app \
    && adduser -S -G app -h /home/app app

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY main.py ./main.py
COPY production_invariants.py ./production_invariants.py
COPY request_limits.py ./request_limits.py
COPY security.py ./security.py

USER app
EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen(f'http://127.0.0.1:{os.getenv(\"PORT\", \"8080\")}/health', timeout=3)"

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
