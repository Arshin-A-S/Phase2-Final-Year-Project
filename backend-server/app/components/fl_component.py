import os
import sys
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime

# 1. Robust Path Resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # app/components
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, '..', '..')) # backend-server

# Ensure the root is in sys.path so 'app.offline_sim' is resolvable
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 2. Absolute Namespace Binding (Critical Mac Fix)
try:
    # Use absolute import to avoid "no known parent package" error
    from app.offline_sim.enhanced_features import EnsembleAnomalyDetector
    
    import __main__
    import app.server
    
    # Inject the class into every namespace joblib might search
    setattr(__main__, 'EnsembleAnomalyDetector', EnsembleAnomalyDetector)
    setattr(app.server, 'EnsembleAnomalyDetector', EnsembleAnomalyDetector)
    
    # Also register the simulation module path to be safe
    if 'app.offline_sim.enhanced_features' in sys.modules:
        setattr(sys.modules['app.offline_sim.enhanced_features'], 'EnsembleAnomalyDetector', EnsembleAnomalyDetector)
        
    print("Intelligence Layer: Namespace binding successful.")
except ImportError as e:
    print(f"Intelligence Layer Binding Error: {e}")
    # Fallback definition if import fails
    class EnsembleAnomalyDetector: pass

# 3. Model Path Configuration
ENSEMBLE_MODEL_PATH = os.path.join(PROJECT_ROOT, "app", "trained_ensemble_detector.pkl")

class FLComponent:
    def __init__(self, model_path: str = ENSEMBLE_MODEL_PATH):
        self.model_path = os.path.abspath(model_path)
        self.threshold = 0.5 
        self.detector = self._load_model()

    def _load_model(self):
        """Loads the Ensemble Intelligence Layer (94.2% Accuracy)."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        try:
            # The unpickler uses the class we injected in Step 2
            detector = joblib.load(self.model_path)
            print(f"Ensemble FL Model loaded from {self.model_path}")
            return detector
        except Exception as e:
            print(f"Fatal Error: Intelligence Layer could not be unpickled: {e}")
            return None

    def score_access(self, context: dict) -> float:
        """Scores an access request using the Ensemble engine."""
        try:
            current_dt = datetime.now()
            # Feature extraction for Ensemble inference
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