"""
Linguistic DNA Extractor Lambda Function
Extracts prosody features and cultural markers from Transcribe output
"""
import json
import os
import re
from datetime import datetime
from typing import Dict, Any, List, Tuple
import boto3
from botocore.exceptions import ClientError

# Import data models
import sys
sys.path.append('/opt/python')  # Lambda layer path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'shared'))

from models import (
    LinguisticDNA, ProsodyVector, CulturalMarker, CadencePattern,
    ExpressionFrequency, ConfidenceMetrics, AudioMetadata, AudioFormat
)


# Initialize AWS clients
s3_client = boto3.client('s3')

# Indian English and Hinglish patterns
HINGLISH_TERMS = [
    "yaar", "na", "hai", "kya", "matlab", "achha", "theek", "haan", 
    "nahi", "bhai", "ji", "beta", "dude"
]

INDIAN_ENGLISH_PHRASES = [
    "prepone", "revert back", "do the needful", "out of station",
    "cousin brother", "cousin sister", "good name", "timepass",
    "pass out", "shift", "foreign return", "co-brother"
]

CULTURAL_EXPRESSIONS = [
    "actually", "basically", "only", "itself", "no", "what to do",
    "like that", "all", "simply", "directly"
]


def download_transcript_from_s3(bucket: str, key: str) -> Dict[str, Any]:
    """
    Download and parse Transcribe JSON output from S3
    
    Args:
        bucket: S3 bucket name
        key: S3 object key
        
    Returns:
        Parsed transcript JSON
    """
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        transcript_json = json.loads(response['Body'].read().decode('utf-8'))
        return transcript_json
    except ClientError as e:
        raise Exception(f"Failed to download transcript: {str(e)}")


def extract_prosody_features(transcript_data: Dict[str, Any]) -> ProsodyVector:
    """
    Extract prosody features from transcript
    
    Args:
        transcript_data: Transcribe JSON output
        
    Returns:
        ProsodyVector with speech patterns
    """
    items = transcript_data.get('results', {}).get('items', [])
    
    if not items:
        # Return default values if no items
        return ProsodyVector(
            speech_rate=0.0,
            pause_frequency=0.0,
            average_pause_duration=0.0,
            pitch_variation=0.0,
            energy_variation=0.0
        )
    
    # Calculate speech rate (words per minute)
    word_count = sum(1 for item in items if item['type'] == 'pronunciation')
    
    # Get timing information
    start_time = float(items[0].get('start_time', 0))
    end_time = float(items[-1].get('end_time', 0))
    duration_minutes = (end_time - start_time) / 60.0 if end_time > start_time else 1.0
    
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
    
    # Pitch and energy variation (simplified - would need audio analysis for accuracy)
    # For MVP, use word confidence as proxy
    confidences = [float(item.get('alternatives', [{}])[0].get('confidence', 0.5)) 
                   for item in items if item['type'] == 'pronunciation']
    
    pitch_variation = calculate_std_dev(confidences) if confidences else 0.0
    energy_variation = pitch_variation  # Simplified for MVP
    
    return ProsodyVector(
        speech_rate=round(speech_rate, 2),
        pause_frequency=round(pause_frequency, 2),
        average_pause_duration=round(average_pause_duration, 3),
        pitch_variation=round(pitch_variation, 3),
        energy_variation=round(energy_variation, 3)
    )


