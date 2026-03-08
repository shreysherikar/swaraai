"""
Transcribe Starter Lambda Function
Triggers AWS Transcribe jobs for audio files uploaded to S3
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError


# Initialize AWS clients
transcribe_client = boto3.client('transcribe')
s3_client = boto3.client('s3')

# Hinglish and Indian English custom vocabulary
CUSTOM_VOCABULARY = [
    # Common Hinglish terms
    "yaar", "actually", "basically", "na", "hai", "kya", "matlab",
    "achha", "theek", "haan", "nahi", "bhai", "dude", "yaar",
    # Indian English expressions
    "prepone", "revert back", "do the needful", "out of station",
    "cousin brother", "cousin sister", "good name", "timepass",
    # Common Indian words in English context
    "ji", "sir", "madam", "uncle", "aunty", "beta",
]


def create_custom_vocabulary(vocabulary_name: str, bucket_name: str) -> bool:
    """
    Create or update custom vocabulary for Hinglish terms
    
    Args:
        vocabulary_name: Name for the custom vocabulary
        bucket_name: S3 bucket for vocabulary file
        
    Returns:
        True if vocabulary exists or was created successfully
    """
    try:
        # Check if vocabulary already exists
        try:
            response = transcribe_client.get_vocabulary(VocabularyName=vocabulary_name)
            if response['VocabularyState'] in ['READY', 'PENDING']:
                return True
        except transcribe_client.exceptions.NotFoundException:
            pass
        
        # Create vocabulary file content
        vocab_content = "\n".join(CUSTOM_VOCABULARY)
        vocab_key = f"transcribe-vocabulary/{vocabulary_name}.txt"
        
        # Upload vocabulary to S3
        s3_client.put_object(
            Bucket=bucket_name,
            Key=vocab_key,
            Body=vocab_content.encode('utf-8'),
            ContentType='text/plain'
        )
        
        # Create custom vocabulary
        transcribe_client.create_vocabulary(
            VocabularyName=vocabulary_name,
            LanguageCode='en-IN',  # Indian English
            VocabularyFileUri=f"s3://{bucket_name}/{vocab_key}"
        )
        
        return True
        
    except ClientError as e:
        print(f"Error creating custom vocabulary: {str(e)}")
        return False


def start_transcription_job(
    job_id: str,
    audio_s3_uri: str,
    output_bucket: str,
    vocabulary_name: str
) -> Dict[str, Any]:
    """
    Start AWS Transcribe job
    
    Args:
        job_id: Unique job identifier
        audio_s3_uri: S3 URI of audio file
        output_bucket: S3 bucket for output
        vocabulary_name: Custom vocabulary name
        
    Returns:
        Transcription job details
        
    Raises:
        ClientError: If Transcribe job fails to start
    """
    job_name = f"swara-transcribe-{job_id}"
    
    try:
        # Start transcription job
        response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-IN',  # Indian English
            MediaFormat='mp3',  # Will be auto-detected
            Media={
                'MediaFileUri': audio_s3_uri
            },
            OutputBucketName=output_bucket,
            OutputKey=f"transcribe-output/{job_id}/",
            Settings={
                'VocabularyName': vocabulary_name,
                'ShowSpeakerLabels': False,
                'MaxSpeakerLabels': 1,
                'ChannelIdentification': False,
            },
            JobExecutionSettings={
                'AllowDeferredExecution': False,
                'DataAccessRoleArn': os.environ.get('TRANSCRIBE_ROLE_ARN', '')
            } if os.environ.get('TRANSCRIBE_ROLE_ARN') else {}
        )
        
        return {
            'job_name': job_name,
            'job_status': response['TranscriptionJob']['TranscriptionJobStatus'],
            'creation_time': response['TranscriptionJob']['CreationTime'].isoformat(),
        }
        
    except ClientError as e:
        raise Exception(f"Failed to start transcription job: {str(e)}")


def get_transcription_status(job_name: str) -> Dict[str, Any]:
    """
    Get status of transcription job
    
    Args:
        job_name: Transcription job name
        
    Returns:
        Job status and details
    """
    try:
        response = transcribe_client.get_transcription_job(
            TranscriptionJobName=job_name
        )
        
        job = response['TranscriptionJob']
        result = {
            'job_name': job_name,
            'status': job['TranscriptionJobStatus'],
            'creation_time': job['CreationTime'].isoformat(),
        }
        
        if job['TranscriptionJobStatus'] == 'COMPLETED':
            result['transcript_uri'] = job['Transcript']['TranscriptFileUri']
        elif job['TranscriptionJobStatus'] == 'FAILED':
            result['failure_reason'] = job.get('FailureReason', 'Unknown error')
        
        return result
        
    except ClientError as e:
        raise Exception(f"Failed to get transcription status: {str(e)}")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for starting Transcribe jobs
    
    Args:
        event: Can be triggered by S3 event or API Gateway
        context: Lambda context
        
    Returns:
        Response with job status
    """
    try:
        bucket_name = os.environ.get('AUDIO_BUCKET')
        if not bucket_name:
            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "error": "Server configuration error: AUDIO_BUCKET not set"
                })
            }
        
        vocabulary_name = "swara-hinglish-vocab"
        
        # Ensure custom vocabulary exists
        create_custom_vocabulary(vocabulary_name, bucket_name)
        
        # Check if triggered by S3 event or API Gateway
        if 'Records' in event:
            # S3 event trigger
            for record in event['Records']:
                s3_bucket = record['s3']['bucket']['name']
                s3_key = record['s3']['object']['key']
                
                # Extract job_id from S3 key (format: audio-uploads/{job_id}.{format})
                job_id = s3_key.split('/')[-1].split('.')[0]
                
                audio_s3_uri = f"s3://{s3_bucket}/{s3_key}"
                
                # Start transcription
                job_details = start_transcription_job(
                    job_id=job_id,
                    audio_s3_uri=audio_s3_uri,
                    output_bucket=bucket_name,
                    vocabulary_name=vocabulary_name
                )
                
                return {
                    "statusCode": 200,
                    "body": json.dumps({
                        "message": "Transcription job started",
                        "job_id": job_id,
                        **job_details
                    })
                }
        else:
            # API Gateway trigger
            params = event.get("queryStringParameters", {}) or {}
            job_id = params.get("job_id")
            action = params.get("action", "start")
            
            if not job_id:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "Missing required parameter: job_id"
                    })
                }
            
            if action == "status":
                # Get job status
                job_name = f"swara-transcribe-{job_id}"
                status = get_transcription_status(job_name)
                
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "job_id": job_id,
                        **status
                    })
                }
            else:
                # Start transcription
                s3_key = f"audio-uploads/{job_id}.mp3"  # Assume mp3 for now
                audio_s3_uri = f"s3://{bucket_name}/{s3_key}"
                
                job_details = start_transcription_job(
                    job_id=job_id,
                    audio_s3_uri=audio_s3_uri,
                    output_bucket=bucket_name,
                    vocabulary_name=vocabulary_name
                )
                
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "message": "Transcription job started",
                        "job_id": job_id,
                        **job_details
                    })
                }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}"
            })
        }
