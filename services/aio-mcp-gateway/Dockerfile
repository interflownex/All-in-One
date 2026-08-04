FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

RUN groupadd --system app && useradd --system --gid app --create-home app
WORKDIR /app

COPY pyproject.toml ./
RUN pip install --no-cache-dir .

COPY main.py ./main.py

USER app
EXPOSE 8080

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
