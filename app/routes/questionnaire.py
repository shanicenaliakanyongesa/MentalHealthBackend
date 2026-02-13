"""
MindTrack Questionnaire Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.database import get_db
from app.auth import get_current_user
from app.models import User, UserResponse, Prediction

router = APIRouter()

# Questionnaire questions model
class QuestionnaireData(BaseModel):
    # Emotional state (1-5 scale)
    feel_sad: int
    feel_lonely: int
    feel_confident: int
    feel_stressed: int
    feel_happy: int
    feel_angry: int
    
    # Sleep (hours)
    hours_sleep: float
    
    # Physical activity (minutes per week)
    minutes_physical_activity: int
    
    # Social factors
    friends_count: int  # 0-5+ scale
    family_support: int  # 1-5 scale
    
    # School factors
    school_belonging: int  # 1-5 scale
    
    # Self-harm (if applicable)
    self_harm_ever: bool = False
    self_harm_frequency: str = "Never"
    
    # Bullying
    bullied_recently: bool = False
    
    # Additional factors
    stress_level: int  # 1-10
    anxiety_level: int  # 1-10

class QuestionnaireResponse(BaseModel):
    id: int
    risk_score: Optional[float]
    risk_level: Optional[str]
    created_at: str
    
    class Config:
        orm_mode = True

@router.post("/submit")
def submit_questionnaire(
    data: QuestionnaireData,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit questionnaire and get prediction"""
    # Store the response
    response = UserResponse(
        user_id=current_user.id,
        questionnaire_data=data.dict()
    )
    
    db.add(response)
    db.commit()
    db.refresh(response)
    
    # Calculate risk score (simplified - will be replaced with ML model)
    risk_score = calculate_risk_score(data.dict())
    
    # Determine risk level
    if risk_score < 30:
        risk_level = "Low"
    elif risk_score < 60:
        risk_level = "Medium"
    else:
        risk_level = "High"
    
    # Update response with risk score
    response.risk_score = risk_score
    response.risk_level = risk_level
    db.commit()
    
    # Generate prediction with recommendations
    prediction = generate_prediction(risk_score, risk_level, data.dict())
    prediction_response = Prediction(
        user_id=current_user.id,
        risk_level=risk_level,
        risk_score=risk_score,
        factors=prediction["factors"],
        recommendations=prediction["recommendations"]
    )
    
    db.add(prediction_response)
    db.commit()
    
    return {
        "response_id": response.id,
        "risk_score": risk_score,
        "risk_level": risk_level,
        "factors": prediction["factors"],
        "recommendations": prediction["recommendations"],
        "message": "Questionnaire submitted successfully"
    }

@router.get("/history", response_model=List[QuestionnaireResponse])
def get_questionnaire_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's questionnaire history"""
    responses = db.query(UserResponse)\
        .filter(UserResponse.user_id == current_user.id)\
        .order_by(UserResponse.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [
        QuestionnaireResponse(
            id=r.id,
            risk_score=r.risk_score,
            risk_level=r.risk_level,
            created_at=r.created_at.isoformat()
        )
        for r in responses
    ]

def calculate_risk_score(data: Dict[str, Any]) -> float:
    """Calculate risk score based on questionnaire data"""
    score = 0
    max_score = 100
    
    # Emotional factors (0-20 points)
    negative_emotions = data.get("feel_sad", 1) + data.get("feel_lonely", 1) + \
                        data.get("feel_stressed", 1) + data.get("feel_angry", 1)
    positive_emotions = data.get("feel_confident", 1) + data.get("feel_happy", 1)
    score += (negative_emotions - positive_emotions) * 2
    
    # Sleep (0-15 points)
    sleep = data.get("hours_sleep", 8)
    if sleep < 6:
        score += 15
    elif sleep < 7:
        score += 10
    elif sleep < 8:
        score += 5
    
    # Physical activity (0-10 points)
    activity = data.get("minutes_physical_activity", 0)
    if activity < 30:
        score += 10
    elif activity < 60:
        score += 5
    
    # Social factors (0-15 points)
    friends = data.get("friends_count", 3)
    if friends < 2:
        score += 10
    elif friends < 3:
        score += 5
    
    family_support = data.get("family_support", 3)
    if family_support < 3:
        score += 5
    
    # School belonging (0-10 points)
    belonging = data.get("school_belonging", 3)
    if belonging < 3:
        score += 10
    elif belonging < 4:
        score += 5
    
    # Self-harm (0-15 points)
    if data.get("self_harm_ever", False):
        score += 15
    
    # Bullying (0-10 points)
    if data.get("bullied_recently", False):
        score += 10
    
    # Stress and anxiety (0-5 points each)
    score += data.get("stress_level", 1) - 1
    score += data.get("anxiety_level", 1) - 1
    
    return min(max(score, 0), 100)

def generate_prediction(risk_score: float, risk_level: str, data: Dict[str, Any]) -> Dict:
    """Generate personalized prediction and recommendations"""
    factors = []
    recommendations = []
    
    # Identify risk factors
    if data.get("hours_sleep", 8) < 7:
        factors.append("Poor sleep patterns")
        recommendations.append("Try to get 7-9 hours of sleep each night. Establish a regular bedtime routine.")
    
    if data.get("minutes_physical_activity", 0) < 60:
        factors.append("Low physical activity")
        recommendations.append("Aim for at least 60 minutes of physical activity per day. Even a 10-minute walk can help.")
    
    if data.get("feel_sad", 1) >= 4:
        factors.append("Feelings of sadness")
        recommendations.append("Consider talking to someone you trust about how you're feeling. Practice self-care activities.")
    
    if data.get("feel_stressed", 1) >= 4:
        factors.append("High stress levels")
        recommendations.append("Try stress management techniques like deep breathing, meditation, or taking breaks.")
    
    if data.get("self_harm_ever", False):
        factors.append("History of self-harm")
        recommendations.append("Please consider reaching out to a mental health professional for support.")
        recommendations.append("You can contact Samaritans helpline: 116 123")
    
    if data.get("bullied_recently", False):
        factors.append("Recent bullying experience")
        recommendations.append("Speak to a trusted adult or teacher about what's happening.")
        recommendations.append("Remember: it's not your fault, and help is available.")
    
    if data.get("family_support", 3) < 3:
        factors.append("Limited family support")
        recommendations.append("Consider building support networks through friends, mentors, or school counselors.")
    
    # Add general recommendations
    if risk_level == "High":
        recommendations.append("Consider scheduling an appointment with a mental health professional.")
        recommendations.append("Practice daily mindfulness or grounding exercises.")
    elif risk_level == "Medium":
        recommendations.append("Regular exercise and healthy sleep can help improve your mental health.")
        recommendations.append("Try keeping a mood journal to track your emotions.")
    else:
        recommendations.append("Great job taking care of your mental health! Keep up the good work.")
        recommendations.append("Continue maintaining healthy habits and supporting others.")
    
    return {
        "factors": factors,
        "recommendations": recommendations
    }
