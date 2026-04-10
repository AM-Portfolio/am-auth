ARG BASE_REGISTRY=""
FROM ${BASE_REGISTRY}am-python-base:latest

WORKDIR /app

COPY am-user-management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY am-user-management/ .
COPY shared/ ./shared/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]