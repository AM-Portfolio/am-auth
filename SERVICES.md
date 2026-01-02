# AM Services & API Reference

This document serves as the source of truth for the AM Ecosystem services, ports, and API structures.

## 🛠 Service Registry

| Service | Port | Public URL | Description |
|---------|------|------------|-------------|
| **Traefik Gateway** | `8000` | `https://am.munish.org` | Main entry point (Route via Host header) |
| **Auth Tokens** | `8001` | `https://am.munish.org/auth/token/v1` | Authentication, login, token validation |
| **User Management** | `8002` | `https://am.munish.org/users/account/v1` | User registration, profiles, status |
| **Diagnostic UI** | `9001` | `http://localhost:9001` | System health and diagnostic tools |
| **Investment UI** | `9000` | `http://localhost:9000` | Main investment dashboard |

## 🔌 API Endpoints

### Auth Service (`/auth/token/v1`)
**Base URL**: `https://am.munish.org/auth/token/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/tokens` | Login (username/password) -> Returns JWT |
| `POST` | `/validate` | Validate JWT token (body) |
| `GET` | `/validate/me` | Validate JWT token (query param) |
| `POST` | `/refresh` | Refresh access token |

### User Service (`/users/account/v1`)
**Base URL**: `https://am.munish.org/users/account/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/register` | Register new user |
| `GET` | `/{id}/status` | Get user status |
| `PATCH` | `/{id}/status` | Update user status (active/inactive) |
| `POST` | `/request-reset` | Request password reset |
| `POST` | `/validate-reset-token` | Validate reset token |
| `POST` | `/confirm-reset` | Confirm password reset |

### Infrastructure Health (`/users/account/v1/infra`)
**Base URL**: `https://am.munish.org/users/account/v1`

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/infra/health` | Check connectivity to DB, Redis, Kafka, etc. |

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
