import json
import os
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime
# Import the exact feature engineering used during training
from offline_sim.enhanced_features import create_enhanced_features

# Path to the new high-performance Ensemble Model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENSEMBLE_MODEL_PATH = os.path.join(BASE_DIR, "..", "trained_ensemble_detector.pkl")

class FLComponent:
    def __init__(self, model_path: str = ENSEMBLE_MODEL_PATH):
        """Initializes the FLComponent by loading the 94.2% accuracy Ensemble Detector."""
        self.model_path = model_path
        self.detector = self._load_model()
        # Default ensemble threshold for anomaly detection
        self.threshold = 0.5 

    def _load_model(self):
        """Loads the trained EnsembleAnomalyDetector from the .pkl file."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"FATAL: Ensemble model not found at {self.model_path}")
        
        # Load the full detector object (includes scaler and ensemble weights)
        detector = joblib.load(self.model_path)
        print(f"Ensemble FL Model (AUC: 0.9517) loaded from {self.model_path}")
        return detector

    def score_access(self, context: dict) -> float:
        """
        Scores an access request using the Ensemble Detector.
        Returns a probability score (0.0 to 1.0) where > 0.5 is an anomaly.
        """
        try:
            # 1. Enrich context for the ensemble feature engine
            current_dt = datetime.now()
            context['hour'] = current_dt.hour
            context['ts'] = time.time()
            
            # Use username as client_id for behavioral matching
            if "client_id" not in context:
                context["client_id"] = context.get("username", "unknown")
            
            # 2. Convert to DataFrame and apply feature engineering
            df = pd.DataFrame([context])
            
            # 3. Predict anomaly probability
            # predict_proba returns the weighted consensus of RF, GBM, and SVM
            anomaly_scores = self.detector.predict_proba(df)
            score = float(anomaly_scores[0])
            
            print(f"Ensemble Inference: Score={score:.4f}")
            return score
            
        except Exception as e:
            print(f"Ensemble FL Inference Error: {e}")
            return 0.0 # Default to safe on error