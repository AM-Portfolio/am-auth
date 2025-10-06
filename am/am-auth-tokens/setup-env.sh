#!/bin/bash
# Environment setup script for AM Auth Tokens

set -e

show_help() {
    echo "Usage: $0 [ENVIRONMENT]"
    echo ""
    echo "ENVIRONMENT options:"
    echo "  local       - Setup for local development"
    echo "  docker      - Setup for Docker Compose"
    echo "  production  - Setup for production (requires manual editing)"
    echo ""
    echo "Examples:"
    echo "  $0 local      # Setup for local development"
    echo "  $0 docker     # Setup for Docker development"
    echo ""
}

setup_local() {
    echo "🔧 Setting up LOCAL development environment..."
    
    # Copy local env file
    cp .env.local .env
    echo "✅ Copied .env.local to .env"
    
    # Kill any existing processes on port 8080
    echo "🔴 Killing any processes on port 8080..."
    lsof -ti :8080 | xargs kill -9 2>/dev/null || true
    
    echo "📋 Local environment ready!"
    echo ""
    echo "Next steps:"
    echo "1. Start your am-user-management service on port 8000"
    echo "2. Run: python3 main.py"
    echo "3. Test: curl http://localhost:8080/health"
    echo ""
}

setup_docker() {
    echo "🐳 Setting up DOCKER development environment..."
    
    # Copy docker env file
    cp .env.docker .env
    echo "✅ Copied .env.docker to .env"
    
    echo "📋 Docker environment ready!"
    echo ""
    echo "Next steps:"
    echo "1. Run: docker-compose up -d"
    echo "2. Test: curl http://localhost:8080/health"
    echo "3. View logs: docker-compose logs -f auth-tokens"
    echo ""
}

setup_production() {
    echo "🚀 Setting up PRODUCTION environment..."
    
    if [ -f .env ]; then
        echo "⚠️  .env file already exists. Creating backup..."
        cp .env .env.backup.$(date +%s)
    fi
    
    cp .env.production .env
    echo "✅ Copied .env.production to .env"
    
    echo ""
    echo "🚨 IMPORTANT: Update these values in .env before deploying:"
    echo "- JWT_SECRET (use a strong, random secret)"
    echo "- USER_SERVICE_URL (your production user management URL)"
    echo "- ALLOWED_ORIGINS (restrict to your domains)"
    echo ""
}

# Main script logic
case "${1:-help}" in
    "local")
        setup_local
        ;;
    "docker")
        setup_docker
        ;;
    "production")
        setup_production
        ;;
    "help"|*)
        show_help
        ;;
esac