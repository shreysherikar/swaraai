"""
Audio Upload Handler Lambda Function
Handles audio file uploads to S3 for voice calibration
"""
import json
import os
import base64
import uuid
import mimetypes
from datetime import datetime
from typing import Dict, Any, Optional
import boto3
from botocore.exceptions import ClientError


# Initialize AWS clients
s3_client = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

# Supported audio formats
SUPPORTED_FORMATS = {
    'audio/mpeg': 'mp3',
    'audio/mp3': 'mp3',
    'audio/wav': 'wav',
    'audio/x-wav': 'wav',
    'audio/wave': 'wav',
    'audio/mp4': 'm4a',
    'audio/x-m4a': 'm4a',
    'audio/webm': 'webm',
    'audio/ogg': 'ogg',
}

SUPPORTED_EXTENSIONS = ['mp3', 'wav', 'm4a', 'webm', 'ogg']


def detect_audio_format(file_name: str, content_type: Optional[str] = None) -> Optional[str]:
    """
    Detect audio format from file name and content type
    
    Args:
        file_name: Name of the audio file
        content_type: MIME type of the file
        
    Returns:
        Detected format (mp3, wav, m4a) or None if unsupported
    """
    # Try content type first
    if content_type and content_type.lower() in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[content_type.lower()]
    
    # Try file extension
    extension = file_name.lower().split('.')[-1]
    if extension in SUPPORTED_EXTENSIONS:
        return extension
    
    # Try mimetypes library
    guessed_type, _ = mimetypes.guess_type(file_name)
    if guessed_type and guessed_type.lower() in SUPPORTED_FORMATS:
        return SUPPORTED_FORMATS[guessed_type.lower()]
    
    return None


def upload_to_s3(audio_data: bytes, job_id: str, file_format: str, bucket_name: str) -> Dict[str, Any]:
    """
    Upload audio file to S3
    
    Args:
        audio_data: Binary audio data
        job_id: Unique job identifier
        file_format: Audio format (mp3, wav, m4a)
        bucket_name: S3 bucket name
        
    Returns:
        Dictionary with S3 key and metadata
        
    Raises:
        ClientError: If S3 upload fails
    """
    s3_key = f"audio-uploads/{job_id}.{file_format}"
    
    try:
        # Upload to S3 with server-side encryption
        s3_client.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=audio_data,
            ContentType=f"audio/{file_format}",
            ServerSideEncryption='aws:kms',
            Metadata={
                'job_id': job_id,
                'format': file_format,
                'upload_timestamp': datetime.utcnow().isoformat(),
            }
        )
        
        return {
            's3_key': s3_key,
            'bucket': bucket_name,
            'size_bytes': len(audio_data),
        }
        
    except ClientError as e:
        raise Exception(f"S3 upload failed: {str(e)}")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for audio file uploads
    
    Args:
        event: API Gateway event with audio file data
        context: Lambda context
        
    Returns:
        API Gateway response with upload status and job ID
    """
    # CORS headers
    cors_headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,X-Api-Key,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }
    
    try:
        # Get environment variables
        bucket_name = os.environ.get('AUDIO_BUCKET')
        if not bucket_name:
            return {
                "statusCode": 500,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Server configuration error: AUDIO_BUCKET not set"
                })
            }
        
        # Parse request body
        body = json.loads(event.get("body", "{}"))
        
        # Validate required fields
        if "audio_data" not in body or "file_name" not in body:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": "Missing required fields: audio_data, file_name"
                })
            }
        
        file_name = body["file_name"]
        audio_data_b64 = body["audio_data"]
        content_type = body.get("content_type")
        user_id = body.get("user_id", "anonymous")
        
        # Detect audio format
        audio_format = detect_audio_format(file_name, content_type)
        if not audio_format:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": f"Unsupported audio format. Supported formats: {', '.join(SUPPORTED_EXTENSIONS)}",
                    "file_name": file_name,
                    "content_type": content_type
                })
            }
        
        # Decode base64 audio data
        try:
            audio_data = base64.b64decode(audio_data_b64)
        except Exception as e:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": f"Invalid base64 audio data: {str(e)}"
                })
            }
        
        # Validate file size (max 50MB for MVP)
        max_size = 50 * 1024 * 1024  # 50MB
        if len(audio_data) > max_size:
            return {
                "statusCode": 400,
                "headers": cors_headers,
                "body": json.dumps({
                    "error": f"File too large. Maximum size: {max_size / (1024 * 1024)}MB",
                    "file_size_mb": len(audio_data) / (1024 * 1024)
                })
            }
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Upload to S3
        upload_result = upload_to_s3(audio_data, job_id, audio_format, bucket_name)
        
        # Automatically trigger Transcribe job
        job_name = f"swara-transcribe-{job_id}"
        audio_s3_uri = f"s3://{bucket_name}/{upload_result['s3_key']}"
        
        # Map format for Transcribe (webm and ogg need special handling)
        transcribe_format = audio_format
        if audio_format == 'webm':
            transcribe_format = 'webm'
        elif audio_format == 'ogg':
            transcribe_format = 'ogg'
        
        try:
            transcribe_client.start_transcription_job(
                TranscriptionJobName=job_name,
                LanguageCode='en-US',  # English (user doesn't speak Hindi)
                MediaFormat=transcribe_format,
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
            transcribe_status = "started"
        except Exception as e:
            # Log error but don't fail the upload
            print(f"Failed to start Transcribe job: {str(e)}")
            transcribe_status = "failed_to_start"
        
        return {
            "statusCode": 200,
            "headers": cors_headers,
            "body": json.dumps({
                "message": "Audio file uploaded and processing started",
                "job_id": job_id,
                "user_id": user_id,
                "file_name": file_name,
                "format": audio_format,
                "size_bytes": upload_result['size_bytes'],
                "s3_key": upload_result['s3_key'],
                "timestamp": datetime.utcnow().isoformat(),
                "status": "processing",
                "transcribe_status": transcribe_status,
                "transcribe_job_name": job_name,
                "next_step": "Processing your voice. This takes 1-2 minutes. Check status with GET /voice/status?job_id={job_id}"
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
