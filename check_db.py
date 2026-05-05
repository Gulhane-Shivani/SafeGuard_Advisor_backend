from database import SessionLocal
import models

def check_users():
    db = SessionLocal()
    users = db.query(models.User).all()
    print(f"{'Email':<30} | {'Role':<15} | {'Full Name':<20}")
    print("-" * 70)
    for user in users:
        print(f"{str(user.email):<30} | {str(user.role):<15} | {str(user.full_name):<20}")
    db.close()

if __name__ == "__main__":
    check_users()
