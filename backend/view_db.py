"""
Script to view database contents for verification.
"""
import json
from database import list_all_jds, list_all_candidates


def display_jds():
    """Display all job descriptions."""
    print("\n" + "="*80)
    print("JOB DESCRIPTIONS IN DATABASE")
    print("="*80)
    
    jds = list_all_jds()
    for jd in jds:
        print(f"\nID: {jd['id']}")
        print(f"Title: {jd['title']}")
        print(f"Company: {jd['company']}")
        print(f"Created: {jd['created_at']}")
        print("\nContent:")
        print(json.dumps(jd['content'], indent=2))


def display_candidates():
    """Display all candidates."""
    print("\n" + "="*80)
    print("CANDIDATES IN DATABASE")
    print("="*80)
    
    candidates = list_all_candidates()
    for candidate in candidates:
        print(f"\nID: {candidate['id']}")
        print(f"Name: {candidate['name']}")
        print(f"Email: {candidate['email']}")
        print(f"Created: {candidate['created_at']}")
        print("\nContent Summary:")
        content = candidate['content']
        print(f"  Summary: {content.get('summary', 'N/A')}")
        print(f"  Skills: {', '.join(content.get('skills', [])[:5])}...")
        print(f"  Experience: {len(content.get('experience', []))} positions")


if __name__ == "__main__":
    display_jds()
    display_candidates()
    print("\n" + "="*80 + "\n")
