"""Phishing detector package."""
from .detector import PhishingDetector
from .feature_extractor import URLFeatureExtractor
from .model_trainer import ModelTrainer

__all__ = ["PhishingDetector", "URLFeatureExtractor", "ModelTrainer"]
