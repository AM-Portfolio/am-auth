# AM User Management
ARG BASE_REGISTRY=""
FROM ${BASE_REGISTRY}am-python-base:latest

WORKDIR /app

# Install dependencies
COPY am-user-management/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application and shared library
COPY am-user-management/ .
COPY shared/ ./shared/

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]