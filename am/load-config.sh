#!/bin/bash
# Load service configuration
set -a
source ./config/services.env
source ./.env.docker
set +a

# The environment variables are now available to docker-compose
# This script is optional - docker-compose will use .env.docker automatically
# But this helps when you need to source config/services.env explicitly

echo "Loaded environment variables:"
echo "SERVICE_PROTOCOL: $SERVICE_PROTOCOL"
echo "AUTH_SERVICE_URL: $AUTH_SERVICE_URL"
echo "USER_MANAGEMENT_URL: $USER_MANAGEMENT_URL"
echo "PYTHON_SERVICE_URL: $PYTHON_SERVICE_URL"
echo "JAVA_SERVICE_URL: $JAVA_SERVICE_URL"
