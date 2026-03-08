#!/usr/bin/env python3
"""
Swara AI Identity Layer - CDK Application Entry Point
"""
import os
import aws_cdk as cdk
from stacks.swara_stack import SwaraStack

app = cdk.App()

# Get environment configuration
env = cdk.Environment(
    account=os.environ.get("AWS_ACCOUNT_ID", os.environ.get("CDK_DEFAULT_ACCOUNT")),
    region=os.environ.get("AWS_REGION", os.environ.get("CDK_DEFAULT_REGION", "us-east-1"))
)

# Create main stack
SwaraStack(
    app,
    "SwaraAIIdentityLayer",
    env=env,
    description="Swara AI Identity Layer - Linguistic Sovereignty Platform"
)

app.synth()
