from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import datetime
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100))
    email = Column(String(100), unique=True, nullable=True)
    password = Column(String(255), nullable=True)
    mobile = Column(String(10), unique=True, nullable=True)
    dob = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    role = Column(String(50), nullable=True, default="CUSTOMER")
    primary_branch = Column(String(100), nullable=True)
    status = Column(String(50), nullable=True, default="Active")
    
    # Nominee info
    nominee_name = Column(String(100), nullable=True)
    nominee_relation = Column(String(50), nullable=True)
    nominee_dob = Column(String(50), nullable=True)
    
    # Bank info
    bank_name = Column(String(100), nullable=True)
    bank_acc_no = Column(String(50), nullable=True)
    bank_acc_name = Column(String(100), nullable=True)
    bank_ifsc = Column(String(20), nullable=True)
    
    policies = relationship("Policy", back_populates="owner")
    claims = relationship("Claim", back_populates="owner")
    service_requests = relationship("ServiceRequest", back_populates="owner")
    notifications = relationship("Notification", back_populates="owner")
    payments = relationship("Payment", back_populates="owner")

class Policy(Base):
    __tablename__ = "policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_number = Column(String(50), unique=True, index=True)
    title = Column(String(200))
    provider = Column(String(100))
    type = Column(String(50))
    sum_assured = Column(String(50))
    premium = Column(String(50))
    status = Column(String(50))
    start_date = Column(String(50))
    end_date = Column(String(50))
    due_date = Column(String(50))
    nominee_name = Column(String(100), nullable=True)
    nominee_relation = Column(String(50), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="policies")
    claims = relationship("Claim", back_populates="policy")

class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)
    claim_number = Column(String(50), unique=True, index=True)
    policy_id = Column(Integer, ForeignKey("policies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    status = Column(String(50))
    date = Column(String(50))
    amount = Column(String(50))
    type = Column(String(50))
    hospital = Column(String(200), nullable=True)
    reason = Column(String(500), nullable=True)

    owner = relationship("User", back_populates="claims")
    policy = relationship("Policy", back_populates="claims")

class ServiceRequest(Base):
    __tablename__ = "service_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_number = Column(String(50), unique=True, index=True)
    type = Column(String(100))
    description = Column(String(500))
    date = Column(String(50))
    status = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="service_requests")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    message = Column(String(500))
    time = Column(String(50))
    unread = Column(Boolean, default=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="notifications")

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100))
    subject = Column(String(200))
    message = Column(String(1000))
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String(50), unique=True, index=True)
    policy = Column(String(200))
    amount = Column(String(50))
    date = Column(String(50))
    status = Column(String(50))
    method = Column(String(50))
    user_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="payments")