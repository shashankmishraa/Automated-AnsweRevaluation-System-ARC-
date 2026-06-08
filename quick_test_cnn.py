"""Quick test to verify CNN integration"""
print("Testing CNN Integration...")
print("=" * 50)

try:
    from models import get_model_manager
    print("✓ Importing models module... SUCCESS")
    
    mm = get_model_manager()
    print("✓ Loading model manager... SUCCESS")
    
    print(f"\nModel Status:")
    print(f"  CNN Model: {'✓ Loaded' if mm.cnn_model is not None else '✗ Not Loaded'}")
    print(f"  Tokenizer: {'✓ Loaded' if mm.tokenizer is not None else '✗ Not Loaded'}")
    print(f"  Sentence Transformers: {len(mm.sentence_transformers)} loaded")
    
    # Test CNN scoring
    if mm.cnn_model and mm.tokenizer:
        print("\n✓ Testing CNN scoring...")
        test_ref = "This is a reference answer for testing purposes."
        test_student = "This is a student answer that should be similar."
        
        try:
            cnn_score = mm.compute_cnn_score(test_ref, test_student)
            print(f"  CNN Score: {cnn_score}")
            
            hybrid_score = mm.compute_hybrid_score(test_ref, test_student)
            print(f"  Hybrid Score: {hybrid_score}")
            
            transformer_score = mm.compute_similarity(test_ref, test_student)
            print(f"  Transformer Score: {transformer_score}")
            
            print("\n✅ ALL TESTS PASSED!")
            
        except Exception as e:
            print(f"  ✗ Scoring failed: {e}")
    else:
        print("\n⚠️  CNN or Tokenizer not loaded - skipping scoring tests")
        
except Exception as e:
    print(f"✗ FAILED: {e}")
    import traceback
    traceback.print_exc()

print("=" * 50)
