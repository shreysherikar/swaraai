"""
Voice Processor Lambda Function
Orchestrates voice processing: Transcribe job management and profile status checking
"""
import json
import os
from typing import Dict, Any
import boto3
from botocore.exceptions import ClientError


# Initialize AWS clients
transcribe_client = boto3.client('transcribe')
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


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
            
            # Parse S3 URI to get bucket and key
            transcript_uri = job['Transcript']['TranscriptFileUri']
            if transcript_uri.startswith('s3://'):
                parts = transcript_uri[5:].split('/', 1)
                if len(parts) == 2:
                    result['transcript_bucket'] = parts[0]
                    result['transcript_key'] = parts[1]
                    
        elif job['TranscriptionJobStatus'] == 'FAILED':
            result['failure_reason'] = job.get('FailureReason', 'Unknown error')
        
        return result
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'BadRequestException':
            raise Exception(f"Transcription job not found: {job_name}")
        raise Exception(f"Failed to get transcription status: {str(e)}")


def start_transcription_job(job_id: str, bucket_name: str) -> Dict[str, Any]:
    """
    Start AWS Transcribe job for audio file
    
    Args:
        job_id: Unique job identifier
        bucket_name: S3 bucket with audio file
        
    Returns:
        Job details
    """
    job_name = f"swara-transcribe-{job_id}"
    
    # Check if job already exists
    try:
        existing_status = get_transcription_status(job_name)
        return {
            'message': 'Transcription job already exists',
            **existing_status
        }
    except Exception:
        pass  # Job doesn't exist, create new one
    
    # Find audio file in S3
    try:
        # List objects with job_id prefix
        response = s3_client.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"audio-uploads/{job_id}"
        )
        
        if 'Contents' not in response or not response['Contents']:
            raise Exception(f"Audio file not found for job_id: {job_id}")
        
        # Get first matching file
        s3_key = response['Contents'][0]['Key']
        audio_s3_uri = f"s3://{bucket_name}/{s3_key}"
        
        # Detect format from file extension
        file_format = s3_key.split('.')[-1].lower()
        if file_format not in ['mp3', 'wav', 'm4a', 'mp4']:
            file_format = 'mp3'  # Default
        
        # Start transcription job
        transcribe_response = transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            LanguageCode='en-IN',  # Indian English
            MediaFormat=file_format,
            Media={
                'MediaFileUri': audio_s3_uri
            },
            OutputBucketName=bucket_name,
            OutputKey=f"transcribe-output/{job_id}/",
            Settings={
                'ShowSpeakerLabels': False,
                'MaxSpeakerLabels': 1,
                'ChannelIdentification': False,
            }
        )
        
        return {
            'message': 'Transcription job started',
            'job_name': job_name,
            'status': transcribe_response['TranscriptionJob']['TranscriptionJobStatus'],
            'audio_uri': audio_s3_uri
        }
        
    except ClientError as e:
        raise Exception(f"Failed to start transcription: {str(e)}")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for voice processing status checking
    
    Args:
        event: API Gateway event with job ID
        context: Lambda context
        
    Returns:
        API Gateway response with processing status
    """
    # CORS headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Api-Key,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }
    
    try:
        bucket_name = os.environ.get('AUDIO_BUCKET')
        table_name = os.environ.get('DYNAMODB_TABLE_NAME')
        
        if not bucket_name or not table_name:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Server configuration error"
                })
            }
        
        # Parse query parameters
        params = event.get("queryStringParameters", {}) or {}
        job_id = params.get("job_id")
        
        if not job_id:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Missing required parameter: job_id"
                })
            }
        
        job_name = f"swara-transcribe-{job_id}"
        
        # Check if profile already exists in DynamoDB
        try:
            table = dynamodb.Table(table_name)
            response = table.get_item(Key={'user_id': job_id})
            
            if 'Item' in response:
                # Profile is ready!
                item = response['Item']
                return {
                    "statusCode": 200,
                    "headers": cors_headers,
                    "body": json.dumps({
                        "job_id": job_id,
                        "status": "COMPLETED",
                        "profile_ready": True,
                        "message": "Voice calibration complete! Your profile is ready.",
                        "style_description": str(item.get('style_description', '')),
                        "word_count": int(item.get('word_count', 0)),
                        "audio_duration": float(item.get('audio_duration', 0)),
                        "next_step": "You can now generate content using your voice profile"
                    })
                }
        except Exception as e:
            print(f"Error checking DynamoDB: {str(e)}")
        
        # Profile not ready yet, check Transcribe status
        try:
            status = get_transcription_status(job_name)
            
            # Add helpful next steps based on status
            if status['status'] == 'COMPLETED':
                status['profile_ready'] = False
                status['message'] = 'Transcription complete. Creating your voice profile...'
                status['next_step'] = 'Profile creation in progress. Check status again in a few moments.'
            elif status['status'] == 'IN_PROGRESS':
                status['profile_ready'] = False
                status['message'] = 'Analyzing your voice...'
                status['next_step'] = 'Transcription in progress. Check status again in a few moments.'
            elif status['status'] == 'FAILED':
                status['profile_ready'] = False
                status['message'] = 'Voice processing failed.'
                status['next_step'] = 'Please upload a new audio file.'
            
            return {
                "statusCode": 200,
                "headers": cors_headers,
                "body": json.dumps({
                    "job_id": job_id,
                    **status
                })
            }
            
        except Exception as e:
            # Job not found
            return {
                "statusCode": 404,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": f"Job not found: {job_id}",
                    "message": "Please upload an audio file first"
                })
            }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": cors_headers,
            "body": json.dumps({
                "error": f"Internal server error: {str(e)}"
            })
        }
