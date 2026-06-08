"""
Test script for Google Gemini LLM integration.
Run this to verify that Gemini is properly configured and working.
"""

import sys
from colorama import init, Fore, Style

# Initialize colorama
init()

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{text.center(60)}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")

def print_success(text):
    """Print success message in green."""
    print(f"{Fore.GREEN}✅ {text}{Style.RESET_ALL}")

def print_error(text):
    """Print error message in red."""
    print(f"{Fore.RED}❌ {text}{Style.RESET_ALL}")

def print_warning(text):
    """Print warning message in yellow."""
    print(f"{Fore.YELLOW}⚠️  {text}{Style.RESET_ALL}")

def print_info(text):
    """Print info message in blue."""
    print(f"{Fore.BLUE}ℹ️  {text}{Style.RESET_ALL}")

def test_package_import():
    """Test if google-generativeai package is installed."""
    print_header("Step 1: Checking Package Installation")
    
    try:
        import google.generativeai as genai
        print_success("google-generativeai package is installed")
        return True
    except ImportError:
        print_error("google-generativeai package NOT installed")
        print_info("Install with: pip install google-generativeai")
        return False

def test_api_key_configured():
    """Test if GEMINI_API_KEY is set in environment."""
    print_header("Step 2: Checking API Key Configuration")
    
    from config import get_settings
    settings = get_settings()
    
    if settings.GEMINI_API_KEY:
        # Mask the key for security
        api_key = settings.GEMINI_API_KEY
        masked_key = f"{api_key[:4]}...{api_key[-4:]}" if len(api_key) > 8 else "***"
        print_success(f"GEMINI_API_KEY is configured: {masked_key}")
        print_info(f"Model: {settings.GEMINI_MODEL}")
        print_info(f"Max tokens: {settings.LLM_MAX_TOKENS}")
        print_info(f"Temperature: {settings.LLM_TEMPERATURE}")
        return True
    else:
        print_warning("GEMINI_API_KEY is not set")
        print_info("To get your FREE API key:")
        print_info("  1. Visit: https://makersuite.google.com/app/apikey")
        print_info("  2. Sign in with Google account")
        print_info("  3. Click 'Create API Key'")
        print_info("  4. Copy the key and add it to your .env file")
        print_info("\nExample .env entry:")
        print_info(f'  GEMINI_API_KEY="AIzaSy..."')
        return False

def test_gemini_initialization():
    """Test if Gemini service initializes correctly."""
    print_header("Step 3: Testing Gemini Service Initialization")
    
    from gemini_service import get_gemini_service
    
    service = get_gemini_service()
    
    if service.is_available():
        print_success("Gemini service initialized successfully")
        print_info(f"Using model: {service.settings.GEMINI_MODEL}")
        return True
    else:
        print_warning("Gemini service is NOT available")
        print_info("This could be due to:")
        print_info("  - Missing API key")
        print_info("  - Network connectivity issues")
        print_info("  - Invalid API key")
        return False

def test_reference_generation():
    """Test actual reference answer generation."""
    print_header("Step 4: Testing Reference Answer Generation")
    
    from gemini_service import get_gemini_service
    
    service = get_gemini_service()
    
    if not service.is_available():
        print_warning("Skipping test - Gemini service not available")
        return False
    
    # Test question
    test_question = "Explain the process of photosynthesis in plants"
    
    print_info(f"Generating reference answer for: '{test_question}'")
    print_info("This may take a few seconds...\n")
    
    try:
        answer = service.generate_reference_answer(test_question, max_length=300)
        
        if answer:
            print_success("Reference answer generated successfully!")
            print(f"\n{Fore.MAGENTA}Generated Answer:{Style.RESET_ALL}")
            print(f"{answer}\n")
            print_info(f"Length: {len(answer)} characters")
            return True
        else:
            print_error("Gemini returned an empty answer")
            return False
            
    except Exception as e:
        print_error(f"Error generating reference: {e}")
        return False

