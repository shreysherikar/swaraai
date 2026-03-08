"""
Create a test style vector in DynamoDB for testing content generation
"""
import boto3
from datetime import datetime, timezone
from decimal import Decimal

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('swara-style-vectors')

# Create test style vector (using Decimal for DynamoDB compatibility)
test_vector = {
    "user_id": "test_user_123",
    "vector_id": "test-vector-001",
    "embeddings": [Decimal('0.5'), Decimal('0.6'), Decimal('0.7'), Decimal('0.8'), Decimal('0.9')],
    "linguistic_features": [
        {
            "feature_name": "speech_rate",
            "feature_value": Decimal('120.0'),
            "importance": Decimal('0.8')
        },
        {
            "feature_name": "cultural_marker_count",
            "feature_value": Decimal('5.0'),
            "importance": Decimal('0.9')
        },
        {
            "feature_name": "pause_frequency",
            "feature_value": Decimal('0.15'),
            "importance": Decimal('0.7')
        }
    ],
    "cultural_context": {
        "primary_language": "Indian English",
        "regional_influences": ["Mumbai", "Delhi"],
        "professional_domain": "Technology"
    },
    "version": 1,
    "created_at": datetime.now(timezone.utc).isoformat(),
    "last_updated": datetime.now(timezone.utc).isoformat(),
    "performance_metrics": {
        "usage_count": 0,
        "average_authenticity_score": Decimal('0.0'),
        "last_used": None
    }
}

# Store in DynamoDB
try:
    response = table.put_item(Item=test_vector)
    print("✅ Test style vector created successfully!")
    print(f"User ID: {test_vector['user_id']}")
    print(f"Vector ID: {test_vector['vector_id']}")
    print(f"Response: {response}")
except Exception as e:
    print(f"❌ Error creating test style vector: {e}")
