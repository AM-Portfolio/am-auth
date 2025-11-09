# 🔐 Password Reset Feature Guide

Complete guide for the forgot password and password reset functionality.

---

## 📋 Overview

The password reset feature allows users to securely reset their password when they forget it. The system uses secure tokens with expiration to ensure safety.

### Key Features:
- ✅ Secure token generation (URL-safe, 32 bytes)
- ✅ Token hashing (SHA-256) for database storage
- ✅ 1-hour token expiration
- ✅ One-time use tokens (cleared after successful reset)
- ✅ Security-first approach (doesn't reveal if email exists)
- ✅ Password validation (minimum 8 characters)

---

## 🔄 Complete Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    1. User Forgets Password                  │
│                    POST /api/v1/password/forgot              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              2. System Generates Reset Token                 │
│  • Creates secure random token (32 bytes)                    │
│  • Hashes token with SHA-256 for storage                     │
│  • Sets expiration (1 hour from now)                         │
│  • Stores hashed token in database                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              3. System Sends Reset Email                     │
│  • Email contains unhashed token                             │
│  • Token is URL-safe for links                               │
│  • In dev: Token shown in terminal logs                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              4. User Clicks Reset Link                       │
│  • Frontend can verify token first (optional)                │
│  • GET /api/v1/password/verify-token/{token}                 │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              5. User Submits New Password                    │
│                POST /api/v1/password/reset                   │
│  • Validates token (checks hash and expiration)              │
│  • Hashes new password with Bcrypt                           │
│  • Updates password in database                              │
│  • Clears reset token                                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              6. User Can Login with New Password             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 API Endpoints

### 1. Request Password Reset

**Endpoint:** `POST /api/v1/password/forgot`

**Request:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If an account with that email exists, a password reset link has been sent.",
  "email": "user@example.com"
}
```

**Notes:**
- Always returns success for security (doesn't reveal if email exists)
- Token expires in 1 hour
- In development, token is printed to terminal logs
- In production, token would be sent via email

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/password/forgot" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com"}'
```

---

### 2. Verify Reset Token (Optional)

**Endpoint:** `GET /api/v1/password/verify-token/{token}`

**Response (Valid Token):**
```json
{
  "valid": true,
  "message": "Token is valid",
  "email": "user@example.com"
}
```

**Response (Invalid/Expired Token):**
```json
{
  "valid": false,
  "message": "Invalid reset token"
}
```

**Notes:**
- Use this endpoint to check token validity before showing reset form
- Helps provide better UX by catching expired tokens early

**Example:**
```bash
curl "http://localhost:8000/api/v1/password/verify-token/mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI"
```

---

### 3. Reset Password with Token

**Endpoint:** `POST /api/v1/password/reset`

**Request:**
```json
{
  "token": "mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI",
  "new_password": "NewSecurePass123!"
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Password has been reset successfully. You can now login with your new password."
}
```

**Response (Invalid Token):**
```json
{
  "success": false,
  "message": "Invalid or expired reset token"
}
```

**Response (Expired Token):**
```json
{
  "success": false,
  "message": "Reset token has expired. Please request a new one."
}
```

**Validation Rules:**
- Token is required
- New password is required
- Password must be at least 8 characters long

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/password/reset" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI",
    "new_password": "NewSecurePass123!"
  }'
```

---

## 🧪 Complete Testing Example

### Step 1: Request Password Reset
```bash
curl -X POST "http://localhost:8000/api/v1/password/forgot" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com"}' | python -m json.tool
```

**Check Terminal Logs for Token:**
```
[MOCK EMAIL] Password reset email sent to test@example.com with token: mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI
```

### Step 2: Verify Token (Optional)
```bash
curl "http://localhost:8000/api/v1/password/verify-token/mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI" | python -m json.tool
```

### Step 3: Reset Password
```bash
curl -X POST "http://localhost:8000/api/v1/password/reset" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "mOSRfAV9ljxHoTSj3xqM73W8VqGs8KWowSxHHf-sPyI",
    "new_password": "NewPassword123!"
  }' | python -m json.tool
```

### Step 4: Login with New Password
```bash
curl -X POST "http://localhost:8001/api/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "NewPassword123!"
  }' | python -m json.tool
```

### Step 5: Verify Old Password Doesn't Work
```bash
curl -X POST "http://localhost:8001/api/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test@example.com",
    "password": "OldPassword123!"
  }' | python -m json.tool
