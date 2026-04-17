import os
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas
from database import engine, SessionLocal

load_dotenv()
from auth import hash_password, verify_password

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

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
        "user": {
            "full_name": db_user.full_name,
            "email": db_user.email,
            "mobile": db_user.mobile
        }
    }

# ---------------------------------------------------------
# CONTACT SERVICE ROUTES
# ---------------------------------------------------------

# ✅ User Submits Contact Form
@app.post("/contact")
def submit_contact(contact: schemas.ContactSchema, db: Session = Depends(get_db)):
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

from auth import create_access_token, verify_token
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    payload = verify_token(token)
    if not payload or payload.get("sub") != ADMIN_USERNAME:
        raise HTTPException(status_code=401, detail="Unauthorized admin access")
    return payload

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
def view_contacts(db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    contacts = db.query(models.Contact).all()
    return contacts

# ✅ Admin Delete Contact
@app.delete("/admin/contacts/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}

# ✅ Admin Update Contact Status (Mark as Read)
@app.patch("/admin/contacts/{contact_id}")
def update_contact_status(contact_id: int, db: Session = Depends(get_db), current_admin: dict = Depends(get_current_admin)):
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    contact.is_read = not getattr(contact, 'is_read', False) # Safety check if column not yet migrated
    db.commit()
    db.refresh(contact)
    return contact