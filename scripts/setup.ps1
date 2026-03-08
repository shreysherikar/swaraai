# Setup script for Swara AI Identity Layer (Windows PowerShell)

Write-Host "Setting up Swara AI Identity Layer..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "Python version: $pythonVersion"

# Create virtual environment
Write-Host "Creating Python virtual environment..." -ForegroundColor Yellow
python -m venv venv

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Install CDK dependencies
Write-Host "Installing CDK dependencies..." -ForegroundColor Yellow
Set-Location infrastructure
pip install -r requirements.txt
Set-Location ..

# Check AWS CLI
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}

Write-Host "Checking AWS credentials..." -ForegroundColor Yellow
aws sts get-caller-identity

# Set environment variables
Write-Host "Setting up environment variables..." -ForegroundColor Yellow
$env:AWS_ACCOUNT_ID = (aws sts get-caller-identity --query Account --output text)
if (-not $env:AWS_REGION) {
    $env:AWS_REGION = "us-east-1"
}

Write-Host "AWS Account ID: $env:AWS_ACCOUNT_ID"
Write-Host "AWS Region: $env:AWS_REGION"

# Create .env file
if (-not (Test-Path .env)) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please update .env file with your configuration" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your AWS configuration"
Write-Host "2. Run '.\venv\Scripts\Activate.ps1' to activate virtual environment"
Write-Host "3. Run 'cd infrastructure; cdk bootstrap' to bootstrap CDK (first time only)"
Write-Host "4. Run 'cd infrastructure; cdk deploy' to deploy infrastructure"
