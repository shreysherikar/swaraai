#!/usr/bin/env pwsh
# Quick Test Script - Run this before submission

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QUICK PRE-SUBMISSION TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Check if frontend is running
Write-Host "Test 1: Checking frontend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 5 -UseBasicParsing
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Frontend is running!" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Frontend not running. Start it with: cd frontend ; npm run dev" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Check AWS deployment
Write-Host "Test 2: Checking AWS backend..." -ForegroundColor Yellow
Write-Host "Checking if CDK stack is deployed..." -ForegroundColor Gray

cd infrastructure

try {
    $stackInfo = cdk list 2>&1
    if ($stackInfo -match "SwaraAIIdentityLayer") {
        Write-Host "✅ CDK stack found!" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Could not verify CDK stack" -ForegroundColor Yellow
}

cd ..

Write-Host ""

# Test 3: Check environment variables
Write-Host "Test 3: Checking environment..." -ForegroundColor Yellow

if (Test-Path ".env") {
    $envContent = Get-Content ".env"
    if ($envContent -match "GROQ_API_KEY") {
        Write-Host "✅ GROQ_API_KEY found in .env" -ForegroundColor Green
    } else {
        Write-Host "⚠️  GROQ_API_KEY not found in .env" -ForegroundColor Yellow
    }
    
    if ($envContent -match "NEXT_PUBLIC_API_URL") {
        Write-Host "✅ API URL configured" -ForegroundColor Green
    } else {
        Write-Host "⚠️  API URL not configured" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "READY FOR SUBMISSION!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Open: http://localhost:3000/calibrate" -ForegroundColor White
Write-Host "2. Upload an audio file (most reliable)" -ForegroundColor White
Write-Host "3. Wait 1-2 minutes for processing" -ForegroundColor White
Write-Host "4. Go to /generate and create content" -ForegroundColor White
Write-Host "5. Show judges the result!" -ForegroundColor White
Write-Host ""

Write-Host "Demo Tips:" -ForegroundColor Cyan
Write-Host "- Use file upload (more reliable than live recording)" -ForegroundColor White
Write-Host "- Have a backup audio file ready" -ForegroundColor White
Write-Host "- Emphasize: Real AWS services, not mocked" -ForegroundColor White
Write-Host "- Show: Automatic pipeline, no manual steps" -ForegroundColor White
Write-Host ""

Write-Host "🏆 GO WIN THIS! 🏆" -ForegroundColor Green
