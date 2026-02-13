"""
MindTrack Database Models
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    responses = relationship("UserResponse", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")
    progress = relationship("UserProgress", back_populates="user")

class UserResponse(Base):
    """User questionnaire responses"""
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    questionnaire_data = Column(JSON, nullable=False)
    risk_score = Column(Float)  # ML predicted risk score (0-100)
    risk_level = Column(String(20))  # Low, Medium, High
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="responses")

class Prediction(Base):
    """ML model predictions"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    risk_level = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    factors = Column(JSON)  # Key risk factors identified
    recommendations = Column(JSON)  # Personalized recommendations
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")

class UserProgress(Base):
    """User progress tracking over time"""
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    mood_rating = Column(Integer)  # 1-10 scale
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="progress")

class SurveyData(Base):
    """Imported survey data from CSV for analysis"""
    __tablename__ = "survey_data"
    
    id = Column(Integer, primary_key=True, index=True)
    year_group = Column(String(20))
    gender = Column(String(20))
    ethnicity = Column(String(50))
    # Emotional responses (encoded as numeric)
    feel_sad = Column(Integer)
    feel_lonely = Column(Integer)
    feel_confident = Column(Integer)
    feel_stressed = Column(Integer)
    feel_happy = Column(Integer)
    feel_angry = Column(Integer)
    # Sleep
    hours_sleep = Column(Integer)
    # Physical activity
    minutes_physical_activity = Column(Integer)
    # Self-harm
    self_harm_ever = Column(String(10))
    self_harm_frequency = Column(String(20))
    # Bullying
    bullied = Column(String(10))
    # School belonging
    school_belonging = Column(String(20))
    # Many more columns...
    
    def __repr__(self):
        return f"<SurveyData(id={self.id}, year_group={self.year_group})>"
