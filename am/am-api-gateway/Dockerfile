ARG BASE_REGISTRY=""
FROM ${BASE_REGISTRY}am-python-base:latest

WORKDIR /app

# Install dependencies
COPY am-api-gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and shared library
COPY am-api-gateway/ .
COPY shared/ ./shared/

# Expose port
EXPOSE 8080

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
