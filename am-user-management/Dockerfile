FROM python:3.11-slim

WORKDIR /app

ENV PYTHONPATH=/app

COPY am-user-management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY am-user-management/ .
COPY shared/ ./shared/

EXPOSE 8002

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]