def test_answer_evaluation():
    """Test intelligent answer evaluation."""
    print_header("Step 5: Testing Answer Evaluation (Optional)")
    
    from gemini_service import get_gemini_service
    
    service = get_gemini_service()
    
    if not service.is_available():
        print_warning("Skipping test - Gemini service not available")
        return False
    
    # Test data
    question = "What is machine learning?"
    reference = "Machine Learning is a subset of AI that enables systems to learn from data."
    student = "ML is when computers learn from data without programming."
    
    print_info("Evaluating student answer...")
    print_info(f"Question: {question}")
    print_info(f"Student: {student}\n")
    
    try:
        evaluation = service.evaluate_answer_quality(question, reference, student)
        
        if evaluation:
            print_success("Answer evaluation completed!")
            print(f"\n{Fore.MAGENTA}Evaluation Results:{Style.RESET_ALL}")
            print(f"  Coverage: {evaluation.get('coverage_score', 'N/A')}/100")
            print(f"  Accuracy: {evaluation.get('accuracy_score', 'N/A')}/100")
            print(f"  Overall Score: {evaluation.get('overall_score', 'N/A')}/100")
            
            if 'feedback' in evaluation:
                print(f"\n{Fore.MAGENTA}Feedback:{Style.RESET_ALL}")
                print(f"  {evaluation.get('feedback', 'N/A')}\n")
            
            return True
        else:
            print_warning("Gemini returned empty evaluation")
            return False
            
    except Exception as e:
        print_error(f"Error during evaluation: {e}")
        return False

def test_fallback_mechanism():
    """Test that fallback to heuristic method works."""
    print_header("Step 6: Testing Fallback Mechanism")
    
    from auto_ref_generator import get_reference_generator
    
    generator = get_reference_generator()
    
    test_question = "Describe the water cycle"
    
    print_info(f"Testing with question: '{test_question}'")
    print_info("(Will use LLM if available, otherwise heuristic fallback)\n")
    
    try:
        result = generator.generate_reference_answer(test_question, max_length=200)
        
        if result:
            print_success(f"Reference generated (confidence: {result.confidence:.2f})")
            print(f"\n{Fore.MAGENTA}Generated Reference:{Style.RESET_ALL}")
            print(f"{result.generated_answer}\n")
            return True
        else:
            print_error("Failed to generate reference")
            return False
            
    except Exception as e:
        print_error(f"Error in fallback test: {e}")
        return False

def main():
    """Run all tests."""
    print_header("🧪 Gemini LLM Integration Test Suite")
    
    results = []
    
    # Run tests
    results.append(("Package Installation", test_package_import()))
    results.append(("API Key Configuration", test_api_key_configured()))
    results.append(("Service Initialization", test_gemini_initialization()))
    results.append(("Reference Generation", test_reference_generation()))
    results.append(("Answer Evaluation", test_answer_evaluation()))
    results.append(("Fallback Mechanism", test_fallback_mechanism()))
    
    # Summary
    print_header("📊 Test Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Fore.GREEN}PASS{Style.RESET_ALL}" if result else f"{Fore.RED}FAIL{Style.RESET_ALL}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Fore.CYAN}Results: {passed}/{total} tests passed{Style.RESET_ALL}")
    
    if passed == total:
        print_success("🎉 All tests passed! Gemini integration is working perfectly!")
    elif passed >= total // 2:
        print_warning("⚠️  Some tests passed. System will work with limited LLM features.")
    else:
        print_error("❌ Most tests failed. Please check configuration and try again.")
    
    print(f"\n{Fore.CYAN}Next Steps:{Style.RESET_ALL}")
    print("  1. If API key missing: Get free key from https://makersuite.google.com/app/apikey")
    print("  2. Add GEMINI_API_KEY to your .env file")
    print("  3. Restart the backend server")
    print("  4. Run this test again to verify")
    print("\n  For detailed setup instructions, see: GEMINI_SETUP_GUIDE.md\n")
    
    sys.exit(0 if passed == total else 1)

if __name__ == "__main__":
    main()
