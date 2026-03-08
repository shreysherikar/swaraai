"""
Test All API Endpoints
Comprehensive test of all API endpoints with proper error handling
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
print("SWARA AI - API ENDPOINT TESTS")
print("=" * 80)

# Test 1: Profile Endpoint
print("\n👤 Test 1: GET /profile")
print("-" * 80)

try:
    response = requests.get(
        f"{API_URL}/profile",
        headers=headers,
        params={"user_id": "test_user_123"},
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text[:200]}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"User ID: {data.get('userId')}")
        print(f"Confidence: {data.get('confidence')}")
        print(f"Last Calibrated: {data.get('lastCalibrated')}")
    elif response.status_code == 404:
        print("⚠️  Profile not found (expected if not calibrated)")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Content Generation
print("\n\n📝 Test 2: POST /content/generate")
print("-" * 80)

payload = {
    "user_id": "test_user_123",
    "prompt": "Write a professional email about project updates",
    "content_type": "email"
}

try:
    response = requests.post(
        f"{API_URL}/content/generate",
        headers=headers,
        json=payload,
        timeout=30
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ SUCCESS!")
        print(f"\n📊 Authenticity Score: {data.get('authenticity_score')}")
        print(f"🎯 Cultural Markers: {len(data.get('cultural_markers', []))}")
        print(f"\n📝 Generated Content (first 150 chars):")
        print(data.get('generated_text', '')[:150] + "...")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: CORS Headers
print("\n\n🌐 Test 3: CORS Headers Check")
print("-" * 80)

try:
    response = requests.options(
        f"{API_URL}/content/generate",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type,X-Api-Key"
        },
        timeout=10
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"CORS Headers:")
    for header, value in response.headers.items():
        if "access-control" in header.lower():
            print(f"  {header}: {value}")
    
    if "access-control-allow-origin" in [h.lower() for h in response.headers.keys()]:
        print("✅ CORS headers present")
    else:
        print("⚠️  CORS headers may be missing")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 4: Error Handling
print("\n\n🔍 Test 4: Error Handling (Non-existent User)")
print("-" * 80)

payload = {
    "user_id": "non_existent_user_xyz",
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
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 500:
        data = response.json()
        if "Style vector not found" in data.get('error', ''):
            print("✅ SUCCESS! Error handling works correctly")
            print(f"Error message: {data['error']}")
        else:
            print(f"⚠️  Unexpected error: {data.get('error')}")
    else:
        print(f"⚠️  Unexpected status: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "=" * 80)
print("API ENDPOINT TESTS COMPLETE")
print("=" * 80)
