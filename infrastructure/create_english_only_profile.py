"""
Create English-only test style vector (no Hindi/Hinglish)
For users who speak pure English without code-mixing
"""
import boto3
from decimal import Decimal
from datetime import datetime

# DynamoDB client
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('swara-style-vectors')

print("Creating English-only style vector for test_user_123...")

# English-only style vector (no Hindi/Hinglish)
style_vector = {
    "user_id": "test_user_123",
    "prosody_features": {
        "speech_rate": Decimal("145"),  # Words per minute
        "pause_patterns": "moderate",
        "tonal_variation": "medium",
        "pitch_range": Decimal("150.5"),
        "energy_level": Decimal("0.75")
    },
    "cultural_context": {
        "regional_influences": [
            "professional",
            "tech-savvy",
            "enthusiastic",
            "collaborative",
            "clear communicator"
        ],
        "code_mixing_patterns": [
            "excited",
            "thrilled",
            "fantastic",
            "absolutely",
            "looking forward"
        ],
        "formality_level": Decimal("0.7"),
        "cultural_markers": []  # No Hindi markers
    },
    "confidence": Decimal("0.90"),
    "created_at": datetime.now().isoformat(),
    "last_updated": datetime.now().isoformat(),
    "sample_count": 5,
    "version": "1.0"
}

try:
    # Put item in DynamoDB
    table.put_item(Item=style_vector)
    print("✅ English-only style vector created successfully!")
    print(f"User ID: test_user_123")
    print(f"Speech Rate: {style_vector['prosody_features']['speech_rate']} wpm")
    print(f"Confidence: {style_vector['confidence']}")
    print(f"Regional Influences: {', '.join(style_vector['cultural_context']['regional_influences'])}")
    print(f"Common Expressions: {', '.join(style_vector['cultural_context']['code_mixing_patterns'])}")
    print("\n✅ No Hindi/Hinglish markers included")
    print("\nNow try generating content again!")
    
except Exception as e:
    print(f"❌ Error: {e}")
