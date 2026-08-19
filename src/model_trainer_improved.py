import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, VotingClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, roc_auc_score
from joblib import dump, load

try:
    from tensorflow import keras
    from tensorflow.keras import layers, models
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from .feature_extractor import URLFeatureExtractor


class ModelTrainerImproved:
    """Trains phishing detection models with advanced ensemble techniques."""
    
    @staticmethod
    def create_expanded_dataset():
        """Create expanded demo dataset with more examples."""
        data = [
            # Safe URLs
            ("http://google.com", 0),
            ("https://www.facebook.com/login", 0),
            ("https://github.com/", 0),
            ("https://example.com/account", 0),
            ("https://secure.appleid.apple.com", 0),
            ("https://ebay.com/offer", 0),
            ("https://amazon.com", 0),
            ("https://wikipedia.org", 0),
            ("https://stackoverflow.com", 0),
            ("https://linkedin.com", 0),
            ("https://twitter.com", 0),
            ("https://reddit.com", 0),
            
            # Phishing URLs
            ("http://paypal.com.sign-in.verify.com", 1),
            ("http://secure-login-paypal.com", 1),
            ("http://123.45.67.89/confirm", 1),
            ("http://bankofamerica.verify-account.com", 1),
            ("http://free-gift-card.app", 1),
            ("http://urgent-update-info.com", 1),
            ("http://microsft-verify.tk", 1),  # Typosquatting
            ("http://applle-id-verify.ml", 1),  # Typosquatting
            ("http://gogle.com/login", 1),  # Typosquatting
            ("http://amaz0n.verify.com", 1),  # Mixed domains
        ]
        return pd.DataFrame(data, columns=["url", "label"])
    
    @staticmethod
    def train_ensemble_model(data_path=None, output_path="models/sklearn_model.joblib"):
        """Train ensemble model combining multiple algorithms for better accuracy."""
        print("Loading dataset...")
        if data_path and Path(data_path).exists():
            df = pd.read_csv(data_path)
        else:
            df = ModelTrainerImproved.create_expanded_dataset()
        
        print(f"Dataset size: {len(df)} URLs")
        print(f"Safe URLs: {(df['label'] == 0).sum()}, Phishing URLs: {(df['label'] == 1).sum()}")
        
        print("\nExtracting features...")
        X, feature_names = URLFeatureExtractor.batch_extract_features(df["url"].tolist())
        y = df["label"].values
        
        print(f"Features extracted: {len(feature_names)} features per URL")
        print(f"Feature names: {', '.join(feature_names[:10])} ...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )
        
        print(f"\nTraining set: {len(X_train)} URLs, Test set: {len(X_test)} URLs")
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        print("\nTraining ensemble models...")
        
        # Base learners
        lr = LogisticRegression(max_iter=1000, solver="lbfgs", random_state=42, C=0.1)
        rf = RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42, n_jobs=-1)
        gb = GradientBoostingClassifier(n_estimators=100, max_depth=7, learning_rate=0.05, random_state=42)
        
        # Ensemble voting classifier
        ensemble = VotingClassifier(
            estimators=[('lr', lr), ('rf', rf), ('gb', gb)],
            voting='soft'
        )
        
        ensemble.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred = ensemble.predict(X_test_scaled)
        y_pred_proba = ensemble.predict_proba(X_test_scaled)[:, 1]
        
        # Evaluation
        accuracy = accuracy_score(y_test, y_pred)
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        report = classification_report(y_test, y_pred, digits=4)
        
        # Cross-validation
        cv_scores = cross_val_score(ensemble, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        print(f"\n✅ Model Performance:")
        print(f"Accuracy: {accuracy:.4f}")
        print(f"ROC-AUC: {roc_auc:.4f}")
        print(f"Cross-validation scores: {cv_scores}")
        print(f"Mean CV accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
        
        print("\nClassification Report:")
        print(report)
        
        # Save model
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        dump({
            "pipeline": ensemble,
            "scaler": scaler,
            "features": feature_names,
            "accuracy": accuracy,
            "roc_auc": roc_auc,
            "cv_scores": cv_scores,
            "feature_count": len(feature_names)
        }, output_path)
        
        print(f"\n✅ Model saved to: {output_path}")
        
        return {
            "model": ensemble,
            "accuracy": accuracy,
            "roc_auc": roc_auc,
            "cv_scores": cv_scores,
            "report": report,
            "path": output_path,
            "type": "sklearn_ensemble",
            "feature_count": len(feature_names)
        }