def calculate_std_dev(values: List[float]) -> float:
    """Calculate standard deviation of values"""
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def identify_cultural_markers(transcript_text: str) -> Tuple[List[CulturalMarker], ExpressionFrequency]:
    """
    Identify Indian English and Hinglish cultural markers
    
    Args:
        transcript_text: Full transcript text
        
    Returns:
        Tuple of (cultural markers list, expression frequency)
    """
    text_lower = transcript_text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    cultural_markers = []
    hinglish_freq = {}
    indian_english_freq = {}
    
    # Identify Hinglish terms
    for term in HINGLISH_TERMS:
        pattern = r'\b' + re.escape(term) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            count = len(matches)
            hinglish_freq[term] = count
            
            # Find context for first occurrence
            match = re.search(pattern, text_lower)
            if match:
                start = max(0, match.start() - 30)
                end = min(len(transcript_text), match.end() + 30)
                context = transcript_text[start:end].strip()
                
                cultural_markers.append(CulturalMarker(
                    expression=term,
                    frequency=count,
                    context=context,
                    confidence=0.9
                ))
    
    # Identify Indian English phrases
    for phrase in INDIAN_ENGLISH_PHRASES:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            count = len(matches)
            indian_english_freq[phrase] = count
            
            match = re.search(pattern, text_lower)
            if match:
                start = max(0, match.start() - 30)
                end = min(len(transcript_text), match.end() + 30)
                context = transcript_text[start:end].strip()
                
                cultural_markers.append(CulturalMarker(
                    expression=phrase,
                    frequency=count,
                    context=context,
                    confidence=0.85
                ))
    
    # Identify cultural expressions
    for expression in CULTURAL_EXPRESSIONS:
        pattern = r'\b' + re.escape(expression) + r'\b'
        matches = re.findall(pattern, text_lower)
        if matches:
            count = len(matches)
            
            # Add to appropriate category
            if count >= 3:  # Only add if used frequently
                match = re.search(pattern, text_lower)
                if match:
                    start = max(0, match.start() - 30)
                    end = min(len(transcript_text), match.end() + 30)
                    context = transcript_text[start:end].strip()
                    
                    cultural_markers.append(CulturalMarker(
                        expression=expression,
                        frequency=count,
                        context=context,
                        confidence=0.7
                    ))
    
    expression_frequency = ExpressionFrequency(
        hinglish_terms=hinglish_freq,
        indian_english_phrases=indian_english_freq,
        total_expressions=len(cultural_markers)
    )
    
    return cultural_markers, expression_frequency


def generate_confidence_scores(
    transcript_data: Dict[str, Any],
    cultural_markers: List[CulturalMarker],
    audio_duration: float,
    word_count: int
) -> ConfidenceMetrics:
    """
    Generate confidence scores for the analysis
    
    Args:
        transcript_data: Transcribe output
        cultural_markers: Identified cultural markers
        audio_duration: Duration in seconds
        word_count: Total word count
        
    Returns:
        ConfidenceMetrics with scores
    """
    # Calculate sample quality based on duration and word count
    min_duration = 30  # 30 seconds minimum
    min_words = 50  # 50 words minimum
    
    duration_score = min(1.0, audio_duration / min_duration)
    word_score = min(1.0, word_count / min_words)
    sample_quality_score = (duration_score + word_score) / 2
    
    # Prosody confidence based on audio duration
    prosody_confidence = min(0.95, 0.5 + (audio_duration / 300))  # Max at 5 minutes
    
    # Cultural marker confidence based on number of markers found
    cultural_marker_confidence = min(0.95, 0.3 + (len(cultural_markers) * 0.1))
    
    # Overall confidence is weighted average
    overall_confidence = (
        prosody_confidence * 0.4 +
        cultural_marker_confidence * 0.3 +
        sample_quality_score * 0.3
    )
    
    return ConfidenceMetrics(
        overall_confidence=round(overall_confidence, 3),
        prosody_confidence=round(prosody_confidence, 3),
        cultural_marker_confidence=round(cultural_marker_confidence, 3),
        sample_quality_score=round(sample_quality_score, 3)
    )


