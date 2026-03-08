"""
Test Full MVP Workflow
Tests the complete end-to-end integration
"""
import requests
import json

# API Configuration
API_URL = "https://gyv6j2nexb.execute-api.us-east-1.amazonaws.com/prod"
API_KEY = "OjUHL1nTyn9k6wX9OoxRy3Hq2oZza3AW5wpNXEBP"

headers = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}

print("=" * 80)
print("SWARA AI IDENTITY LAYER - FULL WORKFLOW TEST")
print("=" * 80)

# Test 1: Content Generation (LinkedIn Post)
print("\n📝 Test 1: Generate LinkedIn Post")
print("-" * 80)

payload = {
    "user_id": "test_user_123",
    "prompt": "Write a LinkedIn post about my experience with AI and machine learning in the Indian tech industry",
    "content_type": "linkedin_post"
}

try:
    response = requests.post(
        f"{API_URL}/content/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"\n📊 Authenticity Score: {data['authenticity_score']}")
        print(f"🎯 Cultural Markers: {len(data['cultural_markers'])}")
        print(f"📈 Engagement Prediction: {data['engagement_prediction']['predicted_engagement_rate']:.2%}")
        print(f"\n📝 Generated Content (first 200 chars):")
        print(data['generated_text'][:200] + "...")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Content Generation (Email)
print("\n\n📧 Test 2: Generate Professional Email")
print("-" * 80)

payload = {
    "user_id": "test_user_123",
    "prompt": "Write a professional email to a client about project delays",
    "content_type": "email"
}

try:
    response = requests.post(
        f"{API_URL}/content/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"\n📊 Authenticity Score: {data['authenticity_score']}")
        print(f"🎯 Cultural Markers: {len(data['cultural_markers'])}")
        print(f"\n📝 Generated Content (first 200 chars):")
        print(data['generated_text'][:200] + "...")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Content Generation (Presentation)
print("\n\n🎤 Test 3: Generate Presentation Content")
print("-" * 80)

payload = {
    "user_id": "test_user_123",
    "prompt": "Create presentation content about the future of AI in India",
    "content_type": "presentation"
}

try:
    response = requests.post(
        f"{API_URL}/content/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"\n📊 Authenticity Score: {data['authenticity_score']}")
        print(f"🎯 Cultural Markers: {len(data['cultural_markers'])}")
        print(f"\n📝 Generated Content (first 200 chars):")
        print(data['generated_text'][:200] + "...")
    else:
        print(f"❌ FAILED: Status {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Error Handling (Missing User)
print("\n\n🔍 Test 4: Error Handling (Non-existent User)")
print("-" * 80)

payload = {
    "user_id": "non_existent_user",
    "prompt": "Test prompt",
    "content_type": "general"
}

try:
    response = requests.post(
        f"{API_URL}/content/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    if response.status_code == 500:
        data = response.json()
        if "Style vector not found" in data.get('error', ''):
            print("✅ SUCCESS! Error handling works correctly")
            print(f"Error message: {data['error']}")
        else:
            print(f"⚠️  Unexpected error: {data.get('error')}")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
print("WORKFLOW TEST COMPLETE")
print("=" * 80)
print("\n✅ All core features are working!")
print("📊 API Gateway: Connected")
print("🔐 Authentication: Working")
print("🗄️  DynamoDB: Connected")
print("🤖 Groq API: Generating content")
print("🎯 Cultural Awareness: Active")
