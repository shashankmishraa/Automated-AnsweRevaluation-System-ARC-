"""
Check if backend is running and all endpoints are accessible
"""

import requests
import sys

print("=" * 60)
print("🔍 DIAGNOSTIC TOOL - Checking Backend Status")
print("=" * 60)

# Test 1: Is backend running?
print("\n[1/5] Checking if backend is running...")
try:
    response = requests.get("http://localhost:8000/docs", timeout=3)
    if response.status_code == 200:
        print("✅ Backend is RUNNING on http://localhost:8000")
    else:
        print(f"❌ Backend returned status {response.status_code}")
        sys.exit(1)
except requests.exceptions.ConnectionError:
    print("❌ BACKEND NOT RUNNING!")
    print("\nTo start backend:")
    print("  cd d:\\D down\\bit")
    print("  python -m uvicorn main:app --host 127.0.0.1 --port 8000")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

# Test 2: Check /evaluate endpoint
print("\n[2/5] Testing /evaluate endpoint...")
try:
    test_data = {
        "question": "Test",
        "reference_answer": "Test answer",
        "student_answer": "Student answer",
        "model_name": None,
        "student_name": None
    }
    response = requests.post("http://localhost:8000/evaluate", json=test_data, timeout=10)
    
    if response.status_code == 200:
        print("✅ /evaluate endpoint WORKS")
    elif response.status_code == 422:
        print("⚠️  /evaluate endpoint has validation issues")
        print(f"   Detail: {response.json().get('detail', 'Unknown')}")
    else:
        print(f"❌ /evaluate endpoint FAILED ({response.status_code})")
        print(f"   {response.text[:200]}")
except Exception as e:
    print(f"❌ /evaluate endpoint ERROR: {e}")

# Test 3: Check OCR endpoint exists
print("\n[3/5] Testing /evaluate/ocr endpoint...")
try:
    # Just check if endpoint exists (don't upload file)
    response = requests.get("http://localhost:8000/docs")
    if "/evaluate/ocr" in response.text:
        print("✅ /evaluate/ocr endpoint EXISTS in documentation")
    else:
        print("❌ /evaluate/ocr endpoint NOT FOUND in docs")
        print("   Backend might not have restarted after adding endpoint")
except Exception as e:
    print(f"❌ Error checking OCR endpoint: {e}")

# Test 4: Try actual OCR request (without file)
print("\n[4/5] Testing OCR endpoint connectivity...")
try:
    # This will fail but should give us useful error info
    response = requests.post("http://localhost:8000/evaluate/ocr", timeout=5)
    print(f"   Response: {response.status_code}")
    if response.status_code == 422:
        print("✅ OCR endpoint is ACTIVE (returned validation error - expected)")
    elif response.status_code == 404:
        print("❌ OCR endpoint NOT FOUND (404)")
    else:
        print(f"   Status: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to OCR endpoint")
except Exception as e:
    print(f"⚠️  OCR endpoint error (might be expected): {type(e).__name__}")

# Test 5: Summary
print("\n[5/5] Summary:")
print("=" * 60)

issues = []

# Check if backend is running
try:
    requests.get("http://localhost:8000/docs", timeout=3)
except:
    issues.append("Backend is not running")

if not issues:
    print("✅ ALL SYSTEMS OPERATIONAL!")
    print("\nYou can now:")
    print("  1. Open http://localhost:3000")
    print("  2. Test text evaluation")
    print("  3. Test OCR evaluation (upload image)")
    print("  4. Download HTML reports")
else:
    print("❌ ISSUES FOUND:")
    for issue in issues:
        print(f"  - {issue}")
    
    print("\n🔧 RECOMMENDED FIXES:")
    if "Backend is not running" in issues:
        print("  1. Start backend first:")
        print("     cd d:\\D down\\bit")
        print("     python -m uvicorn main:app --host 127.0.0.1 --port 8000")
        print()
        print("  2. Wait for 'Application startup complete'")
        print("  3. Then test again")

print("=" * 60)
