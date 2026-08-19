#!/usr/bin/env python
"""Ensemble model stacking with uncertainty calibration."""

import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import classification_report, accuracy_score, roc_auc_score
from joblib import dump, load
import time

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False


class EnsembleDetector:
    """Ensemble model with uncertainty handling and calibration."""
    
    def __init__(self, model_path: str = None):
        """Load or initialize ensemble."""
        self.rf_model = None
        self.gb_model = None
        self.xgb_model = None
        self.scaler = None
        self.uncertainty_threshold = 0.65  # Threshold for manual review
        
        if model_path and Path(model_path).exists():
            self.load_ensemble(model_path)
    
    def load_ensemble(self, model_path: str):
        """Load pre-trained ensemble."""
        ensemble_data = load(model_path)
        self.rf_model = ensemble_data.get('rf_model')
        self.gb_model = ensemble_data.get('gb_model')
        self.xgb_model = ensemble_data.get('xgb_model')
        self.scaler = ensemble_data.get('scaler')
    
    def train_ensemble(self, X_train, X_test, y_train, y_test, output_path: str = "models/ensemble_model.joblib"):
        """Train ensemble with calibration."""
        print("Training ensemble models...")
        
        # Scale features
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Random Forest
        print("  [1/3] Training Random Forest...")
        self.rf_model = RandomForestClassifier(
            n_estimators=150,
            max_depth=15,
            n_jobs=-1,
            random_state=42,
            verbose=1
        )
        self.rf_model.fit(X_train_scaled, y_train)
        rf_pred = self.rf_model.predict(X_test_scaled)
        rf_proba = self.rf_model.predict_proba(X_test_scaled)[:, 1]
        print(f"    RF: Accuracy={accuracy_score(y_test, rf_pred):.4f}, AUC={roc_auc_score(y_test, rf_proba):.4f}")
        
        # Gradient Boosting (with calibration)
        print("  [2/3] Training Gradient Boosting (with calibration)...")
        gb_base = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=8,
            learning_rate=0.1,
            random_state=42,
            verbose=1
        )
        self.gb_model = CalibratedClassifierCV(gb_base, method='sigmoid', cv=5)
        self.gb_model.fit(X_train_scaled, y_train)
        gb_pred = self.gb_model.predict(X_test_scaled)
        gb_proba = self.gb_model.predict_proba(X_test_scaled)[:, 1]
        print(f"    GB: Accuracy={accuracy_score(y_test, gb_pred):.4f}, AUC={roc_auc_score(y_test, gb_proba):.4f}")
        
        # XGBoost (if available)
        if XGBOOST_AVAILABLE:
            print("  [3/3] Training XGBoost (with calibration)...")
            xgb_base = xgb.XGBClassifier(
                n_estimators=100,
                max_depth=8,
                learning_rate=0.1,
                random_state=42,
                verbosity=1,
                use_label_encoder=False,
                eval_metric='logloss'
            )
            self.xgb_model = CalibratedClassifierCV(xgb_base, method='sigmoid', cv=5)
            self.xgb_model.fit(X_train_scaled, y_train)
            xgb_pred = self.xgb_model.predict(X_test_scaled)
            xgb_proba = self.xgb_model.predict_proba(X_test_scaled)[:, 1]
            print(f"    XGB: Accuracy={accuracy_score(y_test, xgb_pred):.4f}, AUC={roc_auc_score(y_test, xgb_proba):.4f}")
        else:
            print("  [3/3] XGBoost not available (install: pip install xgboost)")
        
        # Ensemble voting
        print("\n  Computing ensemble predictions...")
        ensemble_accuracy = self._ensemble_accuracy(X_test_scaled, y_test)
        print(f"  Ensemble Accuracy: {ensemble_accuracy:.4f}")
        
        # Save ensemble
        Path(output_path).parent.mkdir(exist_ok=True)
        ensemble_data = {
            'rf_model': self.rf_model,
            'gb_model': self.gb_model,
            'xgb_model': self.xgb_model if XGBOOST_AVAILABLE else None,
            'scaler': self.scaler,
            'uncertainty_threshold': self.uncertainty_threshold
        }
        dump(ensemble_data, output_path)
        print(f"  Ensemble saved: {output_path}")
        
        return ensemble_accuracy
    
    def predict_with_uncertainty(self, features: np.ndarray) -> dict:
        """Predict with confidence and uncertainty score."""
        if self.scaler is None or self.rf_model is None:
            return {'error': 'Ensemble not initialized'}
        
        # Scale features
        features_scaled = self.scaler.transform([features])[0]
        
        predictions = []
        confidences = []
        
        # Random Forest prediction
        if self.rf_model:
            rf_pred_prob = self.rf_model.predict_proba([features_scaled])[0]
            predictions.append(rf_pred_prob[1])
            confidences.append(max(rf_pred_prob))
        
        # Gradient Boosting prediction
        if self.gb_model:
            gb_pred_prob = self.gb_model.predict_proba([features_scaled])[0]
            predictions.append(gb_pred_prob[1])
            confidences.append(max(gb_pred_prob))
        
        # XGBoost prediction (if available)
        if self.xgb_model:
            xgb_pred_prob = self.xgb_model.predict_proba([features_scaled])[0]
            predictions.append(xgb_pred_prob[1])
            confidences.append(max(xgb_pred_prob))
        
        # Ensemble voting (average)
        ensemble_score = np.mean(predictions)
        avg_confidence = np.mean(confidences)
        
        # Compute uncertainty (std of predictions)
        uncertainty = np.std(predictions)
        
        # Classification
        is_phishing = ensemble_score > 0.5
        
        # Determine action
        action = "classify"
        if uncertainty > self.uncertainty_threshold:
            action = "manual_review"
        
        return {
            'ensemble_score': float(ensemble_score),
            'confidence': float(avg_confidence),
            'uncertainty': float(uncertainty),
            'is_phishing': is_phishing,
            'action': action,
            'model_count': len([p for p in [self.rf_model, self.gb_model, self.xgb_model] if p])
        }
    
    def _ensemble_accuracy(self, X_test_scaled, y_test) -> float:
        """Calculate ensemble accuracy."""
        predictions = []
        for features in X_test_scaled:
            result = self.predict_with_uncertainty(features)
            predictions.append(1 if result['is_phishing'] else 0)
        return accuracy_score(y_test, predictions)
