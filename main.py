import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

load_dotenv()
from auth import hash_password, verify_password, create_access_token, verify_token, SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

from sqlalchemy import text

@app.on_event("startup")
def run_migrations():
    db = SessionLocal()
    try:
        # Check if status column exists in users table
        if engine.name == 'postgresql':
            db.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Active'"))
        else:
            # SQLite doesn't support ADD COLUMN IF NOT EXISTS easily in one line for some versions
            try:
                db.execute(text("ALTER TABLE users ADD COLUMN status VARCHAR(50) DEFAULT 'Active'"))
            except Exception:
                pass # Already exists
        db.commit()
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        db.close()

# Enable CORS for frontend connectivity
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "https://safe-guard-advisor.vercel.app",
    "https://safeguard-advisor.vercel.app",
    "https://safeguard-advisor-backend.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health Check
@app.get("/")
def health_check():
    return {"status": "ok", "message": "SafeGuard Advisor Backend is running"}



# DB Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ Register
@app.post("/register")
def register(user: schemas.RegisterSchema, db: Session = Depends(get_db)):
    print(f"DEBUG: Incoming registration request: {user.dict()}")
    try:
        if user.email:
            existing = db.query(models.User).filter(models.User.email == user.email).first()
            if existing:
                raise HTTPException(status_code=400, detail="Email already registered")

            if not user.password or len(user.password) < 6:
                raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
                
            hashed = hash_password(user.password)

            new_user = models.User(
                full_name=user.full_name,
                email=user.email,
                password=hashed
            )

        elif user.mobile:
            existing = db.query(models.User).filter(models.User.mobile == user.mobile).first()
            if existing:
                raise HTTPException(status_code=400, detail="Mobile already registered")

            new_user = models.User(
                full_name=user.full_name,
                mobile=user.mobile
            )

        else:
            raise HTTPException(status_code=400, detail="Provide email or mobile")

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return {"message": "User registered successfully"}
    except Exception as e:
        db.rollback()
        print(f"Registration Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")

# ✅ Login
@app.post("/login")
def login(user: schemas.LoginSchema, db: Session = Depends(get_db)):

    if user.email:
        db_user = db.query(models.User).filter(models.User.email == user.email).first()
        if not db_user or not verify_password(user.password, db_user.password):
            raise HTTPException(status_code=401, detail="Invalid email or password")

    elif user.mobile:
        db_user = db.query(models.User).filter(models.User.mobile == user.mobile).first()
        if not db_user:
            raise HTTPException(status_code=401, detail="Mobile not registered")

    else:
        raise HTTPException(status_code=400, detail="Provide login details")

    return {
        "message": "Login successful",
        "access_token": create_access_token(data={"sub": db_user.email or db_user.mobile}),
        "token_type": "bearer",
        "user": {
            "full_name": db_user.full_name,
            "email": db_user.email,
            "mobile": db_user.mobile,
            "role": db_user.role,
            "primary_branch": db_user.primary_branch
        }
    }

