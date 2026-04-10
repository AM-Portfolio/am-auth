# AM API Gateway
ARG BASE_REGISTRY=""
FROM ${BASE_REGISTRY}am-python-base:latest

WORKDIR /app

# Install only additional dependencies not in base image
COPY am-api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and shared library
COPY am-api-gateway/ .
COPY shared/ ./shared/

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
