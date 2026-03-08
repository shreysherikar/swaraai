# Swara AI Identity Layer - Infrastructure

AWS CDK infrastructure as code for the Swara AI Identity Layer platform.

## Architecture

The infrastructure includes:

- **API Gateway**: REST API with API key authentication
- **Lambda Functions**: 
  - Audio Upload Handler
  - Voice Processor (with Transcribe integration)
  - Content Generator (with Bedrock integration)
- **S3**: Audio file storage with encryption
- **OpenSearch**: Vector storage for style vectors
- **VPC**: Secure network for OpenSearch
- **KMS**: Encryption key management
- **CloudWatch**: Logging and monitoring

## Prerequisites

- AWS CLI configured with credentials
- AWS CDK CLI installed (`npm install -g aws-cdk`)
- Python 3.11+
- Sufficient AWS permissions to create resources

## Deployment

### First Time Setup

1. Bootstrap CDK (only needed once per account/region):
```bash
cdk bootstrap
```

2. Deploy the stack:
```bash
cdk deploy
```

### Subsequent Deployments

```bash
cdk deploy
```

### View Stack Outputs

```bash
aws cloudformation describe-stacks \
    --stack-name SwaraAIIdentityLayer \
    --query 'Stacks[0].Outputs'
```

## Stack Resources

### Compute
- 3 Lambda functions (Python 3.11)
- Lambda layer for shared dependencies

### Storage
- S3 bucket with KMS encryption
- OpenSearch domain (t3.small.search, 10GB)

### Networking
- VPC with public and private subnets
- NAT Gateway for Lambda internet access
- Security groups for OpenSearch

### Security
- KMS key with rotation enabled
- IAM roles with least privilege
- API Gateway with API key authentication

### Monitoring
- CloudWatch log groups for all Lambda functions
- API Gateway logging and metrics

## Cost Optimization

For development/hackathon:
- Single OpenSearch node (t3.small.search)
- 7-day S3 lifecycle policy
- Single NAT Gateway
- Removal policies set to DESTROY

For production:
- Multi-AZ OpenSearch deployment
- Longer S3 retention
- Multiple NAT Gateways
- Removal policies set to RETAIN

## Cleanup

To delete all resources:
```bash
cdk destroy
```

Note: Some resources may need manual deletion if they contain data.
