#!/bin/bash
# Deployment script for Swara AI Identity Layer

set -e

echo "Deploying Swara AI Identity Layer..."

# Activate virtual environment
source venv/bin/activate

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Build Lambda layer
echo "Building Lambda layer..."
mkdir -p lambda/layers/dependencies/python
pip install -r lambda/layers/dependencies/requirements.txt -t lambda/layers/dependencies/python/

# Deploy CDK stack
echo "Deploying CDK stack..."
cd infrastructure
cdk deploy --require-approval never

echo ""
echo "Deployment complete!"
echo ""
echo "Retrieving API Gateway URL and API Key..."
aws cloudformation describe-stacks \
    --stack-name SwaraAIIdentityLayer \
    --query 'Stacks[0].Outputs' \
    --output table
