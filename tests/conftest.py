"""
Pytest configuration and shared fixtures
"""
import pytest
import os
from moto import mock_aws
import boto3


@pytest.fixture
def aws_credentials():
    """Mock AWS credentials for testing"""
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


@pytest.fixture
def s3_client(aws_credentials):
    """Mock S3 client"""
    with mock_aws():
        yield boto3.client("s3", region_name="us-east-1")


@pytest.fixture
def transcribe_client(aws_credentials):
    """Mock Transcribe client"""
    with mock_aws():
        yield boto3.client("transcribe", region_name="us-east-1")


@pytest.fixture
def audio_bucket(s3_client):
    """Create mock S3 bucket for audio files"""
    bucket_name = "test-swara-audio-bucket"
    s3_client.create_bucket(Bucket=bucket_name)
    return bucket_name
