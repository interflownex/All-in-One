FROM python:3.12-slim
WORKDIR /app
COPY modules/shared /app/shared
COPY modules/jobs/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY modules/jobs/main.py /app/main.py
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
