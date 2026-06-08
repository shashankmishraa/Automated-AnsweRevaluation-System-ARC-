"""
Test script for demo mode OCR and batch endpoints.
Verifies that preset data is returned correctly.
"""

import requests
import json


BASE_URL = "http://localhost:8000"


def test_ocr_demo(subject="general"):
    """Test OCR demo endpoint."""
    print(f"\n{'='*70}")
    print(f"🧪 Testing OCR Demo - Subject: {subject.upper()}")
    print('='*70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/evaluate/ocr-demo",
            data={"subject": subject}
        )
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS!")
            print(f"\n📊 Results:")
            print(f"  Question: {data['question'][:80]}...")
            print(f"  Final Score: {data['final_score']}/10")
            print(f"  Grade: {data['grade']}")
            print(f"  Percentage: {data['percentage']}%")
            
            print(f"\n📈 Detailed Scores:")
            print(f"  Similarity: {data['similarity']*100:.1f}%")
            print(f"  Coverage: {data['coverage']*100:.1f}%")
            print(f"  Grammar: {data['grammar']*100:.1f}%")
            print(f"  Relevance: {data['relevance']*100:.1f}%")
            
            print(f"\n💬 Feedback:")
            print(f"  {data['feedback'][:150]}...")
            
            if 'gap_analysis' in data:
                gap = data['gap_analysis']
                print(f"\n🎯 Gap Analysis:")
                print(f"  Matched Concepts: {len(gap.get('matched', []))}")
                print(f"  Missing Concepts: {len(gap.get('missing', []))}")
                print(f"  Coverage: {gap.get('coverage_percentage', 0):.1f}%")
            
            print(f"\n✨ Demo Mode: {data.get('demo_mode', False)}")
            
            return True
        else:
            print(f"\n❌ FAILED - Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def test_batch_demo():
    """Test batch demo endpoint."""
    print(f"\n{'='*70}")
    print("🧪 Testing Batch Demo Evaluation")
    print('='*70)
    
    try:
        response = requests.post(f"{BASE_URL}/evaluate/batch-demo")
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"\n✅ SUCCESS!")
            
            print(f"\n📊 Overall Statistics:")
            print(f"  Exam: {data['exam_name']}")
            print(f"  Total Students: {data['total_students']}")
            print(f"  Class Average: {data['average_score']}/10 ({data['average_percentage']}%)")
            print(f"  Class Grade: {data['class_grade']}")
            print(f"  Highest Score: {data['highest_score']}/10")
            print(f"  Lowest Score: {data['lowest_score']}/10")
            
            print(f"\n👥 Student Results:")
            for student in data['results']:
                print(f"\n  {student['student_name']}:")
                print(f"    Score: {student['final_score']}/10")
                print(f"    Grade: {student['grade']}")
                print(f"    Feedback: {student['feedback'][:60]}...")
            
            if 'statistics' in data:
                stats = data['statistics']
                print(f"\n📈 Class Analytics:")
                print(f"  Pass Rate: {stats.get('pass_rate', 0):.1f}%")
                print(f"  Excellence Rate: {stats.get('excellence_rate', 0):.1f}%")
                
                if 'grade_distribution' in stats:
                    dist = stats['grade_distribution']
                    print(f"  Grade Distribution:")
                    for grade, count in dist.items():
                        if count > 0:
                            print(f"    {grade}: {count} student(s)")
            
            print(f"\n✨ Demo Mode: {data.get('demo_mode', False)}")
            
            return True
        else:
            print(f"\n❌ FAILED - Status Code: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False


def main():
    """Run all demo mode tests."""
    print("\n" + "="*70)
    print("🎭 DEMO MODE TEST SUITE")
    print("="*70)
    
    # Test OCR demos for all subjects
    subjects = ["general", "physics", "history", "computer_science"]
    
    ocr_results = {}
    for subject in subjects:
        success = test_ocr_demo(subject)
        ocr_results[subject] = success
    
    # Test batch demo
    batch_success = test_batch_demo()
    
    # Summary
    print(f"\n{'='*70}")
    print("📊 TEST SUMMARY")
    print('='*70)
    
    print(f"\nOCR Demo Tests:")
    for subject, success in ocr_results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {subject.title():20} {status}")
    
    print(f"\nBatch Demo Test:")
    print(f"  {'Batch Evaluation':20} {'✅ PASS' if batch_success else '❌ FAIL'}")
    
    total_tests = len(ocr_results) + 1
    passed = sum(ocr_results.values()) + (1 if batch_success else 0)
    
    print(f"\nOverall: {passed}/{total_tests} tests passed")
    
    if passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! Demo mode is working perfectly!")
    else:
        print("\n⚠️  Some tests failed. Make sure the backend server is running.")
    
    print("="*70)


if __name__ == "__main__":
    # Check if backend is running
    print("\n🔍 Checking if backend server is running...")
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=2)
        if health_check.status_code == 200:
            print("✅ Backend server is healthy!")
            main()
        else:
            print("❌ Backend server returned unhealthy status")
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend server!")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nOr:")
        print("  uvicorn main:app --reload")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
