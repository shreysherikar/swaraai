#!/bin/bash
# Build Lambda Layer with dependencies

# Create python directory for Lambda layer
mkdir -p python

# Install dependencies
pip install -r requirements.txt -t python/

# Create zip file (optional, CDK will handle this)
# zip -r layer.zip python/

echo "Lambda layer built successfully in python/ directory"
