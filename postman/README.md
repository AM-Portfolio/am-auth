# Postman Collections

This folder contains comprehensive Postman collections for testing the Auth Tokens and User Management microservices.

## Collections

### 1. Auth-Tokens-Service.postman_collection.json
Complete collection for the Auth Tokens service (Port 8080) including:
- **Health & Info** - Service status and information
- **Traditional Authentication** - Username/password login
- **Google OAuth** - Social login with Google
- **Token Validation** - JWT verification
- **Testing Endpoints** - Mock token generation
- **Complete Test Flow** - End-to-end automated testing

### 2. User-Management-Service.postman_collection.json
Complete collection for the User Management service (Port 8000) including:
- **Health & Info** - Service status and features
- **User Authentication** - Registration and login
- **Google OAuth** - Google user creation/linking
- **Service Registration** - OAuth app registration with credentials
- **Internal APIs** - Internal user lookup
- **Complete Test Flows** - Automated multi-step testing

## Import Instructions

### Method 1: Import via File
1. Open Postman
2. Click **Import** button (top left)
3. Select **Upload Files**
4. Choose both JSON files from this folder
5. Click **Import**

### Method 2: Import via Drag & Drop
1. Open Postman
2. Drag and drop the JSON files into the Postman window
3. Collections will be imported automatically

## Environment Setup

Both collections use variables for easy configuration:

### Auth Tokens Service Variables
- `auth_base_url` - Default: `http://localhost:8080`
- `access_token` - Auto-populated by authentication requests
- `google_id_token` - Auto-populated by mock token generation

### User Management Service Variables
- `user_mgmt_base_url` - Default: `http://localhost:8000`
- `user_id` - Auto-populated by user creation/login
- `google_id` - Google user identifier
- `service_id` - Auto-populated by service registration
- `consumer_key` - Service OAuth key (auto-saved)
- `consumer_secret` - Service OAuth secret (auto-saved)

### Creating an Environment (Optional)
1. Click **Environments** (left sidebar)
2. Click **+** to create new environment
3. Name it "Local Development"
4. Add these variables:
   ```
   auth_base_url = http://localhost:8080
   user_mgmt_base_url = http://localhost:8000
   ```
5. Save and select the environment

## Available Endpoints

### Auth Tokens Service (Port 8080)

#### Health & Info
- `GET /` - Service information
- `GET /health` - Health check
- `GET /info` - Detailed service configuration

#### Authentication
- `POST /api/v1/tokens` - Create JWT token (username/password)
- `POST /api/v1/tokens/oauth` - OAuth2-compliant token endpoint
- `POST /api/v1/validate` - Validate JWT token

#### Google OAuth
- `POST /api/v1/auth/google/token` - Authenticate with Google ID token
- `POST /test/mock/google/token` - Generate mock Google token (testing)

### User Management Service (Port 8000)

#### Health & Info
- `GET /` - Service information
- `GET /health` - Health check with database status
- `GET /api/v1/auth/status` - Authentication module status

#### User Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password

#### Google OAuth
- `POST /api/v1/auth/google` - Create/link Google user
- `GET /auth/google/user/{google_id}` - Get user by Google ID

#### Service Registration (OAuth Apps)
- `POST /api/v1/service/register` - Register new service/app
- `POST /api/v1/service/validate-credentials` - Validate service credentials
- `GET /api/v1/service/{service_id}/status` - Get service status
- `PUT /api/v1/service/{service_id}/update` - Update service info

#### Internal APIs
- `GET /internal/v1/users/{user_id}` - Get user by UUID

## Testing Workflows

### 1. Google OAuth Flow (Auth Tokens Service)

**Complete End-to-End Test** - Use the "Complete Google OAuth Flow (Test)" folder:

1. **Step 1: Generate Mock Google Token**
   - Creates a test Google ID token
   - Saves to `{{google_id_token}}`

2. **Step 2: Authenticate with Google**
   - Uses the mock token to authenticate
   - Creates/links user account
   - Returns internal JWT saved to `{{access_token}}`

3. **Step 3: Validate Internal JWT**
   - Validates the JWT token
   - Confirms the complete flow worked

**Manual Testing:**
```bash
# Generate mock token
POST {{auth_base_url}}/test/mock/google/token
Body: { "email": "test@gmail.com", "name": "Test User" }

# Authenticate
POST {{auth_base_url}}/api/v1/auth/google/token
Body: { "id_token": "{{google_id_token}}" }

# Validate
POST {{auth_base_url}}/api/v1/validate
Body: { "token": "{{access_token}}" }
```

### 2. Service Registration Flow (User Management Service)

**Complete Service Registration** - Use the "Complete Service Registration Flow" folder:

1. **Step 1: Register Service**
   - Registers new OAuth application
   - Returns `service_id`, `consumer_key`, `consumer_secret`
   - Auto-saves credentials to variables

2. **Step 2: Validate Credentials**
   - Validates the credentials work
   - Returns service info and scopes

**Valid Service Scopes:**
- `profile:read` - Read user profiles
- `data:read` - Read user data
- `data:write` - Write/update user data
- `admin:full` - Full administrative access

