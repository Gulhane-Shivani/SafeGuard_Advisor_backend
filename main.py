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

    return {"message": "Login successful"}