import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from joblib import dump, load

try:
    from tensorflow import keras
    from tensorflow.keras import layers, models
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from .feature_extractor import URLFeatureExtractor


class ModelTrainer:
    """Trains phishing detection models."""
    
    @staticmethod
    def create_demo_dataset():
        """Create small demo dataset."""
        data = [
            ("http://google.com", 0),
            ("https://www.facebook.com/login", 0),
            ("http://secure-login-paypal.com", 1),
            ("http://paypal.com.sign-in.verify.com", 1),
            ("https://github.com/", 0),
            ("http://123.45.67.89/confirm", 1),
            ("https://secure.appleid.apple.com", 0),
            ("https://bankofamerica.verify-account.com", 1),
            ("https://ebay.com/offer", 0),
            ("http://free-gift-card.app", 1),
            ("https://amazon.com", 0),
            ("http://urgent-update-account.info", 1),
        ]
        return pd.DataFrame(data, columns=["url", "label"])
    
    @staticmethod
    def load_dataset(data_path: str = None) -> pd.DataFrame:
        """Load dataset from CSV or return demo."""
        if data_path and Path(data_path).exists():
            df = pd.read_csv(data_path)
            if "url" not in df.columns or "label" not in df.columns:
                raise ValueError("CSV must have 'url' and 'label' columns")
            return df
        return ModelTrainer.create_demo_dataset()
    
    @staticmethod
    def train_sklearn_model(data_path=None, output_path="models/sklearn_model.joblib", test_ratio=0.2):
        """Train scikit-learn Logistic Regression model."""
        df = ModelTrainer.load_dataset(data_path)
        X, feature_names = URLFeatureExtractor.batch_extract_features(df["url"].tolist())
        y = df["label"].values
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=42, stratify=y
        )
        
        pipeline = Pipeline([
            ("scaler", StandardScaler()),
            ("clf", LogisticRegression(max_iter=1000, solver="liblinear")),
        ])
        
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)
        
        accuracy = accuracy_score(y_test, y_pred)
        report = classification_report(y_test, y_pred, digits=4)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        dump({"pipeline": pipeline, "features": feature_names}, output_path)
        
        return {
            "model": pipeline,
            "accuracy": accuracy,
            "report": report,
            "path": output_path,
            "type": "sklearn"
        }
    
    @staticmethod
    def train_keras_model(data_path=None, output_path="models/keras_model.h5", epochs=20, batch_size=8):
        """Train Keras/TensorFlow neural network model."""
        if not KERAS_AVAILABLE:
            raise RuntimeError("TensorFlow/Keras not available. Install: pip install tensorflow")
        
        df = ModelTrainer.load_dataset(data_path)
        X, feature_names = URLFeatureExtractor.batch_extract_features(df["url"].tolist())
        y = df["label"].values
        
        # Normalize features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Build neural network
        model = models.Sequential([
            layers.Dense(64, activation='relu', input_shape=(X_train.shape[1],)),
            layers.Dropout(0.3),
            layers.Dense(32, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(16, activation='relu'),
            layers.Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer='adam',
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        history = model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        
        y_pred = (model.predict(X_test) > 0.5).astype(int).flatten()
        accuracy = accuracy_score(y_test, y_pred)
        
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        model.save(output_path)
        
        # Save scaler
        scaler_path = output_path.replace(".h5", "_scaler.joblib")
        dump(scaler, scaler_path)
        
        return {
            "model": model,
            "accuracy": accuracy,
            "history": history,
            "path": output_path,
            "type": "keras"
        }
