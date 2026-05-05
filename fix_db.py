from database import SessionLocal
import models
from auth import hash_password

def fix_superadmin():
    db = SessionLocal()
    try:
        # Check if any user has SUPER_ADMIN role
        super_admin = db.query(models.User).filter(models.User.role == 'SUPER_ADMIN').first()
        
        if not super_admin:
            # Check if common superadmin email exists
            super_admin = db.query(models.User).filter(models.User.email == 'super_admin@safeguard.com').first()
            
        if not super_admin:
            # Create one if missing
            print("Creating new Super Admin...")
            super_admin = models.User(
                full_name="Super Administrator",
                email="super_admin@safeguard.com",
                password=hash_password("admin123"),
                role="SUPER_ADMIN",
                primary_branch="Main Branch"
            )
            db.add(super_admin)
        else:
            print(f"Found Super Admin: {super_admin.email}. Updating details...")
            super_admin.role = "SUPER_ADMIN"
            if not super_admin.full_name or super_admin.full_name == "Anonymous":
                super_admin.full_name = "Super Administrator"
            if not super_admin.password:
                super_admin.password = hash_password("admin123")
        
        db.commit()
        print(f"Super Admin fixed: {super_admin.email} / role: {super_admin.role}")
        
        # Also ensure all users have a role (fix for existing data)
        users = db.query(models.User).filter(models.User.role == None).all()
        for u in users:
            u.role = "CUSTOMER"
        db.commit()
        if users:
            print(f"Fixed {len(users)} users with missing roles.")
            
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_superadmin()
