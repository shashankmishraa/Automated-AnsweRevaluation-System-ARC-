"""Direct test of Gemini service with correct model."""
import os
from dotenv import load_dotenv

load_dotenv()

print("Testing Gemini Service...")
print("=" * 50)

# Check .env
api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "Not set")

print(f"API Key: {'✓ Set' if api_key else '✗ Missing'}")
print(f"Model: {model_name}")

if not api_key:
    print("\n❌ Please add your API key to .env file")
    exit(1)

# Import and test
from gemini_service import get_gemini_service

print("\nInitializing Gemini service...")
service = get_gemini_service()

if service.is_available():
    print("✓ Gemini service initialized successfully")
    print(f"✓ Using model: {service.settings.GEMINI_MODEL}")
    
    # Test answer evaluation
    print("\n🔄 Testing answer evaluation...")
    result = service.evaluate_answer_quality(
        question="What is machine learning?",
        reference_answer="Machine Learning is a subset of AI that enables systems to learn from data.",
        student_answer="ML is when computers learn from data without explicit programming."
    )
    
    if result:
        print("\n✓ Evaluation successful!")
        print(f"Coverage Score: {result.get('coverage_score', 'N/A')}/100")
        print(f"Accuracy Score: {result.get('accuracy_score', 'N/A')}/100")
        print(f"Overall Score: {result.get('overall_score', 'N/A')}/100")
        print(f"\nFeedback: {result.get('feedback', 'N/A')[:200]}...")
    else:
        print("\n✗ Evaluation failed")
else:
    print("✗ Gemini service not available")
    print("Check your API key and model name in .env")