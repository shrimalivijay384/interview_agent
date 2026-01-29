#!/usr/bin/env python3
"""
Quick test script for Interview Agent System
Tests the KPI Extractor Agent standalone
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_kpi_extraction():
    """Test KPI extraction from job description"""
    print("=" * 70)
    print("TESTING KPI EXTRACTOR AGENT")
    print("=" * 70)
    
    # Sample job description
    jd_text = """
    Senior Full Stack Developer
    
    We are seeking an experienced Senior Full Stack Developer to join our team.
    
    Requirements:
    - 5+ years of experience with React and Node.js
    - Strong understanding of system design and architecture
    - Experience with AWS cloud services
    - Excellent communication and teamwork skills
    - Bachelor's degree in Computer Science or related field
    
    Responsibilities:
    - Design and implement scalable web applications
    - Lead technical discussions and code reviews
    - Mentor junior developers
    - Collaborate with product team on feature development
    """
    
    resume_context = {
        "years_of_experience": 7,
        "skills": ["React", "Node.js", "Python", "AWS"],
        "name": "John Doe"
    }
    
    print("\n📋 Job Description:")
    print(jd_text[:200] + "...")
    print("\n🔍 Extracting KPIs...\n")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/unified-interview/kpi-extraction/extract",
            json={
                "jd_text": jd_text,
                "resume_context": resume_context
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ KPI Extraction Successful!\n")
            print(f"📊 Extracted {len(result['kpis'])} KPIs:\n")
            
            for i, kpi in enumerate(result['kpis'], 1):
                print(f"{i}. {kpi['name']}")
                print(f"   Weight: {kpi['weight']:.2f}")
                print(f"   Category: {kpi['category']}")
                print(f"   Expected Level: {kpi['expected_level']}")
                print(f"   Description: {kpi['description'][:100]}...")
                print()
            
            print(f"💡 Extraction Reasoning:")
            print(f"   {result.get('extraction_reasoning', 'N/A')[:200]}...")
            print()
            
            print(f"🎯 Focus Areas: {', '.join(result.get('focus_areas', []))}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {str(e)}")
        return False


def test_health():
    """Test if server is running"""
    print("\n" + "=" * 70)
    print("TESTING SERVER HEALTH")
    print("=" * 70 + "\n")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Server Status: {data['status']}")
            print(f"⏰ Timestamp: {data['timestamp']}")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to server: {str(e)}")
        print(f"\nMake sure the server is running:")
        print(f"  cd backend && ./start_server.sh")
        return False


if __name__ == "__main__":
    print("\n" + "🎯" * 35)
    print("INTERVIEW AGENT SYSTEM - QUICK TEST")
    print("🎯" * 35 + "\n")
    
    # Test server health
    if not test_health():
        print("\n❌ Server is not running. Please start it first.")
        exit(1)
    
    # Test KPI extraction
    print("\n")
    success = test_kpi_extraction()
    
    print("\n" + "=" * 70)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n📚 Next steps:")
        print("  1. Visit http://localhost:8000/docs for full API documentation")
        print("  2. Test other agents: Greeting, Profile Validator, Project Analyzer")
        print("  3. Try the unified interview flow")
    else:
        print("❌ TESTS FAILED")
    print("=" * 70 + "\n")
