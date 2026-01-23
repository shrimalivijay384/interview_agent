"""
Demo script to test KPI determination with Gemini API.
"""
import asyncio
import json
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/labuser/interview_agent/interview_agent/backend')

from app.services.kpi_determiner_db import get_kpi_determiner
from database import get_db_stats, list_all_jds, list_all_candidates


async def test_kpi_determination():
    """Test the KPI determination feature."""
    
    print("\n" + "="*80)
    print("KPI DETERMINATION TEST")
    print("="*80 + "\n")
    
    # Check database
    print("1. Checking database...")
    stats = get_db_stats()
    print(f"   Total JDs: {stats['total_jds']}")
    print(f"   Total Candidates: {stats['total_candidates']}")
    print(f"   Database: {stats['db_path']}\n")
    
    if stats['total_jds'] == 0 or stats['total_candidates'] == 0:
        print("❌ Database is empty. Run database/init_db.py first.")
        return
    
    # List available data
    print("2. Available Job Descriptions:")
    jds = list_all_jds()
    for jd in jds:
        print(f"   ID: {jd['id']} | {jd['content'].get('job_title')} @ {jd['content'].get('company')}")
    
    print("\n3. Available Candidates:")
    candidates = list_all_candidates()
    for candidate in candidates:
        print(f"   ID: {candidate['id']} | {candidate['name']} ({candidate['email']})")
    
    # Test KPI determination
    print("\n4. Testing KPI Determination...")
    print("-" * 80)
    
    try:
        jd_id = 1
        candidate_id = 1
        
        print(f"\n   Determining KPIs for:")
        print(f"   - Job Description ID: {jd_id}")
        print(f"   - Candidate ID: {candidate_id}")
        print(f"\n   Calling Gemini API... (this may take a moment)")
        
        kpi_determiner = get_kpi_determiner()
        result = await kpi_determiner.determine_kpis_from_db(
            jd_id=jd_id,
            candidate_id=candidate_id
        )
        
        # Display results
        print(kpi_determiner.format_kpis_for_display(result))
        
        # Save results to file
        output_file = "/tmp/kpi_determination_result.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\n✅ Results saved to: {output_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_all_combinations():
    """Test KPI determination for all candidate-JD combinations."""
    
    print("\n" + "="*80)
    print("COMPREHENSIVE KPI DETERMINATION TEST")
    print("="*80 + "\n")
    
    stats = get_db_stats()
    
    if stats['total_jds'] == 0 or stats['total_candidates'] == 0:
        print("❌ Database is empty.")
        return
    
    kpi_determiner = get_kpi_determiner()
    
    print(f"Testing {stats['total_jds']} JD(s) × {stats['total_candidates']} Candidate(s) = {stats['total_jds'] * stats['total_candidates']} combinations\n")
    
    for jd_id in range(1, stats['total_jds'] + 1):
        for candidate_id in range(1, stats['total_candidates'] + 1):
            try:
                print(f"Testing JD {jd_id} × Candidate {candidate_id}...", end=" ")
                result = await kpi_determiner.determine_kpis_from_db(
                    jd_id=jd_id,
                    candidate_id=candidate_id
                )
                print(f"✅ ({len(result['kpis'])} KPIs determined)")
                
            except Exception as e:
                print(f"❌ Error: {str(e)[:50]}...")


if __name__ == "__main__":
    import dotenv
    
    # Load environment variables
    dotenv_path = '/home/labuser/interview_agent/interview_agent/backend/.env'
    if os.path.exists(dotenv_path):
        dotenv.load_dotenv(dotenv_path)
        print(f"✓ Loaded environment from {dotenv_path}")
    else:
        print(f"⚠ Environment file not found at {dotenv_path}")
        print("  Make sure GEMINI_API_KEY is set in environment variables")
    
    # Run tests
    print("\nRunning basic KPI determination test...\n")
    result = asyncio.run(test_kpi_determination())
    
    if result:
        print("\n" + "="*80)
        print("Would you like to test all combinations? (This will make multiple API calls)")
        print("="*80)
