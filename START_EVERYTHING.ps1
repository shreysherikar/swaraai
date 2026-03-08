#!/usr/bin/env pwsh
# Start Everything - Complete System Startup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STARTING SWARA AI SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "frontend/package.json")) {
    Write-Host "Error: Please run this script from the project root directory" -ForegroundColor Red
    exit 1
}

# Start frontend
Write-Host "Starting Next.js frontend..." -ForegroundColor Yellow
Write-Host ""

cd frontend

# Check if node_modules exists
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Green
    npm install
}

# Start dev server
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "FRONTEND STARTING" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pages:" -ForegroundColor Cyan
Write-Host "  - Home: http://localhost:3000" -ForegroundColor White
Write-Host "  - Calibrate: http://localhost:3000/calibrate" -ForegroundColor White
Write-Host "  - Generate: http://localhost:3000/generate" -ForegroundColor White
Write-Host "  - Profile: http://localhost:3000/profile" -ForegroundColor White
Write-Host ""
Write-Host "Backend API: https://gyv6j2nexb.execute-api.us-east-1.amazonaws.com/prod" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

npm run dev
