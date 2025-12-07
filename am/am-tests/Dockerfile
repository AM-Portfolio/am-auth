FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy test scripts
COPY . .

# Default command runs the main verification script and then sleeps to allow inspection
CMD ["sh", "-c", "python -u verify_all_services.py; echo 'Tests completed. Sleeping...'; sleep infinity"]
