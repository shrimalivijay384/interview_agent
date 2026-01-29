"""
Initialize database and load mock data.
"""
from app.database import engine, Base, SessionLocal
from app.services.db_service import DatabaseService


def init_database():
    """Create all tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


def load_mock_data():
    """Load mock JD and Resume."""
    db = SessionLocal()
    try:
        print("\nLoading mock data...")
        
        # Load Job Description
        jd = DatabaseService.load_mock_jd(db, "data/mock_jd.json")
        print(f"✓ Loaded Job Description: {jd.job_title} at {jd.company}")
        
        # Load Resume
        resume = DatabaseService.load_mock_resume(db, "data/mock_cv.json")
        print(f"✓ Loaded Resume: {resume.name}")
        
        print(f"\nMock data loaded successfully!")
        print(f"JD ID: {jd.id}, Resume ID: {resume.id}")
        
    except Exception as e:
        print(f"✗ Error loading mock data: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    load_mock_data()