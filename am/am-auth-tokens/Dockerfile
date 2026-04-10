# AM Auth Tokens
ARG BASE_REGISTRY=""
FROM ${BASE_REGISTRY}am-python-base:latest

ENV PYTHONPATH=/app

WORKDIR /app

# Install dependencies
COPY am-auth-tokens/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application and shared library
COPY am-auth-tokens/ .
COPY shared/ ./shared/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

EXPOSE 8001

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8001/health')" || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]