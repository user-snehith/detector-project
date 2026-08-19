import numpy as np
import socket
from urllib.parse import urlparse
from pathlib import Path
from joblib import load

try:
    from tensorflow.keras.models import load_model
    KERAS_AVAILABLE = True
except ImportError:
    KERAS_AVAILABLE = False

from .feature_extractor import URLFeatureExtractor
from .phiusiil_extractor import PhiUSIILFeatureExtractor


class PhishingDetector:
    """Main phishing detection engine."""
    
    def __init__(self, model_path: str, model_type: str = "sklearn"):
        """
        Initialize detector with trained model.
        
        Args:
            model_path: Path to trained model file
            model_type: Type of model ('sklearn' or 'keras')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.scaler = None
        self._load_model()
    
    def _load_model(self):
        """Load model from disk."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        if self.model_type == "sklearn":
            model_data = load(self.model_path)
            
            # Handle both old and new model formats
            if isinstance(model_data, dict):
                self.model = model_data.get("pipeline") or model_data
                self.scaler = model_data.get("scaler")
                self.features = model_data.get("features", [])
            else:
                self.model = model_data
                self.features = []
            
            # Determine feature count
            try:
                self.feature_count = self.model.named_steps['scaler'].n_features_in_
            except:
                self.feature_count = 32  # Default to old model feature count
                
        elif self.model_type == "keras":
            if not KERAS_AVAILABLE:
                raise RuntimeError("TensorFlow/Keras not available")
            self.model = load_model(self.model_path)
            
            # Load scaler
            scaler_path = self.model_path.replace(".h5", "_scaler.joblib")
            if Path(scaler_path).exists():
                self.scaler = load(scaler_path)
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    @staticmethod
    def check_url_existence(url: str) -> dict:
        """Check whether a URL's domain resolves via DNS."""
        try:
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.netloc
            if not domain:
                return {'exists': False, 'reason': 'Invalid URL'}

            socket.gethostbyname(domain)
            return {'exists': True, 'reason': 'Domain resolves', 'domain': domain}

        except socket.gaierror:
            return {'exists': False, 'reason': 'Domain not found'}
        except Exception as e:
            return {'exists': False, 'reason': f'Check failed: {e}'}

    @staticmethod
    def check_url_reachability(url: str, timeout: int = 5) -> dict:
        """Check URL reachability via HTTP HEAD request."""
        try:
            import requests
        except ImportError:
            return {'reachable': False, 'reason': 'requests library is not installed'}

        try:
            formatted = url if '://' in url else 'http://' + url
            response = requests.head(formatted, allow_redirects=True, timeout=timeout)
            if response.status_code < 400:
                return {'reachable': True, 'reason': f'HTTP {response.status_code}'}
            return {'reachable': False, 'reason': f'HTTP {response.status_code}'}
        except requests.RequestException as e:
            return {'reachable': False, 'reason': f'HTTP error: {e}'}
    
    def predict(self, url: str) -> dict:
        """
        Predict if URL is phishing.
        
        Returns:
            {
                'url': str,
                'is_phishing': bool,
                'confidence': float (0-1),
                'risk_level': 'safe' | 'medium' | 'high',
                'homograph_info': dict (homograph attack details, if applicable)
            }
        """
        # Select feature extractor based on feature count
        if hasattr(self, 'feature_count') and self.feature_count == 50:
            features = PhiUSIILFeatureExtractor.extract_features(url)
        else:
            features, feature_names = URLFeatureExtractor.extract_features(url)
        
        # Check for homograph attacks
        parsed = __import__('tldextract').extract(url if '://' in url else 'http://' + url)
        homograph_info = URLFeatureExtractor.detect_homograph_attack(parsed.domain)
        
        # Handle backward compatibility: trim features if model expects fewer
        if hasattr(self, 'feature_count') and len(features) > self.feature_count:
            features = features[:self.feature_count]
        
        if self.model_type == "sklearn":
            # Scale features if scaler is available
            if self.scaler:
                features = self.scaler.transform([features])[0]
            
            prediction = self.model.predict([features])[0]
            probabilities = self.model.predict_proba([features])[0]
            confidence = max(probabilities)
        elif self.model_type == "keras":
            features_scaled = self.scaler.transform([features]) if self.scaler else [features]
            pred_prob = self.model.predict(features_scaled, verbose=0)[0][0]
            prediction = int(pred_prob > 0.5)
            confidence = float(pred_prob) if prediction == 1 else float(1 - pred_prob)
        
        is_phishing = prediction == 1
        
        # Boost confidence if homograph attack detected
        if homograph_info['is_homograph'] and not is_phishing:
            is_phishing = True
            confidence = max(confidence, 0.75)  # At least 75% confidence for homograph attacks
        
        # Risk level classification
        if is_phishing:
            if homograph_info['is_homograph']:
                risk_level = "high"  # Homograph attacks are always high risk
            elif confidence > 0.8:
                risk_level = "high"
            else:
                risk_level = "medium"
        else:
            risk_level = "safe"
        
        result = {
            "url": url,
            "is_phishing": is_phishing,
            "confidence": float(confidence),
            "risk_level": risk_level,
            "model_type": self.model_type,
            "homograph_info": homograph_info if homograph_info['is_homograph'] else None
        }
        
        return result
    
    def predict_batch(self, urls: list) -> list:
        """Predict multiple URLs."""
        results = []
        for url in urls:
            results.append(self.predict(url))
        return results
