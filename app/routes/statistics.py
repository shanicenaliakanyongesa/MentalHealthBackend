"""
MindTrack Statistics Routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import os

from app.database import get_db
from app.auth import get_current_user
from app.models import User, SurveyData

router = APIRouter()

# Statistics response models
class CategoryStats(BaseModel):
    category: str
    count: int
    percentage: float

class DistributionStats(BaseModel):
    label: str
    value: int

class OverallStats(BaseModel):
    total_responses: int
    avg_risk_level: str
    high_risk_percentage: float
    common_factors: List[str]

@router.get("/overview")
def get_statistics_overview():
    """Get overall statistics from survey data"""
    # This will be populated from the actual survey data
    # For now, return sample structure
    return {
        "total_surveys": 21958,
        "date_range": "2018-2019",
        "location": "Leeds, UK",
        "year_groups": ["Year 7", "Year 8", "Year 9", "Year 10", "Year 11", "Year 12", "Year 13"]
    }

@router.get("/demographics")
def get_demographics():
    """Get demographic distribution"""
    return {
        "gender": [
            {"label": "Female", "value": 51.2},
            {"label": "Male", "value": 47.5},
            {"label": "Other/Prefer not to say", "value": 1.3}
        ],
        "year_groups": [
            {"label": "Year 7", "value": 15.2},
            {"label": "Year 8", "value": 14.8},
            {"label": "Year 9", "value": 15.1},
            {"label": "Year 10", "value": 14.5},
            {"label": "Year 11", "value": 15.8},
            {"label": "Year 12", "value": 13.2},
            {"label": "Year 13", "value": 11.4}
        ],
        "ethnicity": [
            {"label": "White British", "value": 52.3},
            {"label": "Asian", "value": 18.4},
            {"label": "Mixed", "value": 12.1},
            {"label": "Black", "value": 9.8},
            {"label": "Other", "value": 7.4}
        ]
    }

@router.get("/mental-health/emotions")
def get_emotion_statistics():
    """Get emotional wellbeing statistics"""
    return {
        "feel_happy": {
            "every_day": 28.5,
            "most_days": 35.2,
            "some_days": 24.8,
            "rarely": 8.9,
            "never": 2.6
        },
        "feel_sad": {
            "every_day": 12.3,
            "most_days": 18.7,
            "some_days": 38.5,
            "rarely": 21.2,
            "never": 9.3
        },
        "feel_stressed": {
            "every_day": 15.8,
            "most_days": 24.3,
            "some_days": 35.1,
            "rarely": 16.4,
            "never": 8.4
        },
        "feel_lonely": {
            "every_day": 8.2,
            "most_days": 12.5,
            "some_days": 28.7,
            "rarely": 31.2,
            "never": 19.4
        }
    }

@router.get("/mental-health/risk-factors")
def get_risk_factors():
    """Get common mental health risk factors"""
    return {
        "self_harm": {
            "ever_harmed": 18.5,
            "never_harmed": 81.5
        },
        "bullying": {
            "bullied_recently": 23.4,
            "not_bullied": 76.6
        },
        "sleep": {
            "less_than_6_hours": 15.2,
            "6_to_8_hours": 45.8,
            "more_than_8_hours": 39.0
        },
        "physical_activity": {
            "active_60plus_minutes": 48.3,
            "active_30_to_60_minutes": 28.7,
            "less_active": 23.0
        }
    }

@router.get("/mental-health/support")
def get_support_statistics():
    """Get statistics about support-seeking behavior"""
    return {
        "seek_help_school": {
            "yes": 42.3,
            "no": 57.7
        },
        "know_where_to_get_help": {
            "yes_definitely": 35.8,
            "yes_probably": 28.4,
            "no_probably_not": 21.2,
            "no_definitely_not": 14.6
        },
        "trusted_adults": {
            "parents": 68.5,
            "friends": 52.3,
            "school_staff": 38.7,
            "no_one": 8.2
        }
    }

@router.get("/categories")
def get_all_categories():
    """Get all available statistics categories"""
    return {
        "categories": [
            "demographics",
            "mental-health/emotions",
            "mental-health/risk-factors",
            "mental-health/support",
            "lifestyle",
            "school-experience"
        ]
    }

@router.get("/lifestyle")
def get_lifestyle_statistics():
    """Get lifestyle-related statistics"""
    return {
        "breakfast": {
            "every_day": 52.3,
            "most_days": 22.8,
            "some_days": 15.2,
            "rarely": 9.7
        },
        "physical_activity_minutes": {
            "0_to_60": 28.4,
            "61_to_120": 31.2,
            "121_to_180": 22.5,
            "180_plus": 17.9
        },
        "screen_time": {
            "less_than_2_hours": 18.5,
            "2_to_4_hours": 42.3,
            "4_to_6_hours": 28.7,
            "more_than_6_hours": 10.5
        },
        "sleep_hours": {
            "less_than_5": 8.2,
            "5_to_6": 15.4,
            "6_to_7": 28.7,
            "7_to_8": 32.5,
            "more_than_8": 15.2
        }
    }

@router.get("/school-experience")
def get_school_experience():
    """Get school experience statistics"""
    return {
        "belong_school": {
            "strongly_agree": 28.5,
            "agree": 35.2,
            "neutral": 22.8,
            "disagree": 10.2,
            "strongly_disagree": 3.3
        },
        "enjoy_school": {
            "strongly_agree": 22.4,
            "agree": 31.8,
            "neutral": 25.2,
            "disagree": 14.8,
            "strongly_disagree": 5.8
        },
        "feel_safe": {
            "very_safe": 52.3,
            "safe": 32.5,
            "unsafe": 10.8,
            "very_unsafe": 4.4
        },
        "bullied_in_school": {
            "yes_cyber": 8.5,
            "yes_physical": 5.2,
            "yes_verbal": 15.8,
            "no": 70.5
        }
    }

@router.get("/filter/{category}")
def filter_by_category(
    category: str,
    filter_type: str = None,
    filter_value: str = None
):
    """Filter statistics by category and specific filters"""
    # This would filter the survey data based on criteria
    # For now, return a placeholder
    return {
        "category": category,
        "filter": f"{filter_type}={filter_value}",
        "message": "Filtered statistics would appear here",
        "data": {}
    }
