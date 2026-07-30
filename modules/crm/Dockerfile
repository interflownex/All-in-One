FROM python:3.12-slim
WORKDIR /app
COPY modules/shared /app/shared
COPY modules/crm/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY modules/crm /app/crm
EXPOSE 8000
CMD ["uvicorn", "crm.main:app", "--host", "0.0.0.0", "--port", "8000"]
