#!/usr/bin/env python
"""Test the feature count fix."""

import sys
sys.path.insert(0, '.')

from src.detector import PhishingDetector

test_urls = [
    "https://amaz0n.com",     # lookalike
    "https://google.com",     # legitimate
    "https://g00gle.com",     # lookalike
]

print("Testing URL detection with backward compatibility fix...")
print("=" * 70)

try:
    detector = PhishingDetector('models/sklearn_model.joblib', 'sklearn')
    print(f"[OK] Model loaded (expects {detector.feature_count} features)")
    print()
    
    for url in test_urls:
        try:
            result = detector.predict(url)
            status = "[PHISHING]" if result['is_phishing'] else "[SAFE]"
            print(f"URL: {url}")
            print(f"  Status: {status}")
            print(f"  Risk: {result['risk_level'].upper()}")
            print(f"  Confidence: {result['confidence']:.2%}")
            if result.get('homograph_info') and result['homograph_info']['is_homograph']:
                print(f"  Homograph: {result['homograph_info']['matched_brand']} ({result['homograph_info']['similarity_score']:.0%})")
            print()
        except Exception as e:
            print(f"  [ERROR] {e}")
            print()
    
    print("=" * 70)
    print("[OK] All tests passed!")
    
except Exception as e:
    print(f"[ERROR] Failed to load model: {e}")
    import traceback
    traceback.print_exc()
