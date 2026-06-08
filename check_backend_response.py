"""Test script to check if backend returns reference answers and CNN scores"""
import requests
import json

API_BASE = 'http://localhost:8000'

# Test data
test_data = {
    "question": "What is photosynthesis?",
    "reference_answer": "Photosynthesis is the process by which plants convert light energy into chemical energy.",
    "student_answer": "Plants make food using sunlight through photosynthesis."
}

print("Testing Backend Response...")
print("=" * 60)

# Test 1: Regular evaluation (without CNN)
print("\n1. Testing POST /evaluate (no CNN)...")
try:
    response = requests.post(f"{API_BASE}/evaluate", json=test_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nResponse keys:", list(result.keys()))
        print(f"\nQuestion present: {'question' in result}")
        print(f"Reference Answer present: {'referenceAnswer' in result}")
        print(f"Student Answer present: {'student_answer' in result}")
        
        if 'referenceAnswer' in result:
            print(f"\n✅ Reference Answer IS being returned!")
            print(f"Preview: {result['referenceAnswer'][:100]}...")
        else:
            print(f"\n❌ Reference Answer NOT in response!")
            
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")

# Test 2: With CNN enabled
print("\n2. Testing POST /evaluate?use_cnn=true...")
try:
    response = requests.post(f"{API_BASE}/evaluate?use_cnn=true", json=test_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\nResponse keys:", list(result.keys()))
        
        # Check for CNN score
        if 'cnn_score' in result:
            print(f"\n✅ CNN Score IS being returned: {result['cnn_score']}")
        elif 'metrics' in result and 'cnn_score' in result['metrics']:
            print(f"\n✅ CNN Score in metrics: {result['metrics']['cnn_score']}")
        else:
            print(f"\n❌ CNN Score NOT in response!")
            
        # Print full response structure
        print("\nFull response structure:")
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Error: {response.text}")
        
except Exception as e:
    print(f"Request failed: {e}")

print("\n" + "=" * 60)
print("Test complete!")
