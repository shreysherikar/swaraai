#!/bin/bash
# Setup script for Swara AI Identity Layer

set -e

echo "Setting up Swara AI Identity Layer..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install CDK dependencies
echo "Installing CDK dependencies..."
cd infrastructure
pip install -r requirements.txt
cd ..

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install AWS CLI."
    exit 1
fi

echo "Checking AWS credentials..."
aws sts get-caller-identity

# Set environment variables
echo "Setting up environment variables..."
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=${AWS_REGION:-us-east-1}

echo "AWS Account ID: $AWS_ACCOUNT_ID"
echo "AWS Region: $AWS_REGION"

# Create .env file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please update .env file with your configuration"
fi

echo ""
echo "Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env file with your AWS configuration"
echo "2. Run 'source venv/bin/activate' to activate virtual environment"
echo "3. Run 'cd infrastructure && cdk bootstrap' to bootstrap CDK (first time only)"
echo "4. Run 'cd infrastructure && cdk deploy' to deploy infrastructure"
