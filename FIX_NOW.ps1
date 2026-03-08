# ONE COMMAND TO FIX EVERYTHING
# This deploys the backend with CORS fixes

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  FIXING CORS ERROR - DEPLOYING BACKEND" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "The issue: Lambda functions need CORS headers deployed to AWS" -ForegroundColor Yellow
Write-Host "The fix: Deploy the updated Lambda functions" -ForegroundColor Yellow
Write-Host ""

Write-Host "⏱️  This will take 2-3 minutes..." -ForegroundColor Gray
Write-Host ""

# Navigate to infrastructure
Set-Location infrastructure

# Deploy
Write-Host "🚀 Deploying to AWS..." -ForegroundColor Cyan
cdk deploy --require-approval never

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ DEPLOYMENT SUCCESSFUL!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Now test the frontend:" -ForegroundColor Yellow
    Write-Host "1. Go to http://localhost:3000/debug" -ForegroundColor White
    Write-Host "2. Click 'Test API'" -ForegroundColor White
    Write-Host "3. Should see success! ✅" -ForegroundColor White
    Write-Host ""
    Write-Host "4. Go to http://localhost:3000/generate" -ForegroundColor White
    Write-Host "5. Generate content" -ForegroundColor White
    Write-Host "6. Should work! ✅" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    Write-Host "Check the error above" -ForegroundColor Red
    Write-Host ""
}

# Go back to root
Set-Location ..
