"""
Transcribe Completion Handler Lambda Function
Triggered when Transcribe job completes - extracts Linguistic DNA and creates Style Vector
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List
import boto3
from decimal import Decimal

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')


def download_transcript_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    """Download and parse Transcribe JSON output from S3"""
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        transcript_json = json.loads(response['Body'].read().decode('utf-8'))
        return transcript_json
    except Exception as e:
        raise Exception(f"Failed to download transcript: {str(e)}")


def extract_linguistic_features(transcript_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract linguistic features from transcript
    Returns prosody features and cultural markers
    """
    items = transcript_data.get('results', {}).get('items', [])
    transcript_text = transcript_data.get('results', {}).get('transcripts', [{}])[0].get('transcript', '')
    
    if not items:
        return {
            'prosody': {
                'speech_rate': 0.0,
                'pause_frequency': 0.0,
                'average_pause_duration': 0.0,
            },
            'cultural_markers': [],
            'transcript_text': transcript_text,
            'word_count': 0,
            'duration': 0.0
        }
    
    # Calculate speech rate (words per minute)
    word_count = sum(1 for item in items if item['type'] == 'pronunciation')
    
    # Get timing information
    start_time = float(items[0].get('start_time', 0))
    end_time = float(items[-1].get('end_time', 0))
    duration_seconds = end_time - start_time if end_time > start_time else 0.0
    duration_minutes = duration_seconds / 60.0 if duration_seconds > 0 else 1.0
    
    speech_rate = word_count / duration_minutes if duration_minutes > 0 else 0.0
    
    # Calculate pause frequency and duration
    pauses = []
    prev_end_time = None
    
    for item in items:
        if item['type'] == 'pronunciation':
            current_start = float(item.get('start_time', 0))
            if prev_end_time is not None:
                pause_duration = current_start - prev_end_time
                if pause_duration > 0.1:  # Consider pauses > 100ms
                    pauses.append(pause_duration)
            prev_end_time = float(item.get('end_time', 0))
    
    pause_frequency = (len(pauses) / duration_minutes) if duration_minutes > 0 else 0.0
    average_pause_duration = sum(pauses) / len(pauses) if pauses else 0.0
    
    # Analyze cultural markers (filler words, expressions)
    text_lower = transcript_text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Common English filler words and expressions
    filler_words = ['um', 'uh', 'like', 'you know', 'i mean', 'actually', 'basically', 'literally', 'so', 'well', 'right']
    
    cultural_markers = []
    for filler in filler_words:
        pattern = r'\b' + re.escape(filler) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            count = len(matches)
            cultural_markers.append({
                'expression': filler,
                'frequency': count,
                'type': 'filler_word'
            })
    
    return {
        'prosody': {
            'speech_rate': round(speech_rate, 2),
            'pause_frequency': round(pause_frequency, 2),
            'average_pause_duration': round(average_pause_duration, 3),
        },
        'cultural_markers': cultural_markers,
        'transcript_text': transcript_text,
        'word_count': word_count,
        'duration': round(duration_seconds, 2)
    }


def create_style_vector(linguistic_features: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    """
    Create style vector from linguistic features
    This is a simplified embedding for MVP - uses feature values directly
    """
    prosody = linguistic_features['prosody']
    markers = linguistic_features['cultural_markers']
    
    # Create simple numerical embedding
    # Normalize speech rate (typical range: 100-200 wpm)
    normalized_speech_rate = min(1.0, prosody['speech_rate'] / 200.0)
    
    # Normalize pause frequency (typical range: 0-10 per minute)
    normalized_pause_freq = min(1.0, prosody['pause_frequency'] / 10.0)
    
    # Normalize pause duration (typical range: 0-2 seconds)
    normalized_pause_dur = min(1.0, prosody['average_pause_duration'] / 2.0)
    
    # Calculate filler word density
    word_count = linguistic_features['word_count']
    total_fillers = sum(m['frequency'] for m in markers)
    filler_density = (total_fillers / word_count) if word_count > 0 else 0.0
    
    # Create embedding vector
    embedding = [
        normalized_speech_rate,
        normalized_pause_freq,
        normalized_pause_dur,
        filler_density,
        # Add more features as needed
    ]
    
    # Create style description
    style_description = f"Professional English speaker with {prosody['speech_rate']:.0f} words per minute speech rate. "
    
    if prosody['speech_rate'] > 150:
        style_description += "Fast-paced and energetic delivery. "
    elif prosody['speech_rate'] < 120:
        style_description += "Measured and deliberate delivery. "
    else:
        style_description += "Moderate and balanced delivery. "
    
    if filler_density > 0.05:
        style_description += "Conversational tone with natural pauses. "
    else:
        style_description += "Clear and direct communication style. "
    
    return {
        'user_id': user_id,
        'embedding': embedding,
        'prosody_features': prosody,
        'cultural_markers': markers,
        'style_description': style_description,
        'transcript_sample': linguistic_features['transcript_text'][:500],  # First 500 chars
        'word_count': linguistic_features['word_count'],
        'audio_duration': linguistic_features['duration'],
        'version': 1,
        'created_at': datetime.utcnow().isoformat(),
        'updated_at': datetime.utcnow().isoformat()
    }


def convert_floats_to_decimal(obj):
    """Convert float values to Decimal for DynamoDB compatibility"""
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats_to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats_to_decimal(item) for item in obj]
    return obj


def store_style_vector_in_dynamodb(style_vector: Dict[str, Any], table_name: str):
    """Store style vector in DynamoDB"""
    try:
        table = dynamodb.Table(table_name)
        
        # Convert floats to Decimal for DynamoDB
        style_vector_decimal = convert_floats_to_decimal(style_vector)
        
        # Store in DynamoDB
        table.put_item(Item=style_vector_decimal)
        
        print(f"Style vector stored for user: {style_vector['user_id']}")
        
    except Exception as e:
        raise Exception(f"Failed to store style vector: {str(e)}")


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler triggered by S3 event when Transcribe output is ready
    Extracts linguistic DNA and creates style vector
    """
    try:
        table_name = os.environ.get('DYNAMODB_TABLE_NAME')
        if not table_name:
            raise Exception("DYNAMODB_TABLE_NAME not set")
        
        # Process S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Processing transcript: s3://{bucket}/{key}")
            
            # Extract job_id and user_id from S3 key
            # Key format: transcribe-output/{job_id}/{filename}.json
            parts = key.split('/')
            if len(parts) < 2:
                print(f"Invalid key format: {key}")
                continue
            
            job_id = parts[1]
            
            # For MVP, extract user_id from job metadata or use job_id
            # In production, you'd store job_id -> user_id mapping
            user_id = job_id  # Use job_id as user_id for now
            
            # Download and parse transcript
            transcript_data = download_transcript_from_s3(bucket, key)
            
            # Extract linguistic features
            linguistic_features = extract_linguistic_features(transcript_data)
            
            print(f"Extracted features: {linguistic_features['word_count']} words, "
                  f"{linguistic_features['duration']}s duration, "
                  f"{len(linguistic_features['cultural_markers'])} markers")
            
            # Create style vector
            style_vector = create_style_vector(linguistic_features, user_id)
            
            # Store in DynamoDB
            store_style_vector_in_dynamodb(style_vector, table_name)
            
            print(f"Successfully processed voice calibration for user: {user_id}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Voice calibration completed successfully"
            })
        }
        
    except Exception as e:
        print(f"Error processing transcript: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": f"Failed to process transcript: {str(e)}"
            })
        }
