# AM Services & API Reference

This document serves as the source of truth for the AM Ecosystem services, ports, and API structures.

## 🛠 Service Registry

| Service | Port | Base URL | Description |
|---------|------|----------|-------------|
| **Traefik Gateway** | `8000` | `http://localhost:8000` | Main entry point for all requests |
| **Auth Tokens** | `8001` | `http://localhost:8001/auth/v1` | Authentication, login, token validation |
| **User Management** | `8002` | `http://localhost:8002/users/v1` | User registration, profiles, status |
| **Diagnostic UI** | `9001` | `http://localhost:9001` | System health and diagnostic tools |
| **Investment UI** | `9000` | `http://localhost:9000` | Main investment dashboard |

## 🔌 API Endpoints

### Auth Service (`/auth/v1`)
Direct Port: `8001` | Gateway: `/auth/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tokens` | Login (username/password) -> Returns JWT |
| `POST` | `/validate` | Validate JWT token (body) |
| `GET` | `/validate/me` | Validate JWT token (query param) |
| `POST` | `/refresh` | Refresh access token |

### User Service (`/users/v1`)
Direct Port: `8002` | Gateway: `/users/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register new user |
| `GET` | `/users/{id}` | Get user profile |
| `GET` | `/users/{id}/status` | Get user status |
| `PATCH` | `/users/{id}/status` | Update user status (active/inactive) |
| `POST` | `/request-reset` | Request password reset |
| `POST` | `/validate-reset-token` | Validate reset token |
| `POST` | `/confirm-reset` | Confirm password reset |

### Infrastructure Health (`/users/v1/infra`)
Handled by User Management Service.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Check connectivity to DB, Redis, Kafka, etc. |

## 🐳 Docker Base Standardization

All Flutter Web UIs follow a standardized multi-stage Docker build process:
1. **Build Stage**: Uses `ghcr.io/cirruslabs/flutter:stable` to compile the app.
2. **Runtime Stage**: Uses `nginx:alpine` to serve static files.

### Standard UI Ports
- **Investment UI**: 9000
- **Diagnostic UI**: 9001
- **Market Data UI**: 9002
- **Trade UI**: 9003
- **Bot UI**: 9006
