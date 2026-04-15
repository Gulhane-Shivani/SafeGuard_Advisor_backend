# schemas.py
from pydantic import BaseModel
from typing import Optional

class RegisterSchema(BaseModel):
    full_name: str
    email: Optional[str] = None
    password: Optional[str] = None
    mobile: Optional[str] = None

class LoginSchema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    mobile: Optional[str] = None