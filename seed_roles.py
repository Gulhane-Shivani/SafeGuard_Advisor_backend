from database import SessionLocal
import models
from auth import hash_password

def seed_roles():
    db = SessionLocal()
    roles = ['SUPER_ADMIN', 'ADMIN', 'AGENT', 'CSR', 'CUSTOMER']
    for role in roles:
        email = f"{role.lower()}@safeguard.com"
        existing = db.query(models.User).filter(models.User.email == email).first()
        if not existing:
            u = models.User(
                full_name=f"{role.replace('_', ' ').title()} User",
                email=email,
                password=hash_password("password123"),
                role=role
            )
            db.add(u)
            db.commit()
            print(f"Created {role} user: {email} / password123")
        else:
            print(f"{role} user already exists: {email}")
    db.close()

if __name__ == "__main__":
    seed_roles()