def extract_linguistic_dna(
    user_id: str,
    job_id: str,
    transcript_bucket: str,
    transcript_key: str,
    audio_metadata: Dict[str, Any]
) -> LinguisticDNA:
    """
    Extract complete linguistic DNA from transcript
    
    Args:
        user_id: User identifier
        job_id: Job identifier
        transcript_bucket: S3 bucket with transcript
        transcript_key: S3 key for transcript
        audio_metadata: Original audio metadata
        
    Returns:
        Complete LinguisticDNA profile
    """
    # Download transcript
    transcript_data = download_transcript_from_s3(transcript_bucket, transcript_key)
    
    # Extract transcript text
    transcript_text = transcript_data.get('results', {}).get('transcripts', [{}])[0].get('transcript', '')
    
    # Extract prosody features
    prosody_vector = extract_prosody_features(transcript_data)
    
    # Identify cultural markers
    cultural_markers, expression_frequency = identify_cultural_markers(transcript_text)
    
    # Calculate audio duration and word count
    items = transcript_data.get('results', {}).get('items', [])
    word_count = sum(1 for item in items if item['type'] == 'pronunciation')
    
    audio_duration = 0.0
    if items:
        start_time = float(items[0].get('start_time', 0))
        end_time = float(items[-1].get('end_time', 0))
        audio_duration = end_time - start_time
    
    # Generate confidence scores
    confidence_scores = generate_confidence_scores(
        transcript_data, cultural_markers, audio_duration, word_count
    )
    
    # Create cadence pattern (simplified for MVP)
    cadence_pattern = CadencePattern(
        rhythm_score=prosody_vector.speech_rate / 200.0,  # Normalized
        emphasis_pattern=[],  # Would need deeper analysis
        intonation_curve=[]   # Would need audio signal processing
    )
    
    # Create audio metadata
    audio_meta = AudioMetadata(
        file_name=audio_metadata.get('file_name', 'unknown'),
        format=AudioFormat(audio_metadata.get('format', 'mp3')),
        duration_seconds=audio_duration,
        file_size_bytes=audio_metadata.get('size_bytes'),
        upload_timestamp=datetime.fromisoformat(audio_metadata.get('upload_timestamp', datetime.utcnow().isoformat()))
    )
    
    # Create LinguisticDNA
    linguistic_dna = LinguisticDNA(
        user_id=user_id,
        prosody_vectors=[prosody_vector],
        cultural_markers=cultural_markers,
        cadence_patterns=[cadence_pattern],
        expression_frequency=expression_frequency,
        confidence_scores=confidence_scores,
        extraction_timestamp=datetime.utcnow(),
        audio_sample_metadata=audio_meta
    )
    
    return linguistic_dna


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for linguistic DNA extraction
    
    Args:
        event: Event with job_id or S3 trigger
        context: Lambda context
        
    Returns:
        Response with linguistic DNA
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
        
        # Parse request
        if 'Records' in event:
            # S3 event trigger (Transcribe output ready)
            for record in event['Records']:
                transcript_bucket = record['s3']['bucket']['name']
                transcript_key = record['s3']['object']['key']
                
                # Extract job_id from key
                job_id = transcript_key.split('/')[-2] if '/' in transcript_key else 'unknown'
                
                # For MVP, use default metadata
                audio_metadata = {
                    'file_name': f'{job_id}.mp3',
                    'format': 'mp3',
                    'upload_timestamp': datetime.utcnow().isoformat()
                }
                
                # Extract linguistic DNA
                linguistic_dna = extract_linguistic_dna(
                    user_id='anonymous',
                    job_id=job_id,
                    transcript_bucket=transcript_bucket,
                    transcript_key=transcript_key,
                    audio_metadata=audio_metadata
                )
                
                # Convert to dict for JSON serialization
                result = {
                    'user_id': linguistic_dna.user_id,
                    'job_id': job_id,
                    'prosody': {
                        'speech_rate': linguistic_dna.prosody_vectors[0].speech_rate,
                        'pause_frequency': linguistic_dna.prosody_vectors[0].pause_frequency,
                        'average_pause_duration': linguistic_dna.prosody_vectors[0].average_pause_duration,
                    },
                    'cultural_markers_count': len(linguistic_dna.cultural_markers),
                    'cultural_markers': [
                        {
                            'expression': m.expression,
                            'frequency': m.frequency,
                            'confidence': m.confidence
                        }
                        for m in linguistic_dna.cultural_markers[:10]  # Top 10
                    ],
                    'confidence_scores': {
                        'overall': linguistic_dna.confidence_scores.overall_confidence,
                        'prosody': linguistic_dna.confidence_scores.prosody_confidence,
                        'cultural_markers': linguistic_dna.confidence_scores.cultural_marker_confidence,
                        'sample_quality': linguistic_dna.confidence_scores.sample_quality_score,
                    },
                    'extraction_timestamp': linguistic_dna.extraction_timestamp.isoformat()
                }
                
                return {
                    "statusCode": 200,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "message": "Linguistic DNA extracted successfully",
                        **result
                    })
                }
        else:
            # API Gateway trigger
            body = json.loads(event.get("body", "{}"))
            job_id = body.get("job_id")
            user_id = body.get("user_id", "anonymous")
            transcript_key = body.get("transcript_key")
            
            if not job_id or not transcript_key:
                return {
                    "statusCode": 400,
                    "headers": {"Content-Type": "application/json"},
                    "body": json.dumps({
                        "error": "Missing required fields: job_id, transcript_key"
                    })
                }
            
            audio_metadata = body.get("audio_metadata", {})
            
            # Extract linguistic DNA
            linguistic_dna = extract_linguistic_dna(
                user_id=user_id,
                job_id=job_id,
                transcript_bucket=bucket_name,
                transcript_key=transcript_key,
                audio_metadata=audio_metadata
            )
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "Linguistic DNA extracted successfully",
                    "job_id": job_id,
                    "user_id": user_id
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
