"""
MindTrack User Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List

from app.database import get_db
from app.auth import get_current_user
from app.models import User, UserProgress

router = APIRouter()

class ProgressCreate(BaseModel):
    mood_rating: int
    notes: str = None

class ProgressResponse(BaseModel):
    id: int
    date: str
    risk_score: Optional[float]
    mood_rating: int
    notes: Optional[str]
    
    class Config:
        orm_mode = True

@router.get("/profile")
def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get user profile"""
    return {
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "created_at": current_user.created_at.isoformat()
    }

@router.put("/profile")
def update_user_profile(
    full_name: str = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    if full_name:
        current_user.full_name = full_name
    
    db.commit()
    db.refresh(current_user)
    
    return {"message": "Profile updated successfully"}

@router.get("/progress", response_model=List[ProgressResponse])
def get_user_progress(
    limit: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user progress history"""
    progress = db.query(UserProgress)\
        .filter(UserProgress.user_id == current_user.id)\
        .order_by(UserProgress.date.desc())\
        .limit(limit)\
        .all()
    
    return [
        ProgressResponse(
            id=p.id,
            date=p.date.isoformat(),
            risk_score=p.risk_score,
            mood_rating=p.mood_rating,
            notes=p.notes
        )
        for p in progress
    ]

@router.post("/progress")
def add_progress(
    progress_data: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add new progress entry"""
    new_progress = UserProgress(
        user_id=current_user.id,
        mood_rating=progress_data.mood_rating,
        notes=progress_data.notes
    )
    
    db.add(new_progress)
    db.commit()
    db.refresh(new_progress)
    
    return {
        "message": "Progress added successfully",
        "id": new_progress.id,
        "date": new_progress.date.isoformat()
    }
