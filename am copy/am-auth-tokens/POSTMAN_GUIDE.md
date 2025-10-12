# Auth Tokens API - Postman Collection Guide

## Import Collection

1. Open Postman
2. Click **Import** button
3. Select `postman_collection.json` from this folder
4. Collection will appear in your sidebar

## Configure Environment

The collection uses port **8080** by default.

### Option 1: Use Default (localhost:8080)
- No configuration needed
- Works immediately for local testing

### Option 2: Use Replit URL
1. In Postman, click **Environments**
2. Create new environment or edit existing
3. Add variable:
   - Key: `AUTH_BASE`
   - Value: `https://your-replit-url.replit.dev:8080`

## Test Workflow

### Step 1: Health Check
```
GET /health
```
Verify service is running

### Step 2: Create Token
```
POST /api/v1/tokens
Body: {
  "username": "test@example.com",
  "password": "securePassword123"
}
```
**Note:** Use `username`, NOT `email`!

Response includes `access_token` - automatically saved to environment

### Step 3: Validate Token
```
POST /api/v1/validate
Body: {
  "token": "{{access_token}}"
}
```
Uses the token from Step 2 automatically

## All Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/info` | GET | Detailed service info |
| `/api/v1/tokens` | POST | Create JWT token |
| `/api/v1/tokens/oauth` | POST | OAuth2 token endpoint |
| `/api/v1/validate` | POST | Validate JWT token |
| `/api/v1/docs` | GET | Interactive API docs |

## Common Issues

**422 Error on /tokens:**
- Make sure you're using `"username"` not `"email"` in request body
- Content-Type must be `application/json`

**Connection refused:**
- Service runs on port **8080**, not 5000
- Verify service is running
