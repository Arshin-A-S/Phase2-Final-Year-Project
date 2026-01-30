import pandas as pd
import joblib
import os
import sys
import json
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Path Setup
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))

if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the custom class for joblib deserialization
from app.offline_sim.enhanced_federated_train_eval import EnsembleAnomalyDetector

def validate_intelligence():
    print("=== Intelligence Pillar: Ensemble FL Accuracy, ROC & FPR ===")
    
    model_path = os.path.join(project_root, "app", "trained_ensemble_detector.pkl")
    data_path = os.path.join(project_root, "data", "synthetic_events.csv")
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}")
        return

    try:
        detector = joblib.load(model_path)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return
    
    # Load and preprocess synthetic data using the detector's internal pipeline
    df = pd.read_csv(data_path)
    X, df_enhanced = detector.prepare_data(df)
    
    # Map labels: 1 = Anomaly (label 0 in original), 0 = Normal (label 1 in original)
    y_true = (df_enhanced['label'] == 0).astype(int)
    
    # Generate weighted anomaly scores (probabilities)
    test_probs = detector.predict_proba(df)
    
    # Apply decision threshold for classification metrics
    threshold = 0.5 
    y_pred = (test_probs >= threshold).astype(int)
    
    # Calculate standard performance metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    roc_auc = roc_auc_score(y_true, test_probs)
    
    # NEW: Calculate False Positive Rate (FPR)
    # tn: True Negatives (Legitimate allowed)
    # fp: False Positives (Legitimate blocked)
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred).ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    perf_data = {
        "layer": "Intelligence",
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "fpr": round(fpr, 4),
        "threshold": threshold
    }
    
    print(f"[+] Detection Accuracy: {acc*100:.2f}%")
    print(f"[+] ROC-AUC Score:     {roc_auc:.4f}")
    print(f"[+] False Positive Rate: {fpr:.4f}")
    print(f"[+] F1-Score:          {f1:.4f}")

    # Save metrics to the results directory
    output_dir = os.path.join(current_dir, "results")
    os.makedirs(output_dir, exist_ok=True)
    results_file = os.path.join(output_dir, "intelligence_performance.json")
    
    with open(results_file, "w") as f:
        json.dump(perf_data, f, indent=4)
        
    print(f"[!] Results saved to {results_file}")

if __name__ == "__main__":
    validate_intelligence()