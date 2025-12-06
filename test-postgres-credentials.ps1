# PostgreSQL Connection Test Script
# This script tests different PostgreSQL credentials

Write-Host "=========================================="  -ForegroundColor Cyan
Write-Host "PostgreSQL Credential Tester" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$credentials = @(
    @{User="postgres"; Password="postgres"},
    @{User="postgres"; Password="password"},
    @{User="postgrid"; Password="postgrid"},
    @{User="postgrid"; Password="password"}
)

$success = $false

foreach ($cred in $credentials) {
    $user = $cred.User
    $pass = $cred.Password
    
    Write-Host "Testing: $user / $pass" -ForegroundColor Yellow -NoNewline
    
    $env:PGPASSWORD = $pass
    $result = psql -U $user -h localhost -d postgres -c "SELECT 1;" 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " âœ… SUCCESS!" -ForegroundColor Green
        Write-Host ""
        Write-Host "============================================" -ForegroundColor Green
        Write-Host "FOUND WORKING CREDENTIALS:" -ForegroundColor Green
        Write-Host "  Username: $user" -ForegroundColor Green
        Write-Host "  Password: $pass" -ForegroundColor Green
        Write-Host "============================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Update am/config/database.env with:" -ForegroundColor Cyan
        Write-Host "DATABASE_URL=postgresql://${user}:${pass}@host.docker.internal:5432/postgres" -ForegroundColor White
        Write-Host ""
        $success = $true
        break
    } else {
        Write-Host " âœ— Failed" -ForegroundColor Red
    }
}

if (-not $success) {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "NO WORKING CREDENTIALS FOUND" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Is PostgreSQL running? (Check services)" -ForegroundColor White
    Write-Host "2. Is PostgreSQL listening on port 5432?" -ForegroundColor White
    Write-Host "3. What are your actual PostgreSQL credentials?" -ForegroundColor White
    Write-Host ""
    Write-Host "To reset PostgreSQL password:" -ForegroundColor Yellow
    Write-Host "  psql -U postgres" -ForegroundColor White
    Write-Host "  ALTER USER postgres WITH PASSWORD 'postgres'`;" -ForegroundColor White
}

# Clean up
$env:PGPASSWORD = $null
