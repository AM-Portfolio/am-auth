# Environment Configuration Guide

## 📁 Environment Files

This project includes three pre-configured environment files:

### `.env.local` - Local Development
```bash
# For development on your local machine
USER_SERVICE_URL=http://localhost:8000
DEBUG=true
JWT_SECRET=dev-jwt-secret-key-change-in-production-12345
```

### `.env.docker` - Docker Compose
```bash  
# For running with Docker Compose
USER_SERVICE_URL=http://am-user-management:8000
DEBUG=false
JWT_SECRET=docker-jwt-super-secret-key-production-ready-2025
```

### `.env.production` - Production
```bash
# For production deployment (requires customization)
USER_SERVICE_URL=https://your-user-management-service.com
DEBUG=false
JWT_SECRET=CHANGE-THIS-TO-SUPER-SECURE-SECRET-KEY-IN-PRODUCTION
```

## 🚀 Quick Setup

### Option 1: Use Setup Script (Recommended)
```bash
# Local development
./setup-env.sh local

# Docker development  
./setup-env.sh docker

# Production setup
./setup-env.sh production
```

### Option 2: Manual Setup
```bash
# Copy the appropriate environment file
cp .env.local .env      # For local development
cp .env.docker .env     # For Docker development
cp .env.production .env # For production
```

## 🔧 Environment Variables

| Variable | Description | Local | Docker | Production |
|----------|-------------|--------|--------|------------|
| `ENVIRONMENT` | Deployment environment | `development` | `docker` | `production` |
| `DEBUG` | Enable debug mode | `true` | `false` | `false` |
| `JWT_SECRET` | Secret key for JWT signing | Dev key | Docker key | **CHANGE THIS** |
| `JWT_EXPIRE_MINUTES` | Token expiration time | `1440` | `1440` | `60` |
| `USER_SERVICE_URL` | User management service URL | `localhost:8000` | `am-user-management:8000` | **YOUR URL** |
| `PORT` | Server port | `8080` | `8080` | `8080` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `*` | `*` | **YOUR DOMAINS** |

## 📋 Development Workflows

### Local Development
```bash
# 1. Setup environment
./setup-env.sh local

# 2. Start user management service (separate terminal)
cd /path/to/am-user-management
python3 main.py  # Should run on port 8000

# 3. Start auth tokens service
python3 main.py  # Will run on port 8080

# 4. Test
curl http://localhost:8080/health
```

### Docker Development
```bash
# 1. Setup environment
./setup-env.sh docker

# 2. Start all services
docker-compose up -d

# 3. Test
curl http://localhost:8080/health

# 4. View logs
docker-compose logs -f auth-tokens
```

### Production Deployment
```bash
# 1. Setup environment
./setup-env.sh production

# 2. Edit .env file with your production values
nano .env

# 3. Deploy using your preferred method
```

## 🚨 Security Notes

### Local Development
- Uses weak JWT secret (fine for development)
- Debug mode enabled
- CORS allows all origins

### Docker Development  
- Uses stronger JWT secret
- Debug mode disabled
- Still allows all origins (development only)

### Production
- **MUST change JWT_SECRET** to a strong, random key
- **MUST set USER_SERVICE_URL** to your production service
- **MUST restrict ALLOWED_ORIGINS** to your domains
- Debug mode disabled
- Shorter token expiration time

## 🔐 Production Security Checklist

Before deploying to production:

- [ ] Change `JWT_SECRET` to a cryptographically secure random string
- [ ] Set `USER_SERVICE_URL` to your production user management service
- [ ] Restrict `ALLOWED_ORIGINS` to your actual domains
- [ ] Use HTTPS URLs only
- [ ] Review `JWT_EXPIRE_MINUTES` (60 minutes for production)
- [ ] Ensure `DEBUG=false`
- [ ] Set up proper logging and monitoring

## 🛠 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8080
lsof -ti :8080 | xargs kill -9

# Or use the setup script (kills automatically)
./setup-env.sh local
```

### Service Connection Issues
```bash
# Check if services are running
curl http://localhost:8000/health  # User management
curl http://localhost:8080/health  # Auth tokens

# Check environment configuration
cat .env | grep USER_SERVICE_URL
```

### JWT Token Issues
```bash
# Verify JWT secret is set
cat .env | grep JWT_SECRET

# Check token expiration
cat .env | grep JWT_EXPIRE_MINUTES
```

## 🔄 Switching Environments

You can easily switch between environments:

```bash
# Switch to local development
./setup-env.sh local
python3 main.py

# Switch to Docker
./setup-env.sh docker
docker-compose up -d

# Switch back to local
./setup-env.sh local
```

The setup script automatically:
- Copies the correct environment file
- Kills existing processes (for local)
- Shows next steps for each environment