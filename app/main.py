"""
MindTrack - AI Mental Wellness Companion
FastAPI Backend Application
"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth, users, questionnaire, predictions, statistics
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MindTrack API",
    description="AI Mental Wellness Companion Backend",
    version="1.0.0"
)

# Configure CORS - allows environment variable for Render deployment
# Default to localhost for development
cors_origins = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(questionnaire.router, prefix="/api/questionnaire", tags=["Questionnaire"])
app.include_router(predictions.router, prefix="/api/predictions", tags=["Predictions"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])

@app.get("/")
def root():
    return {"message": "Welcome to MindTrack API - AI Mental Wellness Companion"}

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "service": "MindTrack API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
