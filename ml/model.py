"""
MindTrack ML Model Module
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os

class MentalHealthPredictor:
    """ML model for predicting mental health risk levels"""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()
        self.feature_names = [
            'feel_sad', 'feel_lonely', 'feel_confident', 'feel_stressed',
            'feel_happy', 'feel_angry', 'hours_sleep', 'minutes_physical_activity',
            'friends_count', 'family_support', 'school_belonging',
            'self_harm_ever', 'bullied_recently', 'stress_level', 'anxiety_level'
        ]
        self.risk_levels = ['Low', 'Medium', 'High']
        
    def prepare_features(self, data: dict) -> np.ndarray:
        """Prepare features from input data"""
        features = []
        
        for feature in self.feature_names:
            value = data.get(feature, 0)
            
            # Convert boolean to int
            if isinstance(value, bool):
                value = int(value)
            
            # Handle string values
            if isinstance(value, str):
                if value.lower() in ['never', 'no', 'false']:
                    value = 0
                elif value.lower() in ['rarely', 'sometimes']:
                    value = 1
                elif value.lower() in ['often', 'yes', 'true']:
                    value = 2
                else:
                    value = 0
            
            features.append(float(value))
        
        return np.array(features).reshape(1, -1)
    
    def train(self, X_train: np.ndarray, y_train: np.ndarray):
        """Train the model"""
        # Scale features
        X_scaled = self.scaler.fit_transform(X_train)
        
        # Use Gradient Boosting for better performance
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        self.model.fit(X_scaled, y_train)
        
        return self.model
    
    def predict(self, X: np.ndarray) -> dict:
        """Make predictions"""
        if self.model is None:
            return {
                'error': 'Model not trained. Please train the model first.'
            }
        
        X_scaled = self.scaler.transform(X)
        prediction = self.model.predict(X_scaled)
        probability = self.model.predict_proba(X_scaled)
        
        # Get risk level
        risk_level = self.risk_levels[prediction[0]]
        
        # Get confidence scores
        confidence = {
            level: float(prob[0][i])
            for i, level in enumerate(self.risk_levels)
        }
        
        return {
            'risk_level': risk_level,
            'risk_score': float(probability[0][prediction[0]] * 100),
            'confidence': confidence
        }
    
    def predict_from_data(self, data: dict) -> dict:
        """Make prediction from raw data"""
        features = self.prepare_features(data)
        return self.predict(features)
    
    def save_model(self, path: str):
        """Save the trained model"""
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'risk_levels': self.risk_levels
        }, path)
    
    def load_model(self, path: str):
        """Load a trained model"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.risk_levels = data['risk_levels']


def create_synthetic_training_data(n_samples: int = 1000) -> tuple:
    """Create synthetic training data based on survey patterns"""
    np.random.seed(42)
    
    X = []
    y = []
    
    for _ in range(n_samples):
        # Generate random features
        feel_sad = np.random.randint(1, 6)
        feel_lonely = np.random.randint(1, 6)
        feel_confident = np.random.randint(1, 6)
        feel_stressed = np.random.randint(1, 6)
        feel_happy = np.random.randint(1, 6)
        feel_angry = np.random.randint(1, 6)
        
        hours_sleep = np.random.uniform(4, 10)
        minutes_physical_activity = np.random.randint(0, 300)
        
        friends_count = np.random.randint(0, 6)
        family_support = np.random.randint(1, 6)
        school_belonging = np.random.randint(1, 6)
        
        self_harm_ever = np.random.choice([0, 1], p=[0.8, 0.2])
        bullied_recently = np.random.choice([0, 1], p=[0.75, 0.25])
        
        stress_level = np.random.randint(1, 11)
        anxiety_level = np.random.randint(1, 11)
        
        features = [
            feel_sad, feel_lonely, feel_confident, feel_stressed,
            feel_happy, feel_angry, hours_sleep, minutes_physical_activity,
            friends_count, family_support, school_belonging,
            self_harm_ever, bullied_recently, stress_level, anxiety_level
        ]
        
        # Calculate risk label based on patterns
        risk_score = (
            (6 - feel_sad) * 2 +
            (6 - feel_lonely) * 1.5 +
            (6 - feel_confident) * 1.5 +
            (6 - feel_stressed) * 2 +
            (6 - feel_happy) * 2 +
            (6 - feel_angry) * 1 +
            max(0, 8 - hours_sleep) * 3 +
            max(0, 60 - minutes_physical_activity) * 0.02 +
            max(0, 3 - friends_count) * 3 +
            max(0, 3 - family_support) * 3 +
            max(0, 3 - school_belonging) * 2 +
            self_harm_ever * 15 +
            bullied_recently * 10 +
            stress_level * 2 +
            anxiety_level * 2
        )
        
        # Determine risk level
        if risk_score < 25:
            label = 0  # Low
        elif risk_score < 50:
            label = 1  # Medium
        else:
            label = 2  # High
        
        X.append(features)
        y.append(label)
    
    return np.array(X), np.array(y)


def train_model():
    """Train and save the model"""
    print("Creating training data...")
    X, y = create_synthetic_training_data(2000)
    
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print("Training model...")
    predictor = MentalHealthPredictor()
    predictor.train(X_train, y_train)
    
    # Evaluate
    X_scaled = predictor.scaler.transform(X_test)
    y_pred = predictor.model.predict(X_scaled)
    
    print("\nModel Performance:")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=predictor.risk_levels))
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), 'model.joblib')
    predictor.save_model(model_path)
    print(f"\nModel saved to {model_path}")
    
    return predictor


if __name__ == "__main__":
    train_model()