# ---------------------------------------------------------
# CUSTOMER PORTAL ROUTES
# ---------------------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Unauthorized access")
    sub = payload.get("sub")
    user = db.query(models.User).filter(
        (models.User.email.ilike(sub)) | (models.User.mobile == sub)
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

class PaymentCreate(schemas.BaseModel):
    policy: str
    amount: str
    method: str

@app.post("/customer/payments")
async def record_payment(payment: PaymentCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    import uuid
    from datetime import datetime
    
    new_payment = models.Payment(
        user_id=current_user.id,
        transaction_id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
        policy=payment.policy,
        amount=payment.amount,
        date=datetime.now().strftime("%d %b %Y"),
        status="SUCCESS",
        method=payment.method
    )
    db.add(new_payment)
    db.commit()
    db.refresh(new_payment)
    return new_payment

# ---------------------------------------------------------
# CONTACT SERVICE ROUTES
# ---------------------------------------------------------

# ✅ User Submits Contact Form
@app.post("/contact")
def submit_contact(contact: schemas.ContactSchema, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    try:
        new_contact = models.Contact(
            name=contact.name,
            email=contact.email,
            subject=contact.subject,
            message=contact.message
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        return {"message": "Your message has been sent successfully!"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to submit contact: {str(e)}")

# ---------------------------------------------------------
# ADMIN PANEL ROUTES
# ---------------------------------------------------------

# Hardcoded Admin Credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin_password_123"

def get_current_admin(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    print(f"DEBUG: Verifying admin token...")
    payload = verify_token(token)
    if not payload:
        print("DEBUG: Token verification failed")
        raise HTTPException(status_code=401, detail="Unauthorized: Token verification failed.")
    
    sub = payload.get("sub")
    print(f"DEBUG: Token sub: {sub}")
    if not sub:
        print("DEBUG: Token missing 'sub'")
        raise HTTPException(status_code=401, detail="Unauthorized: Token is missing 'sub' claim.")
    
    # 1. Check hardcoded admin
    if sub == ADMIN_USERNAME:
        print("DEBUG: Hardcoded admin detected")
        return payload
        
    # 2. Check database for user with admin/super_admin role
    user = db.query(models.User).filter(
        (models.User.email.ilike(sub)) | (models.User.mobile == sub)
    ).first()
    
    if not user:
        print(f"DEBUG: User '{sub}' not found in DB")
        raise HTTPException(status_code=401, detail=f"Unauthorized: User '{sub}' not found.")
        
    role = getattr(user, 'role', 'N/A')
    print(f"DEBUG: User role in DB: {role}")
    
    if role:
        role_upper = role.strip().upper()
        if role_upper in ['ADMIN', 'SUPER_ADMIN']:
            print(f"DEBUG: Access granted for role {role_upper}")
            return user
        
    print(f"DEBUG: Forbidden - User {sub} has role {role}")
    raise HTTPException(status_code=403, detail=f"Forbidden: ADMIN or SUPER_ADMIN required. Your role: {role}")

# ✅ Admin Login
@app.post("/admin/login")
def admin_login(admin: schemas.AdminLoginSchema):
    if admin.username == ADMIN_USERNAME and admin.password == ADMIN_PASSWORD:
        access_token = create_access_token(data={"sub": ADMIN_USERNAME})
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "message": "Admin login successful"
        }
    else:
        raise HTTPException(status_code=401, detail="Invalid admin credentials")

# ✅ Admin View All Contacts
@app.get("/admin/contacts")
def view_contacts(db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    contacts = db.query(models.Contact).all()
    return contacts

# ✅ Admin Delete Contact
@app.delete("/admin/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

# ✅ Admin Update Contact Status (Mark as Read)
@app.patch("/admin/contacts/{contact_id}")
def update_contact_status(contact_id: int, db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.is_read = not getattr(contact, 'is_read', False) # Safety check if column not yet migrated
    db.commit()
    db.refresh(contact)
    return contact

# ✅ Admin View All Users (With Search & Pagination)
@app.get("/admin/users", response_model=list[schemas.UserResponseSchema])
def view_users(
    search: str = None, 
    page: int = 1, 
    page_size: int = 50, 
    db: Session = Depends(get_db), 
    current_admin: models.User = Depends(get_current_admin)
):
    query = db.query(models.User)
    
    if search:
        query = query.filter(
            (models.User.full_name.ilike(f"%{search}%")) | 
            (models.User.email.ilike(f"%{search}%")) |
            (models.User.mobile.ilike(f"%{search}%"))
        )
    
    # Simple Pagination
    offset = (page - 1) * page_size
    users = query.offset(offset).limit(page_size).all()
    
    # Ensure role is set to return something valid
    for user in users:
        if not getattr(user, 'role', None):
            user.role = "CUSTOMER"
    return users

# ✅ Admin Delete User
@app.delete("/admin/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Prevent deleting yourself
    sub = getattr(current_admin, 'email', None) or current_admin.get('sub')
    if user.email == sub:
        raise HTTPException(status_code=400, detail="You cannot delete your own account")

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

# ✅ Admin Create User
@app.post("/admin/users", response_model=schemas.UserResponseSchema)
def create_user(user_data: schemas.AdminCreateUserSchema, db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    import secrets
    import string
    
    # Generate temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%") for i in range(10))
    hashed_password = hash_password(temp_password)
    
    new_user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        password=hashed_password,
        role=user_data.role,
        primary_branch=user_data.primary_branch,
        status=user_data.status or "Active"
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # In a real app, send the temp password via email here.
    print(f"User created: {new_user.email}, Temporary Password: {temp_password}")
    
    return new_user

# ✅ Admin Update User
@app.put("/admin/users/{user_id}", response_model=schemas.UserResponseSchema)
def update_user(user_id: int, user_data: schemas.AdminUpdateUserSchema, db: Session = Depends(get_db), current_admin: models.User = Depends(get_current_admin)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.role is not None:
        user.role = user_data.role
    if user_data.primary_branch is not None:
        user.primary_branch = user_data.primary_branch
    if user_data.status is not None:
        user.status = user_data.status
        
    db.commit()
    db.refresh(user)
    return user
