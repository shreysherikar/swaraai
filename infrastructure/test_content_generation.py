"""
Test content generation Lambda with the test style vector
"""
import boto3
import json

# Initialize Lambda client
lambda_client = boto3.client('lambda', region_name='us-east-1')

# Test payload
test_payload = {
    "body": json.dumps({
        "user_id": "test_user_123",
        "prompt": "Write a LinkedIn post about my experience with AI and machine learning in the Indian tech industry",
        "content_type": "linkedin_post"
    })
}

# Invoke Lambda function
print("🚀 Invoking ContentGenerator Lambda...")
response = lambda_client.invoke(
    FunctionName='SwaraAIIdentityLayer-ContentGenerator08D4D895-pNoTOzCykcRH',
    InvocationType='RequestResponse',
    Payload=json.dumps(test_payload)
)

# Parse response
response_payload = json.loads(response['Payload'].read())
print("\n📊 Lambda Response:")
print(json.dumps(response_payload, indent=2))

# Parse the body if it exists
if 'body' in response_payload:
    body = json.loads(response_payload['body'])
    print("\n✅ Generated Content:")
    print("=" * 80)
    if 'generated_text' in body:
        print(body['generated_text'])
        print("=" * 80)
        print(f"\n📈 Authenticity Score: {body.get('authenticity_score', 'N/A')}")
        print(f"🎯 Cultural Markers Found: {len(body.get('cultural_markers', []))}")
    else:
        print("❌ Error:", body.get('error', 'Unknown error'))
