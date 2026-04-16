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
    "https://safe-guard-advisor.vercel.app",
    "https://safe-guard-advisor.vercel.app/",
    "https://safe-guard-advisor-backend.onrender.com",
    "postgresql://future_invo_solution:pW0ocqWPIdd15y4HbJKP2HTH2GV1rbz2@dpg-d7gb7p1j2pic738aeu10-a/safeguard_db_3vad"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

    if user.email:
        existing = db.query(models.User).filter(models.User.email == user.email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

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