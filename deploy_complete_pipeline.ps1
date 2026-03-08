#!/usr/bin/env pwsh
# Deploy Complete Voice Processing Pipeline

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploying Complete Voice Pipeline" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "infrastructure/app.py")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Step 1: Deploy infrastructure
Write-Host "Step 1: Deploying AWS infrastructure..." -ForegroundColor Yellow
Write-Host ""

cd infrastructure

# Activate virtual environment
if (Test-Path "venv/Scripts/Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Creating virtual environment..." -ForegroundColor Green
    python -m venv venv
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
}

# Deploy CDK stack
Write-Host ""
Write-Host "Deploying CDK stack..." -ForegroundColor Green
cdk deploy --require-approval never

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "Error: CDK deployment failed" -ForegroundColor Red
    cd ..
    exit 1
}

cd ..

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "What's New:" -ForegroundColor Cyan
Write-Host "  ✓ Upload automatically triggers Transcribe" -ForegroundColor Green
Write-Host "  ✓ S3 event triggers linguistic analysis" -ForegroundColor Green
Write-Host "  ✓ Real voice analysis (not test data)" -ForegroundColor Green
Write-Host "  ✓ Automatic profile creation" -ForegroundColor Green
Write-Host "  ✓ Frontend polls for completion" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Go to http://localhost:3000/calibrate" -ForegroundColor White
Write-Host "  2. Upload or record your voice" -ForegroundColor White
Write-Host "  3. Wait 1-2 minutes for processing" -ForegroundColor White
Write-Host "  4. Generate content with YOUR voice profile" -ForegroundColor White
Write-Host ""

Write-Host "Testing:" -ForegroundColor Cyan
Write-Host "  Run: cd infrastructure ; python test_full_workflow.py" -ForegroundColor White
Write-Host ""

Write-Host "Troubleshooting:" -ForegroundColor Cyan
Write-Host "  - Check CloudWatch logs for Lambda functions" -ForegroundColor White
Write-Host "  - Check S3 bucket for transcribe-output/ folder" -ForegroundColor White
Write-Host "  - Check DynamoDB table for your job_id" -ForegroundColor White
Write-Host ""
