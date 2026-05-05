# seed.py
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import models
from auth import hash_password
import sys

# Ensure UTF-8 output for Windows console to handle symbols like ₹
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def seed_data():
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Create a test user
        test_user = db.query(models.User).filter(models.User.email == "test@example.com").first()
        if not test_user:
            test_user = models.User(
                full_name="Prashant Kumar",
                email="test@example.com",
                password=hash_password("password123"),
                mobile="9876543210",
                dob="15 May 1992",
                address="Flat 402, Green Glen Layout, Bellandur, Bangalore - 560103",
                nominee_name="Sneha Kumar",
                nominee_relation="Spouse",
                nominee_dob="10 Jun 1994",
                bank_name="HDFC Bank",
                bank_acc_no="**** 5562",
                bank_acc_name="Prashant Kumar",
                bank_ifsc="HDFC0001234"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print("Created test user: test@example.com / password123")

        # Clear existing data for this user to avoid duplicates if re-running
        db.query(models.Claim).filter(models.Claim.user_id == test_user.id).delete()
        db.query(models.Policy).filter(models.Policy.user_id == test_user.id).delete()
        db.query(models.ServiceRequest).filter(models.ServiceRequest.user_id == test_user.id).delete()
        db.query(models.Notification).filter(models.Notification.user_id == test_user.id).delete()
        db.query(models.Payment).filter(models.Payment.user_id == test_user.id).delete()
        db.commit()

        # Add Policies
        p1 = models.Policy(
            policy_number="POL-LIC-2023001",
            title="LIC Tech Term Plan",
            provider="LIC of India",
            type="Term Life Insurance",
            sum_assured="₹1 Crore",
            premium="₹1,199",
            status="Active",
            start_date="12 Jan 2023",
            end_date="11 Jan 2043",
            due_date="12 Jan 2025",
            nominee_name="Sneha Kumar",
            nominee_relation="Spouse",
            user_id=test_user.id
        )
        p2 = models.Policy(
            policy_number="POL-STR-2022087",
            title="Star Comprehensive Health",
            provider="Star Health Insurance",
            type="Health Floater",
            sum_assured="₹10 Lakh",
            premium="₹799",
            status="Active",
            start_date="05 Aug 2022",
            end_date="04 Aug 2025",
            due_date="05 Aug 2025",
            user_id=test_user.id
        )
        p3 = models.Policy(
            policy_number="POL-BAJ-2024019",
            title="Bajaj Allianz Car Insurance",
            provider="Bajaj Allianz",
            type="Comprehensive Motor",
            sum_assured="₹8.5 Lakh",
            premium="₹499",
            status="Renewal Due",
            start_date="10 Nov 2023",
            end_date="09 Nov 2024",
            due_date="05 Nov 2024",
            user_id=test_user.id
        )
        db.add_all([p1, p2, p3])
        db.commit()

        # Add Claims
        claims = [
            models.Claim(
                claim_number="CLM-STR-99021",
                policy_id=p2.id,
                user_id=test_user.id,
                status="Under Review",
                date="15 Oct 2024",
                amount="₹45,000",
                type="Hospitalization",
                hospital="Apollo Hospital, Bangalore",
                reason="Dengue Treatment"
            )
        ]
        db.add_all(claims)

        # Add Notifications
        notifications = [
            models.Notification(
                title="Premium Due",
                message="Your Bajaj Allianz Car Insurance premium is due on 05 Nov.",
                time="2 hours ago",
                unread=True,
                user_id=test_user.id
            ),
            models.Notification(
                title="Claim Update",
                message="Documents for claim CLM-STR-99021 have been verified.",
                time="1 day ago",
                unread=False,
                user_id=test_user.id
            )
        ]
        db.add_all(notifications)

        # Add Payments
        payments = [
            models.Payment(
                transaction_id="TXN10029334",
                policy="LIC Tech Term Plan",
                amount="₹1,199",
                date="12 Jan 2024",
                status="Success",
                method="UPI",
                user_id=test_user.id
            ),
            models.Payment(
                transaction_id="TXN10028812",
                policy="Star Comprehensive Health",
                amount="₹799",
                date="05 Aug 2023",
                status="Success",
                method="Debit Card",
                user_id=test_user.id
            )
        ]
        db.add_all(payments)

        db.commit()
        print("Successfully seeded dashboard data for test user.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
