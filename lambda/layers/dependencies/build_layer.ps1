# Build Lambda Layer with dependencies for Windows

# Create python directory for Lambda layer
New-Item -ItemType Directory -Force -Path python | Out-Null

# Install dependencies
pip install -r requirements.txt -t python/

Write-Host "Lambda layer built successfully in python/ directory"
