"""
User model for authentication and profile management.
"""
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid
import json


class User(Base):
    """
    User model for authentication and profile.
    
    Fields:
    - id: UUID primary key
    - email: Unique email address
    - hashed_password: Bcrypt hashed password
    - name: User's full name
    - created_at: Account creation timestamp
    - is_active: Account status
    """
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    # analyses = relationship("ContractAnalysis", back_populates="user")


class ContractAnalysis(Base):
    """
    Contract analysis history for users.
    Stores analysis results linked to users.
    """
    __tablename__ = "contract_analyses"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)  # Foreign key to users.id
    contract_filename = Column(String, nullable=False)
    fairness_score = Column(Integer, nullable=False)
    contract_type = Column(String)
    industry = Column(String)
    role = Column(String)
    location = Column(String)
    salary = Column(Integer, nullable=True)
    notice_period_days = Column(Integer, nullable=True)
    analysis_result_json = Column(Text, nullable=True)  # Store full analysis result as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    # user = relationship("User", back_populates="analyses")

