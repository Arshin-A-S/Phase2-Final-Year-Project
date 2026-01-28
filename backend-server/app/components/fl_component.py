import os
import sys
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime

# 1. Path Setup: Ensure the offline_sim directory is in the system path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
OFFLINE_SIM_PATH = os.path.join(PROJECT_ROOT, "app", "offline_sim")

if OFFLINE_SIM_PATH not in sys.path:
    sys.path.insert(0, OFFLINE_SIM_PATH)

# 2. Critical Namespace Fix: Import the class and alias it to __main__
try:
    import enhanced_features
    from enhanced_features import EnsembleAnomalyDetector
    
    import __main__
    setattr(__main__, 'EnsembleAnomalyDetector', EnsembleAnomalyDetector)
except (ImportError, AttributeError) as e:
    print(f"Namespace setup error: {e}")

# 3. Model Path Configuration
ENSEMBLE_MODEL_PATH = os.path.join(PROJECT_ROOT, "app", "trained_ensemble_detector.pkl")

class FLComponent:
    def __init__(self, model_path: str = ENSEMBLE_MODEL_PATH):
        self.model_path = os.path.abspath(model_path)
        self.threshold = 0.5 
        self.detector = self._load_model()

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        try:
            # The global injection above allows joblib to find the class
            detector = joblib.load(self.model_path)
            print(f"Ensemble FL Model loaded successfully from {self.model_path}")
            return detector
        except Exception as e:
            print(f"Error unpickling model: {e}")
            return None

    def score_access(self, context: dict) -> float:
        """Scores an access request using the Ensemble Detector (AUC: 0.9517)."""
        try:
            current_dt = datetime.now()
            # Prepare data in the format expected by your feature engineering engine
            data = {
                'username': context.get('username', 'unknown'),
                'location': context.get('location', 'unknown'),
                'device': context.get('device', 'unknown'),
                'department': context.get('department', 'unknown'),
                'hour': current_dt.hour,
                'ts': time.time(),
                'client_id': context.get('username', 'unknown')
            }
            df = pd.DataFrame([data])
            
            if self.detector:
                # The model combines RF, GBM, and LR for consensus scoring
                score = float(self.detector.predict_proba(df)[0])
                print(f"Inference: Probability={score:.4f}")
                return score
            return 0.0
        except Exception as e:
            print(f"Inference Error: {e}")
            return 0.0