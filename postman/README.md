# Postman Collections

This folder contains Postman collections for testing the Auth Tokens and User Management microservices.

## Collections

### 1. Auth-Tokens-Service.postman_collection.json
Complete collection for the Auth Tokens service (Port 8080) including:
- Health & info endpoints
- Traditional username/password authentication
- Google OAuth authentication
- Token validation
- Mock Google token generation
- Complete end-to-end test flow

### 2. User-Management-Service.postman_collection.json
Complete collection for the User Management service (Port 8000) including:
- User login/credential validation
- Google user creation and linking
- User profile endpoints
- Testing scenarios for new users and account linking

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
- `user_id` - Auto-populated by user creation requests

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

## Testing Google OAuth Flow

### Complete End-to-End Test
Use the **"Complete Google OAuth Flow (Test)"** folder in Auth Tokens collection:

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

Each step has test scripts that:
- Auto-save variables for next steps
- Log progress to console
- Verify response status

### Individual Testing
You can also test endpoints individually:

**Generate Mock Token:**
```
POST {{auth_base_url}}/test/mock/google/token
Body: { "email": "test@gmail.com", "name": "Test User" }
```

**Authenticate:**
```
POST {{auth_base_url}}/api/v1/auth/google/token
Body: { "id_token": "{{google_id_token}}" }
```

**Validate:**
```
POST {{auth_base_url}}/api/v1/validate
Body: { "token": "{{access_token}}" }
```

## Testing Traditional Authentication

**Create Token:**
```
POST {{auth_base_url}}/api/v1/tokens
Body: { "username": "testuser", "password": "testpass123" }
```

**Validate Token:**
```
POST {{auth_base_url}}/api/v1/validate
Body: { "token": "{{access_token}}" }
```

## Production Testing

To test against production:
1. Create a new environment "Production"
2. Update the base URLs to your production endpoints
3. For Google OAuth, use real Google credentials instead of mock tokens
4. Remove the mock token generation step

## Test Scripts

All requests include automatic test scripts that:
- Extract and save tokens to variables
- Log success messages to console
- Chain requests together in workflows

View console output:
1. Open Postman Console (View → Show Postman Console)
2. Run requests to see detailed logs

## Troubleshooting

**Variables not auto-populating?**
- Check that test scripts are enabled
- View Postman Console for error messages
- Verify environment is selected

**Requests failing?**
- Ensure both services are running (ports 8080 and 8000)
- Check the base_url variables match your setup
- Review service logs for errors

**Google OAuth not working?**
- Use mock tokens for local testing
- Verify GOOGLE_CLIENT_ID is set to test value
- Check GOOGLE_OAUTH_STATUS.md for setup details

## Additional Resources

- **GOOGLE_OAUTH_STATUS.md** - Complete Google OAuth implementation guide
- **GOOGLE_OAUTH_IMPLEMENTATION.md** - Original specification
- **replit.md** - Project architecture and configuration

## Support

For issues or questions:
1. Check service logs in Replit console
2. Review the documentation files
3. Verify environment configuration
4. Test with health check endpoints first
