# Deployment script for Swara AI Infrastructure
# Deploys updated Lambda functions with CORS fixes

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "SWARA AI - DEPLOYMENT SCRIPT" -ForegroundColor Cyan
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

Write-Host "`n📦 Step 1: Synthesizing CDK Stack..." -ForegroundColor Yellow
cdk synth

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ CDK synthesis failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Synthesis complete!" -ForegroundColor Green

Write-Host "`n🚀 Step 2: Deploying to AWS..." -ForegroundColor Yellow
cdk deploy --require-approval never

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Deployment failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Deployment complete!" -ForegroundColor Green

Write-Host "`n🧪 Step 3: Running API Tests..." -ForegroundColor Yellow
python test_api_endpoints.py

Write-Host "`n" -NoNewline
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "DEPLOYMENT COMPLETE" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan

Write-Host "`n📋 Next Steps:" -ForegroundColor Yellow
Write-Host "1. Frontend is running at http://localhost:3000" -ForegroundColor White
Write-Host "2. Test voice calibration and content generation" -ForegroundColor White
Write-Host "3. Check browser console for any errors" -ForegroundColor White
Write-Host "4. API URL: https://gyv6j2nexb.execute-api.us-east-1.amazonaws.com/prod" -ForegroundColor White
