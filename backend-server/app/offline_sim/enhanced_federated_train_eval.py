import json
import numpy as np
import pandas as pd
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, accuracy_score
from sklearn.model_selection import train_test_split
from .enhanced_features import create_enhanced_features

class EnsembleAnomalyDetector:
    def __init__(self):
        # Initializing the ensemble models as per the architectural requirement
        self.models = {
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42),
            'logistic_regression': LogisticRegression(random_state=42, max_iter=1000),
            'isolation_forest': IsolationForest(contamination=0.1, random_state=42),
            'one_class_svm': OneClassSVM(kernel='rbf', nu=0.1)
        }
        self.scaler = StandardScaler()
        self.weights = {
            'random_forest': 0.35,
            'gradient_boosting': 0.35,
            'logistic_regression': 0.2,
            'isolation_forest': 0.05,
            'one_class_svm': 0.05
        }
        self.feature_cols = [
            'hour_sin', 'hour_cos', 'is_weekend', 'is_night', 'is_business_hours',
            'location_encoded', 'device_encoded', 'department_encoded',
            'location_frequency', 'device_frequency',
            'location_user_pattern', 'device_user_pattern', 'hour_user_pattern'
        ]

    def prepare_data(self, df: pd.DataFrame):
        """Prepares the feature matrix for training or inference."""
        df_enhanced = create_enhanced_features(df)
        X = df_enhanced[self.feature_cols].fillna(0).values
        return X, df_enhanced

    def fit(self, df: pd.DataFrame):
        """Trains the ensemble models on provided data."""
        print("Starting Ensemble Training...")
        X, df_enhanced = self.prepare_data(df)
        # In this dataset, label=1 is normal, label=0 is anomaly. 
        # We map it so 1 = Anomaly for the classifier.
        y = (df_enhanced['label'] == 0).astype(int)
        
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Supervised Models
        for name in ['random_forest', 'gradient_boosting', 'logistic_regression']:
            print(f"  Training {name}...")
            self.models[name].fit(X_scaled, y)
            
        # Train Unsupervised Models (on normal data only)
        normal_indices = np.where(y == 0)[0]
        for name in ['isolation_forest', 'one_class_svm']:
            print(f"  Training {name}...")
            self.models[name].fit(X_scaled[normal_indices])
            
        print("Ensemble training complete.")

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        """Calculates a weighted anomaly score from the ensemble."""
        X, _ = self.prepare_data(df)
        X_scaled = self.scaler.transform(X)
        
        scores = np.zeros(X_scaled.shape[0])
        
        # Collect Supervised Probabilities
        for name in ['random_forest', 'gradient_boosting', 'logistic_regression']:
            scores += self.weights[name] * self.models[name].predict_proba(X_scaled)[:, 1]
            
        # Collect Unsupervised Scores (Normalized to 0-1)
        iso_raw = self.models['isolation_forest'].score_samples(X_scaled)
        iso_norm = (iso_raw - iso_raw.min()) / (iso_raw.max() - iso_raw.min() + 1e-8)
        scores += self.weights['isolation_forest'] * (1 - iso_norm)
        
        svm_raw = self.models['one_class_svm'].score_samples(X_scaled)
        svm_norm = (svm_raw - svm_raw.min()) / (svm_raw.max() - svm_raw.min() + 1e-8)
        scores += self.weights['one_class_svm'] * (1 - svm_norm)
        
        return scores

def run_training():
    # Load dataset
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, "data", "synthetic_events.csv")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"Missing training data at {data_path}")
        
    df = pd.read_csv(data_path)
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=42)
    
    detector = EnsembleAnomalyDetector()
    detector.fit(train_df)
    
    # Evaluation
    test_probs = detector.predict_proba(test_df)
    test_labels = (test_df['label'] == 0).astype(int)
    auc = roc_auc_score(test_labels, test_probs)
    
    # Target Accuracy Threshold
    accuracy = accuracy_score(test_labels, (test_probs > 0.5).astype(int))
    
    print(f"\nFINAL METRICS:")
    print(f"ROC-AUC: {auc:.4f}")
    print(f"Accuracy: {accuracy * 100:.1f}%")
    
    # Save the files needed for production
    joblib.dump(detector, 'trained_ensemble_detector.pkl')
    
    meta = {
        "version": 3,
        "performance": {"accuracy": accuracy, "auc": auc},
        "feature_cols": detector.feature_cols
    }
    with open('enhanced_fl_model.json', 'w') as f:
        json.dump(meta, f, indent=2)
        
    print(f"\nEnsemble model saved as 'trained_ensemble_detector.pkl'")

if __name__ == "__main__":
    run_training()