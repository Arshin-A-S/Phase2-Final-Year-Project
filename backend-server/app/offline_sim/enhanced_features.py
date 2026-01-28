# offline_sim/enhanced_features.py

import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from .enhanced_features import create_enhanced_features

def create_enhanced_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create enhanced features for better anomaly detection"""
    # Time-based features
    df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
    df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
    df['is_weekend'] = df['ts'].apply(lambda x: datetime.fromtimestamp(x).weekday() >= 5)
    df['is_night'] = (df['hour'] <= 6) | (df['hour'] >= 22)
    df['is_business_hours'] = (df['hour'] >= 9) & (df['hour'] <= 17)

    # Behavioral features
    df['location_device_combo'] = df['location'] + '_' + df['device']
    df['location_dept_combo'] = df['location'] + '_' + df['department']

    if len(df) == 1:
        # For single-event inference, use defaults
        df['location_user_pattern'] = 1  # Single unique location
        df['device_user_pattern'] = 1    # Single unique device
        df['hour_user_pattern'] = 0      # No standard deviation for single value
        df['label_user_pattern'] = 1     # Assume normal for single event
    else:
        # For training data with multiple rows per user
        user_stats = df.groupby('client_id').agg({
            'location': lambda x: len(x.unique()),
            'device': lambda x: len(x.unique()),
            'hour': 'std',
            'label': 'mean'
        }).add_suffix('_user_pattern')
        df = df.merge(user_stats, left_on='client_id', right_index=True, how='left')
        
        # Fill any remaining NaNs
        df['location_user_pattern'] = df['location_user_pattern'].fillna(1)
        df['device_user_pattern'] = df['device_user_pattern'].fillna(1)
        df['hour_user_pattern'] = df['hour_user_pattern'].fillna(0)
        df['label_user_pattern'] = df['label_user_pattern'].fillna(1)

    # Location frequency (rare locations are more suspicious)
    loc_freq = df['location'].value_counts(normalize=True)
    df['location_frequency'] = df['location'].map(loc_freq).fillna(0.1)  # Default for unknown

    # Device frequency
    dev_freq = df['device'].value_counts(normalize=True)
    df['device_frequency'] = df['device'].map(dev_freq).fillna(0.1)  # Default for unknown

    # Encode categorical variables
    le_loc = LabelEncoder()
    le_dev = LabelEncoder()
    le_dept = LabelEncoder()
    
    df['location_encoded'] = le_loc.fit_transform(df['location'].astype(str))
    df['device_encoded'] = le_dev.fit_transform(df['device'].astype(str))
    df['department_encoded'] = le_dept.fit_transform(df['department'].astype(str))

    return df

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