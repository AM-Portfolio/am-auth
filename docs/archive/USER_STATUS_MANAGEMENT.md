# User Status Management API

## Overview
New endpoints to check and manage user account status in the User Management service.

## Valid Status Values

| Status | Description | Use Case |
|--------|-------------|----------|
| `active` | User account is active | User can login and use the system |
| `inactive` | User account is deactivated | User voluntarily deactivated account |
| `pending_verification` | Awaiting verification | New users awaiting email/phone verification |
| `suspended` | Account suspended | Temporary suspension due to policy violations |
| `deleted` | Account marked as deleted | Soft delete - account flagged for deletion |

**Default Status:** All new users start with `pending_verification`

## API Endpoints

### 1. Get User Status by ID
**GET** `/api/v1/users/{user_id}/status`

Get complete user status information by user ID (UUID).

**Request:**
```bash
GET http://localhost:8000/api/v1/users/1ac55c4d-db30-4c4d-ad2d-4abc36a5dba9/status
```

**Response:**
```json
{
  "user_id": "1ac55c4d-db30-4c4d-ad2d-4abc36a5dba9",
  "email": "user@example.com",
  "status": "pending_verification",
  "email_verified": false,
  "auth_provider": "local",
  "created_at": "2025-10-10T16:29:15.788429+00:00",
  "last_login_at": null,
  "verified_at": null,
  "locked_until": null,
  "failed_login_attempts": 0
}
```

### 2. Get User Status by Email
**GET** `/api/v1/users/email/{email}/status`

Get complete user status information by email address.

**Request:**
```bash
GET http://localhost:8000/api/v1/users/email/user@example.com/status
```

**Response:** Same as above

### 3. Update User Status by ID
**PATCH** `/api/v1/users/{user_id}/status`

Update user status by user ID with optional reason.

**Request:**
```bash
PATCH http://localhost:8000/api/v1/users/1ac55c4d-db30-4c4d-ad2d-4abc36a5dba9/status
Content-Type: application/json

{
  "status": "active",
  "reason": "Email verification completed"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User status updated successfully: Email verification completed",
  "user_id": "1ac55c4d-db30-4c4d-ad2d-4abc36a5dba9",
  "old_status": "pending_verification",
  "new_status": "active"
}
```

### 4. Update User Status by Email
**PATCH** `/api/v1/users/email/{email}/status`

Update user status by email address with optional reason.

**Request:**
```bash
PATCH http://localhost:8000/api/v1/users/email/user@example.com/status
Content-Type: application/json

{
  "status": "suspended",
  "reason": "Policy violation - spam activity detected"
}
```

**Response:**
```json
{
  "success": true,
  "message": "User status updated successfully: Policy violation - spam activity detected",
  "user_id": "1ac55c4d-db30-4c4d-ad2d-4abc36a5dba9",
  "old_status": "active",
  "new_status": "suspended"
}
```

## Common Use Cases

### 1. Email Verification Flow
```bash
# User registers
POST /api/v1/auth/register
# Status: pending_verification

# After email verification
PATCH /api/v1/users/{user_id}/status
{
  "status": "active",
  "reason": "Email verified successfully"
}
```

### 2. Account Suspension
```bash
# Check current status
GET /api/v1/users/{user_id}/status

# Suspend account
PATCH /api/v1/users/{user_id}/status
{
  "status": "suspended",
  "reason": "Multiple failed login attempts"
}
```

### 3. Account Deactivation
```bash
# User requests to deactivate
PATCH /api/v1/users/email/{email}/status
{
  "status": "inactive",
  "reason": "User requested account deactivation"
}
```

### 4. Account Deletion (Soft Delete)
```bash
PATCH /api/v1/users/{user_id}/status
{
  "status": "deleted",
  "reason": "User requested account deletion"
}
```

## Integration with Authentication

The Auth Tokens service checks user status before issuing JWT tokens:
- ✅ `active` - Token issued
- ❌ `pending_verification` - 403 Forbidden
- ❌ `inactive` - 403 Forbidden
- ❌ `suspended` - 403 Forbidden
- ❌ `deleted` - 403 Forbidden

**Only users with status="active" can receive JWT tokens!**

## Postman Testing

The Postman collection includes a new **"User Status Management"** folder with:
1. Get User Status by ID
2. Get User Status by Email
3. Update User Status by ID
4. Update User Status by Email

Variables used:
- `{{user_id}}` - User UUID
- `{{user_email}}` - User email address

## Security Considerations

1. **Authentication Required:** These endpoints should be protected with admin authentication
2. **Audit Logging:** The `reason` field provides audit trail for status changes
3. **Status Validation:** Only valid status values are accepted
4. **Soft Delete:** `deleted` status preserves data while marking account as deleted

## Error Handling

**Invalid User ID:**
```json
{
  "detail": "Invalid user ID format. Must be a valid UUID"
}
```

**User Not Found:**
```json
{
  "detail": "User with ID {user_id} not found"
}
```

**Invalid Status:**
```json
{
  "detail": "Invalid status value. Must be one of: active, inactive, pending_verification, suspended, deleted"
}
```

## Examples

### Complete User Lifecycle

```bash
# 1. Register (status: pending_verification)
POST /api/v1/auth/register
{
  "email": "newuser@example.com",
  "password": "SecurePass123!",
  "phone_number": "+1234567890"
}

# 2. Check status
GET /api/v1/users/email/newuser@example.com/status
# Response: status = "pending_verification"

# 3. Activate after verification
PATCH /api/v1/users/email/newuser@example.com/status
{
  "status": "active",
  "reason": "Email verified"
}

# 4. User can now login
POST /api/v1/auth/login
{
  "email": "newuser@example.com",
  "password": "SecurePass123!"
}

# 5. If policy violation, suspend
PATCH /api/v1/users/email/newuser@example.com/status
{
  "status": "suspended",
  "reason": "Spam detected"
}

# 6. Restore if needed
PATCH /api/v1/users/email/newuser@example.com/status
{
  "status": "active",
  "reason": "False positive, account restored"
}
```

## Files Created

1. **Backend Router:** `am-user-management/modules/account_management/api/public/user_status_router.py`
2. **Postman Collection:** Updated `postman/User-Management-Service.postman_collection.json`
3. **Documentation:** This file

## Testing Summary

✅ All endpoints tested and working:
- GET by ID - Returns complete status info
- GET by email - Returns complete status info
- PATCH by ID - Updates status with reason
- PATCH by email - Updates status with reason

✅ Postman collection updated with 4 new requests
✅ Variables added: `user_email`
✅ Test scripts included for automated testing

---

**Ready to use!** Import the updated Postman collection and start managing user statuses. 🚀
