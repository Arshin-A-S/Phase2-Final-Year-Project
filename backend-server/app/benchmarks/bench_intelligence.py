import pandas as pd
import pickle
import os
import sys
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

# Ensure the project root is in sys.path so we can import from 'app'
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- CRITICAL FIX ---
# Import the custom class so Pickle can find the definition during unpickling
from app.components.fl_component import EnsembleAnomalyDetector
# --------------------

def validate_intelligence():
    print("=== Intelligence Pillar: Ensemble FL Accuracy ===")
    
    model_path = os.path.join(project_root, "app", "trained_ensemble_detector.pkl")
    data_path = os.path.join(project_root, "data", "synthetic_events.csv")
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    # Load the trained model
    with open(model_path, "rb") as f:
        detector = pickle.load(f)
    
    # Load and preprocess synthetic data
    df = pd.read_csv(data_path)
    df['loc_c'] = df['location'].astype('category').cat.codes
    df['dev_c'] = df['device_id'].astype('category').cat.codes
    df['dept_c'] = df['department'].astype('category').cat.codes
    
    X = df[['loc_c', 'dev_c', 'dept_c']]
    y_true = df['is_anomaly'] 
    
    # Generate scores and apply decision threshold
    scores = detector.decision_function(X)
    threshold = 0.6 
    y_pred = [1 if s >= threshold else 0 for s in scores]
    
    # Calculate performance metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    perf_data = {
        "layer": "Intelligence",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4)
    }
    
    print(f"[+] Detection Accuracy: {acc*100:.2f}%")
    print(f"[+] F1-Score:  {f1:.4f}")

    # Save metrics to the results directory
    output_dir = os.path.join(current_dir, "results")
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, "intelligence_performance.json")
    
    with open(results_file, "w") as f:
        json.dump(perf_data, f, indent=4)
        
    print(f"[!] Results saved to {results_file}")

if __name__ == "__main__":
    validate_intelligence()