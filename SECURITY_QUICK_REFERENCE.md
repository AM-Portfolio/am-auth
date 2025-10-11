# 🔒 Quick Reference: Why Postman Can't Access Internal Services

## The Simple Answer

**Even with a valid JWT token, Postman cannot connect because the ports are not exposed to your computer.**

```
Your Computer (Postman)
        ↓
   🚫 BLOCKED 🚫  ← No port mapping in docker-compose.yml
        ↓
Docker Internal Network
  (Services running here)
```

---

## Visual Comparison

### ✅ Public Services (You CAN access):

```
docker-compose.yml:
  am-user-management:
    ports:
      - "8000:8000"  ← This line exposes the port!

Result:
  Postman → localhost:8000 → ✅ Connected
```

### ❌ Internal Services (You CANNOT access):

```
docker-compose.yml:
  am-python-internal-service:
    # No ports: section!  ← Port NOT exposed!

Result:
  Postman → localhost:8002 → ❌ Connection Refused
```

---

## The Two Security Layers

```
🚧 Layer 1: Network Isolation
   ├─ Blocks: External connections
   ├─ How: No port mapping in docker-compose.yml
   └─ When: BEFORE token is checked

🔑 Layer 2: JWT Authentication
   ├─ Blocks: Unauthorized internal requests
   ├─ How: Validates JWT token
   └─ When: ONLY if Layer 1 allows connection
```

---

## Test It Yourself

### Prove Layer 1 is blocking:

```bash
# This will fail (Connection Refused)
curl http://localhost:8002/health

# Output: curl: (7) Failed to connect to localhost port 8002: Connection refused
```

### Prove Layer 2 works (from inside Docker):

```bash
# Without token = 401
docker exec am-am-user-management-1 python3 -c "
import httpx
r = httpx.get('http://am-python-internal-service:8002/internal/service-info')
print(r.status_code)  # Output: 401
"

# With valid token = 200
docker exec am-am-user-management-1 python3 -c "
import httpx
token = 'YOUR_TOKEN'
r = httpx.get(
    'http://am-python-internal-service:8002/internal/service-info',
    headers={'Authorization': f'Bearer {token}'}
)
print(r.status_code)  # Output: 200
"
```

---

## How to Test Internal Services

### Option 1: Run the security test (Easiest)
```bash
./test_security.sh
# Shows all 8 security tests - all passing ✅
```

### Option 2: Generate fresh token
```bash
python3 generate_token.py
# Creates token.txt with valid service token
```

### Option 3: See it in action
```bash
# Run with verbose output
./test_security.sh

# You'll see:
# ✅ External access BLOCKED (Layer 1 working)
# ✅ Internal access requires token (Layer 2 working)
# ✅ Valid token grants access (Both layers working)
```

---

## Common Questions

**Q: My JWT token is valid, why doesn't it work?**
- A: Connection is refused BEFORE your token is checked.

**Q: Is this a bug?**
- A: No! This is intentional security (defense in depth).

**Q: How do I test these endpoints?**
- A: Use `./test_security.sh` - it tests from inside Docker.

**Q: Can't I just expose the ports?**
- A: You could add `ports: ["8002:8002"]` but it defeats the security.

---

## The Bottom Line

✅ **Your Authorization header is correct**
✅ **Your JWT token is valid**  
✅ **Security is working as designed**  
❌ **Postman can't reach the service** ← This is the security feature!

**To test internal services:** Use the provided scripts that run FROM INSIDE the Docker network.

---

## Test Results

```
$ ./test_security.sh

🎉 SECURITY IS WORKING! 8/8 tests passed

Network Isolation:
  ✅ Python service blocked externally
  ✅ Java service blocked externally

JWT Authentication:
  ✅ Rejects requests without token
  ✅ Accepts requests with valid token

Service Communication:
  ✅ Internal services can communicate
  ✅ Public services accessible
```

---

## Related Documentation

- `SECURITY_ARCHITECTURE.md` - Full detailed explanation
- `SERVICE_TO_SERVICE_AUTH_PROMPT.md` - Implementation guide
- `test_security.sh` - Security test script
- `generate_token.py` - Token generation script

**🎓 Key Insight:** The fact that Postman can't access these services PROVES your security is working correctly!
