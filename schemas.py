# schemas.py
from pydantic import BaseModel
from typing import Optional, List

class RegisterSchema(BaseModel):
    full_name: Optional[str] = "Anonymous"
    email: Optional[str] = None
    password: Optional[str] = None
    mobile: Optional[str] = None

class LoginSchema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    mobile: Optional[str] = None

class ContactSchema(BaseModel):
    name: str
    email: str
    subject: str
    message: str

    class Config:
        orm_mode = True

class AdminLoginSchema(BaseModel):
    username: str
    password: str

# Dashboard Schemas
class PolicySchema(BaseModel):
    policy_number: str
    title: str
    provider: str
    type: str
    sum_assured: str
    premium: str
    status: str
    start_date: str
    end_date: str
    due_date: str
    nominee_name: Optional[str] = None
    nominee_relation: Optional[str] = None

    class Config:
        orm_mode = True

class ClaimSchema(BaseModel):
    claim_number: str
    policy_id: int
    status: str
    date: str
    amount: str
    type: str
    hospital: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        orm_mode = True

class ServiceRequestSchema(BaseModel):
    request_number: str
    type: str
    description: str
    date: str
    status: str

    class Config:
        orm_mode = True

class NotificationSchema(BaseModel):
    title: str
    message: str
    time: str
    unread: bool

    class Config:
        orm_mode = True

class UserDashboardData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    dob: Optional[str] = None
    address: Optional[str] = None
    nominee: dict
    bankDetails: dict
    stats: dict
    policies: List[PolicySchema]
    claims: List[ClaimSchema]
    service_requests: List[ServiceRequestSchema]
    notifications: List[NotificationSchema]