**Manual Testing:**
```bash
# Register service
POST {{user_mgmt_base_url}}/api/v1/service/register
Body: {
  "service_id": "my-app",
  "service_name": "My App",
  "description": "My application",
  "primary_contact_name": "John Doe",
  "admin_email": "admin@myapp.com",
  "scopes": ["profile:read", "data:read"],
  "scope_justifications": {
    "profile:read": "Need to display user info",
    "data:read": "Need for analytics"
  }
}

# Validate credentials
POST {{user_mgmt_base_url}}/api/v1/service/validate-credentials
Body: {
  "service_id": "{{service_id}}",
  "consumer_key": "{{consumer_key}}",
  "consumer_secret": "{{consumer_secret}}"
}
```

### 3. Traditional Authentication

**Create Token:**
```bash
POST {{auth_base_url}}/api/v1/tokens
Body: { "username": "testuser", "password": "testpass123" }
```

**Validate Token:**
```bash
POST {{auth_base_url}}/api/v1/validate
Body: { "token": "{{access_token}}" }
```

### 4. User Registration

**Register New User:**
```bash
POST {{user_mgmt_base_url}}/api/v1/auth/register
Body: {
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "phone_number": "+1234567890"
}
```

**Login:**
```bash
POST {{user_mgmt_base_url}}/api/v1/auth/login
Body: {
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}
```

## Test Scripts & Automation

All requests include automatic test scripts that:
- Extract and save tokens/IDs to environment variables
- Log success messages to console
- Chain requests together in workflows
- Validate response structure

**View Console Output:**
1. Open Postman Console: **View → Show Postman Console**
2. Run any request
3. See detailed logs, variable updates, and success messages

## Important Notes

### Google OAuth Testing
- Use **mock tokens** for local testing (no real Google account needed)
- Mock tokens work with test client ID: `test-google-client-id.apps.googleusercontent.com`
- For production, use real Google OAuth credentials

### Service Registration
- `consumer_secret` is **only shown once** - save it securely!
- Service IDs must match pattern: `^[a-z0-9_-]{3,64}$`
- All scopes must have justifications

### User Management
- Login requires **email** (not username)
- Passwords must meet security requirements
- Phone numbers must be unique

## Production Testing

To test against production:
1. Create a new environment "Production"
2. Update the base URLs to your production endpoints:
   ```
   auth_base_url = https://your-auth-service.com
   user_mgmt_base_url = https://your-user-service.com
   ```
3. For Google OAuth:
   - Use real Google credentials
   - Set up OAuth in Google Cloud Console
   - Remove mock token generation steps

## Troubleshooting

**Variables not auto-populating?**
- Ensure test scripts are enabled
- Check Postman Console for errors
- Verify correct environment is selected

**Requests failing?**
- Ensure both services are running (ports 8080 and 8000)
- Check base_url variables match your setup
- Review service logs in Replit console

**Google OAuth not working?**
- Use mock tokens for local testing
- Verify `GOOGLE_CLIENT_ID` environment variable
- Check `GOOGLE_OAUTH_STATUS.md` for details

**Service registration failing?**
- Use valid scopes: `profile:read`, `data:read`, `data:write`, `admin:full`
- Provide justification for each scope
- Service ID must be lowercase alphanumeric with dashes/underscores

**401 Unauthorized errors?**
- Token may be expired (default: 24 hours)
- Regenerate token with login/authentication
- Check user status is "ACTIVE"

## Quick Test Commands

### Test All Health Endpoints
```bash
curl http://localhost:8080/health
curl http://localhost:8000/health
```

### Generate and Test Google OAuth
```bash
# Generate mock token
TOKEN=$(curl -s -X POST http://localhost:8080/test/mock/google/token \
  -H "Content-Type: application/json" \
  -d '{"email":"test@gmail.com","name":"Test"}' \
  | jq -r '.id_token')

# Authenticate
curl -X POST http://localhost:8080/api/v1/auth/google/token \
  -H "Content-Type: application/json" \
  -d "{\"id_token\":\"$TOKEN\"}"
```

### Register Service
```bash
curl -X POST http://localhost:8000/api/v1/service/register \
  -H "Content-Type: application/json" \
  -d '{
    "service_id":"my-app-123",
    "service_name":"My App",
    "description":"Test app",
    "primary_contact_name":"John Doe",
    "admin_email":"admin@test.com",
    "scopes":["profile:read"],
    "scope_justifications":{"profile:read":"Need user data"}
  }'
```

## Additional Resources

- **GOOGLE_OAUTH_STATUS.md** - Complete Google OAuth implementation guide
- **GOOGLE_OAUTH_IMPLEMENTATION.md** - Original specification
- **replit.md** - Project architecture and configuration

## Collection Features

✅ Complete endpoint coverage for both services  
✅ Automated variable management  
✅ Test scripts with console logging  
✅ Multi-step workflow automation  
✅ Production-ready examples  
✅ Error handling demonstrations  
✅ Security best practices

## Support

For issues or questions:
1. Check service logs in Replit console
2. Review the documentation files
3. Verify environment configuration
4. Test with health check endpoints first
5. Check Postman Console for detailed errors