```

**Expected:** `{"detail": "Invalid credentials"}`

---

## 🗄️ Database Schema

### New Columns Added to `user_accounts` Table:

```sql
password_reset_token         VARCHAR(255)              -- Hashed reset token
password_reset_token_expires TIMESTAMP WITH TIME ZONE  -- Token expiration time
```

**Migration Command:**
```sql
ALTER TABLE user_accounts 
ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255),
ADD COLUMN IF NOT EXISTS password_reset_token_expires TIMESTAMP WITH TIME ZONE;
```

---

## 🔐 Security Features

### 1. Token Generation
- Uses `secrets.token_urlsafe(32)` for cryptographically secure random tokens
- 32 bytes = 256 bits of entropy
- URL-safe encoding (can be used in links)

### 2. Token Storage
- Tokens are hashed with SHA-256 before storage
- Only hashed version is stored in database
- Original token is never stored

### 3. Token Expiration
- Tokens expire after 1 hour
- Expiration checked on every reset attempt
- Expired tokens cannot be used

### 4. One-Time Use
- Token is cleared from database after successful reset
- Cannot be reused even if not expired

### 5. Email Privacy
- System doesn't reveal if email exists in database
- Always returns success message
- Prevents email enumeration attacks

### 6. Password Security
- New password is hashed with Bcrypt (12 rounds)
- Minimum 8 characters required
- Can add additional strength requirements

---

## 📝 Implementation Details

### Files Created/Modified:

1. **`modules/account_management/infrastructure/models/user_account_orm.py`**
   - Added `password_reset_token` column
   - Added `password_reset_token_expires` column

2. **`modules/account_management/application/use_cases/forgot_password.py`**
   - `ForgotPasswordUseCase` - Handles reset request
   - `ResetPasswordWithTokenUseCase` - Handles password reset

3. **`modules/account_management/api/public/password_reset_router.py`**
   - `/api/v1/password/forgot` endpoint
   - `/api/v1/password/reset` endpoint
   - `/api/v1/password/verify-token/{token}` endpoint

4. **`main.py`**
   - Registered password reset router

---

## 🎨 Frontend Integration Example

### React/Next.js Example:

```typescript
// Request password reset
async function requestPasswordReset(email: string) {
  const response = await fetch('http://localhost:8000/api/v1/password/forgot', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email })
  });
  
  const data = await response.json();
  // Show success message (always shows success for security)
  alert(data.message);
}

// Verify token (optional, for better UX)
async function verifyResetToken(token: string) {
  const response = await fetch(
    `http://localhost:8000/api/v1/password/verify-token/${token}`
  );
  
  const data = await response.json();
  return data.valid;
}

// Reset password
async function resetPassword(token: string, newPassword: string) {
  const response = await fetch('http://localhost:8000/api/v1/password/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, new_password: newPassword })
  });
  
  const data = await response.json();
  
  if (data.success) {
    // Redirect to login page
    window.location.href = '/login';
  } else {
    // Show error message
    alert(data.message);
  }
}
```

---

## 🚀 Production Deployment

### Email Service Integration

Replace `MockEmailService` with a real email service:

```python
# Example with SendGrid
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

class SendGridEmailService(EmailServiceInterface):
    def __init__(self, api_key: str):
        self.client = SendGridAPIClient(api_key)
    
    async def send_password_reset_email(self, to: Email, token: str):
        reset_link = f"https://yourapp.com/reset-password?token={token}"
        
        message = Mail(
            from_email='noreply@yourapp.com',
            to_emails=str(to),
            subject='Reset Your Password',
            html_content=f'''
                <h2>Password Reset Request</h2>
                <p>Click the link below to reset your password:</p>
                <a href="{reset_link}">Reset Password</a>
                <p>This link expires in 1 hour.</p>
                <p>If you didn't request this, please ignore this email.</p>
            '''
        )
        
        response = self.client.send(message)
        return response.status_code == 202
```

### Environment Variables

```env
# Email Service
EMAIL_SERVICE=sendgrid
SENDGRID_API_KEY=your-api-key
FROM_EMAIL=noreply@yourapp.com

# Frontend URL (for reset links)
FRONTEND_URL=https://yourapp.com

# Token Expiration (in minutes)
PASSWORD_RESET_TOKEN_EXPIRY=60
```

---

## ✅ Testing Checklist

- [x] Request reset for existing email
- [x] Request reset for non-existing email (should still return success)
- [x] Verify token validity
- [x] Reset password with valid token
- [x] Try to reset with expired token
- [x] Try to reset with invalid token
- [x] Try to reuse token after successful reset
- [x] Login with new password
- [x] Verify old password doesn't work
- [x] Test password validation (min 8 characters)

---

## 📚 Additional Resources

- [OWASP Password Reset Guidelines](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [Python secrets module](https://docs.python.org/3/library/secrets.html)
- [Bcrypt Password Hashing](https://github.com/pyca/bcrypt/)

---

**Status:** ✅ Fully Implemented and Tested

**Last Updated:** November 10, 2025
