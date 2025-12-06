#!/bin/bash
# Access Token obtained from previous manual test (valid for 30 mins)
ACCESS_TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NjQ5NDcyNjAsImlhdCI6MTc2NDk0NTQ2MCwic3ViIjoiN2NlNzE2N2YtYWZiMy00ODNhLWIwNmMtNzY1YWE3MDBhYjFkIiwidXNlcm5hbWUiOiJwcml5YW5zaHVrcGRAZ21haWwuY29tIiwiZW1haWwiOiJwcml5YW5zaHVrcGRAZ21haWwuY29tIiwic2NvcGVzIjpbInJlYWQiLCJ3cml0ZSIsInByb2ZpbGUiXX0.ob5vXgV4qVbVcYE8slr9XO1mKIs1DGnCOKOF0Y0ZBFs"

echo "Testing Protected API (Document Types) with Google User Token..."
echo "User: priyanshukpd@gmail.com"
echo "Token: ${ACCESS_TOKEN:0:20}..."

curl -v -H "Authorization: Bearer $ACCESS_TOKEN" http://localhost:8000/api/v1/documents/types
