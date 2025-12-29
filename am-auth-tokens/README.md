# Auth Tokens Microservice

A FastAPI-based JWT authentication service that handles token creation and validation for the AM (Application Management) portfolio.

## Features

- **JWT Token Creation**: Generate secure JWT tokens for authenticated users
- **Token Validation**: Validate JWT tokens and extract user information
- **User Integration**: Integrates with am-user-management service for credential validation
- **RESTful API**: Clean REST endpoints for token operations
- **Docker Support**: Containerized deployment with Docker Compose
- **Health Monitoring**: Built-in health check endpoints

## Project Structure

```
am-auth-tokens/
│
├── app/
│   ├── core/
│   │   └── security.py            # JWT encode/decode functionality
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── token.py       # POST /tokens - Token creation
│   │       │   └── validate.py    # POST /validate - Token validation
│   │       ├── api.py             # API router aggregation
│   │       └── deps.py            # Dependency injection
│   │
│   └── services/
│       └── user_validation.py     # User management service integration
│
├── shared_infra/
│   └── config/
│       └── settings.py            # Configuration management
│
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Container configuration
├── docker-compose.yml             # Real services orchestration
├── setup-env.sh                   # Environment setup script
├── .env.example                   # Environment variables template
├── .env.local                     # Local development config
├── .env.docker                    # Docker environment config
├── .env.production                # Production template
├── ENVIRONMENT_GUIDE.md           # Environment setup guide
└── README.md                      # This file
```

## API Endpoints

### Authentication
- `POST /api/v1/tokens` - Create access token with username/password
- `POST /api/v1/tokens/oauth` - OAuth2 compatible token endpoint

### Validation
- `POST /api/v1/validate` - Validate JWT token and return user info
- `POST /api/v1/validate/bearer` - Alternative token validation endpoint
- `GET /api/v1/validate/me` - Validate token via query parameter

### Health & Info
- `GET /` - Service information
- `GET /health` - Health check endpoint
- `GET /info` - Detailed service information

## Quick Start

### Prerequisites
- Python 3.11+
- Docker and Docker Compose (for containerized deployment)

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd am-auth-tokens
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Run the service**:
```bash
python main.py
```

The service will start on `http://localhost:8000`

### Docker Deployment

1. **Start all services**:
```bash
docker-compose up -d
```

2. **View logs**:
```bash
docker-compose logs -f auth-tokens
```

3. **Stop services**:
```bash
docker-compose down
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Deployment environment | `development` |
| `DEBUG` | Enable debug mode | `true` |
| `JWT_SECRET` | Secret key for JWT signing | `your-super-secret-jwt-key-change-this-in-production` |
| `JWT_ALGORITHM` | JWT signing algorithm | `HS256` |
| `JWT_EXPIRE_MINUTES` | Token expiration time in minutes | `1440` (24 hours) |
| `USER_SERVICE_URL` | User management service URL | `http://localhost:8001` |
| `USER_SERVICE_TIMEOUT` | Timeout for user service calls | `30` |

### Security Configuration

- Change the `JWT_SECRET` in production environments
- Configure CORS origins appropriately for your deployment
- Use HTTPS in production
- Consider shorter token expiration times for sensitive applications

## API Usage Examples

### Create Token
```bash
curl -X POST "http://localhost:8000/api/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "testpass"
  }'
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 86400,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "testuser",
  "email": "test@example.com"
}
```

### Validate Token
```bash
curl -X POST "http://localhost:8000/api/v1/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
  }'
```

Response:
```json
{
  "valid": true,
  "user_id": "123e4567-e89b-12d3-a456-426614174000",
  "username": "testuser",
  "email": "test@example.com",
  "scopes": ["read", "write"],
  "expires_at": "2025-10-02T12:00:00",
  "message": "Token is valid"
}
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

### API Documentation
When running in debug mode, visit:
- Swagger UI: `http://localhost:8000/api/v1/docs`
- ReDoc: `http://localhost:8000/api/v1/redoc`

### Code Structure

- **`app/core/security.py`**: JWT token creation, validation, and utility functions
- **`app/services/user_validation.py`**: Integration with user management service
- **`app/api/v1/endpoints/`**: API endpoint implementations
- **`app/api/v1/deps.py`**: FastAPI dependency injection functions
- **`shared_infra/config/settings.py`**: Centralized configuration management

## Integration

### User Management Service

This service expects the user management service to provide these endpoints:

- `POST /internal/validate-credentials`: Validate username/password
- `GET /internal/users/{user_id}`: Retrieve user information

Expected response format for credential validation:
```json
{
  "user_id": "string",
  "username": "string", 
  "email": "string",
  "scopes": ["array", "of", "strings"]
}
```

### Service Dependencies

- **am-user-management**: For user credential validation
- **Database**: None required (stateless service)
- **External Services**: User management service only

## Monitoring

### Health Checks
- Container health check: `GET /health`
- Service status: `GET /`
- Detailed info: `GET /info`

### Logging
- Structured logging with uvicorn
- Configurable log levels based on environment
- Request/response logging in debug mode

## Security Considerations

1. **JWT Secret**: Use a strong, randomly generated secret in production
2. **Token Expiration**: Configure appropriate expiration times
3. **HTTPS**: Always use HTTPS in production environments
4. **CORS**: Configure CORS origins restrictively for production
5. **Input Validation**: All inputs are validated using Pydantic models
6. **Error Handling**: Sensitive information is not exposed in error messages

## Production Deployment

1. **Environment Variables**: Set production values for all configuration
2. **Secrets Management**: Use a secrets management system for JWT_SECRET
3. **Load Balancing**: Deploy multiple instances behind a load balancer
4. **Monitoring**: Implement application performance monitoring
5. **Logging**: Configure centralized logging
6. **Backup**: No data backup required (stateless service)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

[Your License Here]