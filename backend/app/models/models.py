from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    filename = Column(String)
    file_path = Column(String)  # Path to stored PDF
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Analysis results (simplified for now, could be JSON or specific fields)
    summary = Column(Text, nullable=True)
    risk_score = Column(Integer, nullable=True)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    # owner = relationship("User", back_populates="contracts") 
