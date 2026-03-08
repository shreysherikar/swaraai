# Swara AI Identity Layer - Setup Guide

Complete setup guide for the Swara AI Identity Layer project.

## Prerequisites

### Required Software
- **Python 3.11+**: [Download](https://www.python.org/downloads/)
- **Node.js 18+**: [Download](https://nodejs.org/)
- **AWS CLI**: [Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- **AWS CDK CLI**: Install with `npm install -g aws-cdk`
- **Git**: [Download](https://git-scm.com/downloads)

### AWS Account Requirements
- Active AWS account
- IAM user with administrator access (or specific permissions for Lambda, S3, OpenSearch, etc.)
- AWS credentials configured locally

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., `us-east-1`)
- Default output format (e.g., `json`)

Verify configuration:
```bash
aws sts get-caller-identity
```

### 2. Run Setup Script

**Linux/Mac:**
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

**Windows PowerShell:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup.ps1
```

### 3. Update Environment Variables

Edit the `.env` file created by the setup script:

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012  # Your AWS account ID

# Other variables will be populated after deployment
```

### 4. Deploy Infrastructure

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\Activate.ps1  # Windows

# Bootstrap CDK (first time only)
cd infrastructure
cdk bootstrap

# Deploy stack
cdk deploy
```

The deployment will take 10-15 minutes due to OpenSearch domain creation.

### 5. Retrieve API Configuration

After deployment, get your API Gateway URL and API Key:

```bash
aws cloudformation describe-stacks \
    --stack-name SwaraAIIdentityLayer \
    --query 'Stacks[0].Outputs' \
    --output table
```

Update your `.env` file with these values.

## Manual Setup (Alternative)

If you prefer manual setup:

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# OR
.\venv\Scripts\Activate.ps1  # Windows
```

### 2. Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Install CDK Dependencies

```bash
cd infrastructure
pip install -r requirements.txt
cd ..
```

### 4. Build Lambda Layer

```bash
mkdir -p lambda/layers/dependencies/python
pip install -r lambda/layers/dependencies/requirements.txt \
    -t lambda/layers/dependencies/python/
```

### 5. Deploy with CDK

```bash
cd infrastructure
cdk bootstrap  # First time only
cdk deploy
```

## Project Structure

```
.
├── infrastructure/          # AWS CDK infrastructure code
│   ├── app.py              # CDK app entry point
│   ├── stacks/             # CDK stack definitions
│   └── cdk.json            # CDK configuration
├── lambda/                 # Lambda function code
│   ├── handlers/           # Lambda function handlers
│   ├── shared/             # Shared utilities and models
│   └── layers/             # Lambda layers
├── frontend/               # Next.js frontend (to be implemented)
├── tests/                  # Test suite
├── scripts/                # Setup and deployment scripts
├── requirements.txt        # Python dependencies
└── .env.example           # Environment variable template
```

## Testing

Run tests:
```bash
pytest tests/
```

Run with coverage:
```bash
pytest tests/ --cov=lambda --cov-report=html
```

## Development Workflow

1. **Make changes** to Lambda functions in `lambda/handlers/`
2. **Test locally** using pytest
3. **Deploy changes**: `cd infrastructure && cdk deploy`
4. **Monitor logs**: Check CloudWatch logs in AWS Console

## AWS Services Used

| Service | Purpose | Cost Estimate (MVP) |
|---------|---------|---------------------|
| Lambda | Serverless compute | ~$0.20/million requests |
| API Gateway | REST API | ~$3.50/million requests |
| S3 | Audio storage | ~$0.023/GB |
| Transcribe | Voice-to-text | ~$0.024/minute |
| OpenSearch | Vector storage | ~$0.048/hour (t3.small) |
| Bedrock | Content generation | ~$0.00025/1K tokens |
| KMS | Encryption | ~$1/month |
| CloudWatch | Logging | ~$0.50/GB |

**Estimated MVP cost**: $50-100/month for moderate usage

## Troubleshooting

### CDK Bootstrap Fails
```bash
# Ensure you have correct AWS credentials
aws sts get-caller-identity

# Try with explicit account and region
cdk bootstrap aws://ACCOUNT-ID/REGION
```

### Lambda Layer Build Issues
```bash
# Clean and rebuild
rm -rf lambda/layers/dependencies/python
mkdir -p lambda/layers/dependencies/python
pip install -r lambda/layers/dependencies/requirements.txt \
    -t lambda/layers/dependencies/python/ --platform manylinux2014_x86_64 --only-binary=:all:
```

### OpenSearch Deployment Timeout
OpenSearch domain creation can take 15-20 minutes. If deployment times out:
1. Check AWS Console for OpenSearch domain status
2. Wait for domain to become active
3. Re-run `cdk deploy`

### Permission Errors
Ensure your IAM user has permissions for:
- Lambda (create, update, invoke)
- S3 (create bucket, put/get objects)
- OpenSearch (create domain)
- VPC (create VPC, subnets, security groups)
- IAM (create roles, policies)
- CloudFormation (create/update stacks)

## Next Steps

After successful setup:

1. **Test API endpoints** using Postman or curl
2. **Implement Task 2**: Voice calibration Lambda function
3. **Set up frontend**: Initialize Next.js project in `frontend/`
4. **Configure monitoring**: Set up CloudWatch alarms

## Support

For issues or questions:
- Check AWS CloudWatch logs for Lambda errors
- Review CDK deployment output for resource creation issues
- Ensure all prerequisites are installed correctly

## Cleanup

To remove all AWS resources:

```bash
cd infrastructure
cdk destroy
```

**Warning**: This will delete all data including audio files and style vectors.
