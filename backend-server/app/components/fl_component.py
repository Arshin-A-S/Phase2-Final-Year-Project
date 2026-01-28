import os
import sys
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime

# 1. Path Resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..'))

# Add root to path so 'app' is a valid package
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Namespace Binding (The macOS Fix)
try:
    # Absolute import from the package
    from app.offline_sim.enhanced_features import EnsembleAnomalyDetector
    
    # CRITICAL: Tell Python to look in __main__ for this class
    # joblib defaults to looking in the execution script's namespace
    import __main__
    __main__.EnsembleAnomalyDetector = EnsembleAnomalyDetector
    
    # Register in sys.modules to satisfy secondary lookups
    sys.modules['EnsembleAnomalyDetector'] = EnsembleAnomalyDetector
    
    print("Intelligence Layer: Namespace binding successful.")
except ImportError as e:
    print(f"Intelligence Layer Binding Error: {e}")

# 3. Model Configuration
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
            # The unpickler will now find the class in Step 2
            detector = joblib.load(self.model_path)
            print(f"Ensemble FL Model loaded successfully from {self.model_path}")
            return detector
        except Exception as e:
            print(f"Fatal Error: Intelligence Layer could not be unpickled: {e}")
            return None

    def score_access(self, context: dict) -> float:
        try:
            current_dt = datetime.now()
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
            
            if self.detector and hasattr(self.detector, 'predict_proba'):
                score = float(self.detector.predict_proba(df)[0])
                print(f"Inference Score: {score:.4f}")
                return score
            return 0.0
        except Exception as e:
            print(f"Inference Error: {e}")
            return 0.0