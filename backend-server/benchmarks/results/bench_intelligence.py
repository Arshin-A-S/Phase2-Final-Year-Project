import pandas as pd
import pickle
import os
import sys
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def validate_intelligence():
    print("=== Intelligence Pillar: Ensemble FL Accuracy ===")
    
    model_path = "../trained_ensemble_detector.pkl"
    data_path = "../../data/synthetic_events.csv"
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    # Load Model
    with open(model_path, "rb") as f:
        detector = pickle.load(f)
    
    # Load Behavioral Data
    df = pd.read_csv(data_path)
    
    # Pre-process features for prediction
    df['loc_c'] = df['location'].astype('category').cat.codes
    df['dev_c'] = df['device_id'].astype('category').cat.codes
    df['dept_c'] = df['department'].astype('category').cat.codes
    
    X = df[['loc_c', 'dev_c', 'dept_c']]
    y_true = df['is_anomaly'] 
    
    # Score access requests
    scores = detector.decision_function(X)
    threshold = 0.6 # Optimized for your framework
    y_pred = [1 if s >= threshold else 0 for s in scores]
    
    # Metrics calculation
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    
    print(f"[+] Detection Accuracy: {acc*100:.2f}%")
    print(f"[+] Precision: {prec:.4f}")
    print(f"[+] Recall:    {rec:.4f}")
    print(f"[+] F1-Score:  {f1:.4f}")

if __name__ == "__main__":
    validate_intelligence()