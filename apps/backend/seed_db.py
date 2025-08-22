"""
Database seeding script for Briefcase application.
Creates test users for development and demonstration.
"""
import sys
from pathlib import Path

# Add parent directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent))

from app.core.database import engine, SessionLocal, Base
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy.orm import Session


def create_test_users(db: Session):
    """Create test users for development."""
    
    test_users = [
        {
            "email": "alice@briefcase.com",
            "password": "alicepass123",
            "is_active": True,
            "description": "Alice - Senior Manager (can share documents)"
        },
        {
            "email": "bob@briefcase.com", 
            "password": "bobpass123",
            "is_active": True,
            "description": "Bob - Team Lead (regular user)"
        },
        {
            "email": "charlie@briefcase.com",
            "password": "charliepass123", 
            "is_active": True,
            "description": "Charlie - Developer (regular user)"
        },
        {
            "email": "inactive@briefcase.com",
            "password": "inactivepass123",
            "is_active": False,
            "description": "Inactive User (for testing inactive account handling)"
        }
    ]
    
    for user_data in test_users:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        
        if existing_user:
            print(f"User {user_data['email']} already exists - skipping")
            continue
        
        # Create new user
        user = User(
            email=user_data["email"],
            password_hash=get_password_hash(user_data["password"]),
            is_active=user_data["is_active"]
        )
        
        db.add(user)
        print(f"Created user: {user_data['email']} - {user_data['description']}")
    
    db.commit()
    print("\nTest users created successfully!")
    print("\nYou can log in with these credentials:")
    for user_data in test_users:
        if user_data["is_active"]:
            print(f"  Email: {user_data['email']}, Password: {user_data['password']}")


def seed_database():
    """Main function to seed the database."""
    print("Starting database seeding...")
    
    # Create all tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = SessionLocal()
    
    try:
        create_test_users(db)
        print("\nDatabase seeding completed successfully!")
    except Exception as e:
        print(f"Error during database seeding: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()