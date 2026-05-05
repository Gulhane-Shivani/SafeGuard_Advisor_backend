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
        from_attributes = True

class AdminLoginSchema(BaseModel):
    username: str
    password: str

class AdminCreateUserSchema(BaseModel):
    full_name: str
    email: str
    role: str
    primary_branch: str
    status: Optional[str] = "Active"

class AdminUpdateUserSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    primary_branch: Optional[str] = None
    status: Optional[str] = None

class UserResponseSchema(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    role: Optional[str] = None
    primary_branch: Optional[str] = None
    status: Optional[str] = "Active" # Mock status

    class Config:
        from_attributes = True

# Dashboard Schemas
class PolicySchema(BaseModel):
    id: int
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
        from_attributes = True

class ClaimSchema(BaseModel):
    id: int
    claim_number: str
    policy_id: int
    policy_title: Optional[str] = None
    status: str
    date: str
    amount: str
    type: str
    hospital: Optional[str] = None
    reason: Optional[str] = None

    class Config:
        from_attributes = True

class ServiceRequestSchema(BaseModel):
    id: int
    request_number: str
    type: str
    description: str
    date: str
    status: str

    class Config:
        from_attributes = True

class NotificationSchema(BaseModel):
    id: int
    title: str
    message: str
    time: str
    unread: bool

    class Config:
        from_attributes = True

class PaymentSchema(BaseModel):
    id: int
    transaction_id: str
    policy: str
    amount: str
    date: str
    status: str
    method: str

    class Config:
        from_attributes = True

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
    serviceRequests: List[ServiceRequestSchema]
    notifications: List[NotificationSchema]
    payments: List[PaymentSchema]