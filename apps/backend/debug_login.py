"""
Debug script to test login functionality directly.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal
from app.models.user import User
from app.core.security import verify_password, get_password_hash

def test_login_logic():
    """Test the login logic step by step."""
    print("Testing login logic...")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Test data
        email = "alice@briefcase.com"
        password = "alicepass123"
        
        print(f"1. Looking for user with email: {email}")
        
        # Find user by email
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print("[ERROR] User not found")
            return
        
        print(f"[OK] User found: ID={user.id}, Email={user.email}, Active={user.is_active}")
        print(f"   Password hash: {user.password_hash[:50]}...")
        
        print(f"2. Verifying password: {password}")
        
        # Test password verification
        try:
            is_valid = verify_password(password, user.password_hash)
            print(f"[OK] Password verification result: {is_valid}")
        except Exception as e:
            print(f"[ERROR] Password verification failed: {e}")
            import traceback
            traceback.print_exc()
            return
        
        if not is_valid:
            print("[ERROR] Password is incorrect")
            return
        
        print(f"3. Checking if user is active: {user.is_active}")
        
        if not user.is_active:
            print("[ERROR] User is not active")
            return
        
        print("[OK] All checks passed - login should work!")
        
        # Test password hash creation for comparison
        print(f"4. Testing password hash creation...")
        new_hash = get_password_hash(password)
        print(f"   New hash: {new_hash[:50]}...")
        print(f"   Verification with new hash: {verify_password(password, new_hash)}")
        
    except Exception as e:
        print(f"[ERROR] Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_login_logic()