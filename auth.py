import bcrypt
import hashlib

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