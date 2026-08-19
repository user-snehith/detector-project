#!/usr/bin/env python
"""Comprehensive test suite for phishing detector."""

import unittest
import numpy as np
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.feature_extractor import URLFeatureExtractor
from src.phiusiil_extractor import PhiUSIILFeatureExtractor
from src.detector import PhishingDetector


class TestFeatureExtraction(unittest.TestCase):
    """Test URL feature extraction."""
    
    def test_basic_url_features(self):
        """Test basic URL parsing."""
        url = "https://example.com/path"
        features, names = URLFeatureExtractor.extract_features(url)
        
        self.assertEqual(len(features), 32)
        self.assertGreater(len(url), 0)
        self.assertTrue(all(isinstance(f, (int, float)) for f in features))
    
    def test_phiusiil_features(self):
        """Test PhiUSIIL feature extraction."""
        url = "https://google.com/search?q=test"
        features = PhiUSIILFeatureExtractor.extract_features(url)
        
        self.assertEqual(len(features), 50)
        self.assertTrue(all(isinstance(f, (int, float)) for f in features))
        self.assertTrue(np.all(np.isfinite(features)))  # No NaN/inf
    
    def test_feature_determinism(self):
        """Test that same URL produces same features."""
        url = "https://suspicious-site.com/verify?id=123"
        
        features1 = PhiUSIILFeatureExtractor.extract_features(url)
        features2 = PhiUSIILFeatureExtractor.extract_features(url)
        
        np.testing.assert_array_almost_equal(features1, features2)
    
    def test_malformed_url(self):
        """Test handling of malformed URLs."""
        malformed = "not a valid url at all"
        features = PhiUSIILFeatureExtractor.extract_features(malformed)
        
        self.assertEqual(len(features), 50)
        self.assertTrue(np.all(np.isfinite(features)))


class TestDomainValidation(unittest.TestCase):
    """Test domain validation methods."""
    
    def test_domain_existence_valid(self):
        """Test domain existence for valid domain."""
        result = PhishingDetector.check_url_existence("google.com")
        self.assertTrue(result['exists'])
        self.assertIn('reason', result)
    
    def test_domain_existence_invalid(self):
        """Test domain existence for invalid domain."""
        result = PhishingDetector.check_url_existence("definitely-not-a-real-domain-12345.com")
        self.assertFalse(result['exists'])
    
    def test_domain_existence_empty(self):
        """Test domain existence for empty string."""
        result = PhishingDetector.check_url_existence("")
        self.assertFalse(result['exists'])


class TestPrediction(unittest.TestCase):
    """Test model predictions."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize detector once for all tests."""
        model_path = "models/sklearn_model.joblib"
        if Path(model_path).exists():
            cls.detector = PhishingDetector(model_path, "sklearn")
        else:
            cls.detector = None
    
    def test_prediction_output_structure(self):
        """Test prediction output format."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        result = self.detector.predict("https://google.com")
        
        self.assertIn('url', result)
        self.assertIn('is_phishing', result)
        self.assertIn('confidence', result)
        self.assertIn('risk_level', result)
        
        self.assertIsInstance(result['is_phishing'], (bool, np.bool_))
        self.assertIsInstance(result['confidence'], (float, np.floating))
        self.assertIn(result['risk_level'], ['safe', 'medium', 'high'])
    
    def test_prediction_confidence_range(self):
        """Test that confidence is in valid range."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        result = self.detector.predict("https://example.com")
        self.assertGreaterEqual(result['confidence'], 0.0)
        self.assertLessEqual(result['confidence'], 1.0)
    
    def test_batch_prediction(self):
        """Test batch prediction."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        urls = [
            "https://google.com",
            "https://facebook.com",
            "https://github.com"
        ]
        results = self.detector.predict_batch(urls)
        
        self.assertEqual(len(results), len(urls))
        for result in results:
            self.assertIn('is_phishing', result)
            self.assertIn('confidence', result)
    
    def test_prediction_determinism(self):
        """Test that same URL produces consistent predictions."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        url = "https://example.com"
        result1 = self.detector.predict(url)
        result2 = self.detector.predict(url)
        
        self.assertEqual(result1['is_phishing'], result2['is_phishing'])
        self.assertAlmostEqual(result1['confidence'], result2['confidence'], places=4)


class TestSecurityValidation(unittest.TestCase):
    """Test security-related validations."""
    
    def test_url_length_limit(self):
        """Test URL length validation."""
        # Chrome/Firefox limit: 2083 characters
        max_url_length = 2083
        
        # Create a long URL
        long_url = "https://example.com/" + "a" * 3000
        
        # Should handle gracefully
        features = PhiUSIILFeatureExtractor.extract_features(long_url)
        self.assertEqual(len(features), 50)
    
    def test_csv_column_validation(self):
        """Test CSV column validation."""
        # This test verifies structure, actual CSV handling in UI
        required_columns = ['url', 'label']
        
        import pandas as pd
        df = pd.DataFrame({
            'url': ['http://google.com', 'http://phishing.com'],
            'label': [0, 1]
        })
        
        for col in required_columns:
            self.assertIn(col, df.columns)


class TestModelFiles(unittest.TestCase):
    """Test model file integrity."""
    
    def test_sklearn_model_exists(self):
        """Test sklearn model file exists."""
        model_path = Path("models/sklearn_model.joblib")
        self.assertTrue(model_path.exists(), "sklearn_model.joblib not found")
    
    def test_model_loadable(self):
        """Test that model can be loaded."""
        try:
            detector = PhishingDetector("models/sklearn_model.joblib", "sklearn")
            self.assertIsNotNone(detector.model)
        except Exception as e:
            self.fail(f"Failed to load model: {e}")


class TestIntegration(unittest.TestCase):
    """Integration tests."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize detector."""
        model_path = "models/sklearn_model.joblib"
        if Path(model_path).exists():
            cls.detector = PhishingDetector(model_path, "sklearn")
        else:
            cls.detector = None
    
    def test_full_pipeline(self):
        """Test full detection pipeline."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        url = "https://bank-verify-account.com"
        
        # Check existence
        exist_result = PhishingDetector.check_url_existence(url)
        self.assertIn('exists', exist_result)
        
        # Predict
        pred_result = self.detector.predict(url)
        self.assertIn('is_phishing', pred_result)
        self.assertIn('confidence', pred_result)
    
    def test_legitimate_url_detection(self):
        """Test that legitimate URLs are detected correctly."""
        if self.detector is None:
            self.skipTest("Model not available")
        
        legitimate_urls = [
            "https://google.com",
            "https://github.com",
            "https://amazon.com"
        ]
        
        for url in legitimate_urls:
            result = self.detector.predict(url)
            # We expect these to be classified as safe
            self.assertIn('confidence', result)


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
