FROM python:3.12-slim
WORKDIR /app
COPY modules/shared /app/shared
COPY modules/bi/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY modules/bi /app/bi
EXPOSE 8000
CMD ["uvicorn", "bi.main:app", "--host", "0.0.0.0", "--port", "8000"]
