# Restart Next.js Dev Server
# This ensures all environment variables and code changes are loaded

Write-Host "🔄 Restarting Next.js Development Server..." -ForegroundColor Cyan
Write-Host ""

# Stop any running Next.js processes
Write-Host "1. Stopping existing processes..." -ForegroundColor Yellow
Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*node_modules*" } | Stop-Process -Force -ErrorAction SilentlyContinue

# Clear Next.js cache
Write-Host "2. Clearing Next.js cache..." -ForegroundColor Yellow
if (Test-Path ".next") {
    Remove-Item -Recurse -Force ".next"
    Write-Host "   ✅ Cache cleared" -ForegroundColor Green
}

# Verify environment variables
Write-Host "3. Checking environment variables..." -ForegroundColor Yellow
if (Test-Path ".env.local") {
    Write-Host "   ✅ .env.local found" -ForegroundColor Green
    Get-Content ".env.local" | ForEach-Object {
        if ($_ -match "^NEXT_PUBLIC_") {
            Write-Host "   $($_.Split('=')[0]) = SET" -ForegroundColor Gray
        }
    }
} else {
    Write-Host "   ❌ .env.local NOT FOUND!" -ForegroundColor Red
}

Write-Host ""
Write-Host "4. Starting development server..." -ForegroundColor Yellow
Write-Host ""
Write-Host "   Frontend will be available at: http://localhost:3000" -ForegroundColor Cyan
Write-Host "   Debug page: http://localhost:3000/debug" -ForegroundColor Cyan
Write-Host ""
Write-Host "   Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host ""

# Start the dev server
npm run dev
