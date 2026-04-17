import bcrypt
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# Secret key for JWT (in production, use a more secure key from environment variables)
SECRET_KEY = "safeguard_advisor_secret_key_123"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt. 
    Pre-hashes with SHA-256 to bypass bcrypt's 72-byte limit and ensures compatibility.
    """
    if not password:
        return None
    
    # 1. SHA-256 hash (hex) as a fixed length string (64 chars)
    # This solves the bcrypt 72-byte limit issue.
    password_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    
    # 2. Bcrypt hashing
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_hash.encode("utf-8"), salt)
    
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain password against a hashed password.
    """
    if not plain_password or not hashed_password:
        return False
        
    try:
        # Pre-hash plain password to match the hashing logic
        password_hash = hashlib.sha256(plain_password.encode("utf-8")).hexdigest()
        
        return bcrypt.checkpw(
            password_hash.encode("utf-8"), 
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None