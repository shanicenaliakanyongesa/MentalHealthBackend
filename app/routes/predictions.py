"""
MindTrack Predictions Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Prediction

router = APIRouter()

class PredictionResponse(BaseModel):
    id: int
    risk_level: str
    risk_score: float
    factors: List[str]
    recommendations: List[str]
    created_at: str
    
    class Config:
        orm_mode = True

@router.get("/history", response_model=List[PredictionResponse])
def get_prediction_history(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's prediction history"""
    predictions = db.query(Prediction)\
        .filter(Prediction.user_id == current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .limit(limit)\
        .all()
    
    return [
        PredictionResponse(
            id=p.id,
            risk_level=p.risk_level,
            risk_score=p.risk_score,
            factors=p.factors or [],
            recommendations=p.recommendations or [],
            created_at=p.created_at.isoformat()
        )
        for p in predictions
    ]

@router.get("/latest")
def get_latest_prediction(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's latest prediction"""
    prediction = db.query(Prediction)\
        .filter(Prediction.user_id == current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .first()
    
    if not prediction:
        raise HTTPException(
            status_code=404,
            detail="No predictions found. Please complete a questionnaire first."
        )
    
    return {
        "id": prediction.id,
        "risk_level": prediction.risk_level,
        "risk_score": prediction.risk_score,
        "factors": prediction.factors or [],
        "recommendations": prediction.recommendations or [],
        "created_at": prediction.created_at.isoformat()
    }

@router.get("/trends")
def get_prediction_trends(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction trends over time"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    predictions = db.query(Prediction)\
        .filter(
            Prediction.user_id == current_user.id,
            Prediction.created_at >= start_date
        )\
        .order_by(Prediction.created_at.asc())\
        .all()
    
    if not predictions:
        return {
            "message": "No data available for the selected period",
            "trends": []
        }
    
    # Calculate trends
    scores = [p.risk_score for p in predictions]
    avg_score = sum(scores) / len(scores)
    
    # Determine trend direction
    if len(scores) >= 2:
        if scores[-1] < scores[0]:
            trend = "improving"
        elif scores[-1] > scores[0]:
            trend = "declining"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "average_score": round(avg_score, 2),
        "trend": trend,
        "total_predictions": len(predictions),
        "data_points": [
            {
                "date": p.created_at.isoformat(),
                "score": p.risk_score,
                "level": p.risk_level
            }
            for p in predictions
        ]
    }

@router.get("/insights")
def get_personalized_insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized insights based on prediction history"""
    predictions = db.query(Prediction)\
        .filter(Prediction.user_id == current_user.id)\
        .order_by(Prediction.created_at.desc())\
        .limit(30)\
        .all()
    
    if not predictions:
        return {
            "insights": [],
            "message": "Complete questionnaires to receive personalized insights"
        }
    
    insights = []
    
    # Analyze risk levels
    risk_levels = [p.risk_level for p in predictions]
    high_count = risk_levels.count("High")
    medium_count = risk_levels.count("Medium")
    low_count = risk_levels.count("Low")
    
    if high_count > len(predictions) * 0.5:
        insights.append({
            "type": "warning",
            "title": "Consistently High Risk",
            "message": "You've been experiencing high risk levels frequently. Consider seeking professional support."
        })
    
    # Analyze improvement
    if len(predictions) >= 3:
        recent_avg = sum([p.risk_score for p in predictions[:3]]) / 3
        older_avg = sum([p.risk_score for p in predictions[-3:]]) / 3
        
        if recent_avg < older_avg - 10:
            insights.append({
                "type": "positive",
                "title": "Great Progress!",
                "message": "Your risk scores have been improving. Keep up the good work!"
            })
    
    # Common factors analysis
    all_factors = []
    for p in predictions:
        if p.factors:
            all_factors.extend(p.factors)
    
    if all_factors:
        from collections import Counter
        factor_counts = Counter(all_factors)
        common_factors = factor_counts.most_common(3)
        
        if common_factors:
            insights.append({
                "type": "info",
                "title": "Common Challenges",
                "message": f"Most common factors: {', '.join([f[0] for f in common_factors])}"
            })
    
    return {
        "insights": insights,
        "summary": {
            "total_assessments": len(predictions),
            "high_risk_count": high_count,
            "medium_risk_count": medium_count,
            "low_risk_count": low_count
        }
    }
