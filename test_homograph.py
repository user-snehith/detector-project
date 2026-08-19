#!/usr/bin/env python3
"""
Test script for homograph detection functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.feature_extractor import URLFeatureExtractor

def test_homograph_detection():
    """Test homograph detection with various examples"""

    extractor = URLFeatureExtractor()

    # Test cases: (url, expected_homograph, description)
    test_cases = [
        ("https://google.com", False, "Normal Google domain"),
        ("https://g00gle.com", True, "Zero instead of O"),
        ("https://amaz0n.com", True, "Zero instead of O"),
        ("https://rnicrosoft.com", True, "rn instead of m"),
        ("https://paypa1.com", True, "1 instead of l"),
        ("https://faceb00k.com", True, "00 instead of OO"),
        ("https://netfl1x.com", True, "1 instead of i"),
        ("https://instagrarn.com", True, "rn instead of m"),
        ("https://tw1tter.com", True, "1 instead of i"),
        ("https://y0utube.com", True, "0 instead of O"),
        ("https://legit-site.com", False, "Normal legitimate site"),
        ("https://suspicious-site.co.uk", False, "Normal suspicious site"),
    ]

    print("🧪 Testing Homograph Detection")
    print("=" * 50)

    passed = 0
    total = len(test_cases)

    for url, expected, description in test_cases:
        try:
            # Extract features
            feature_array, feature_names = extractor.extract_features(url)

            # Convert to dictionary for easier access
            features = dict(zip(feature_names, feature_array))

            # Check homograph detection
            is_homograph = bool(features.get('is_homograph', False))
            similarity_score = features.get('homograph_similarity_score', 0.0)
            has_obfuscation = bool(features.get('has_obfuscation_chars', False))

            # Test result
            success = is_homograph == expected

            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status} {url}")
            print(f"    Expected: {expected}, Got: {is_homograph}")
            print(f"    Similarity: {similarity_score:.3f}, Obfuscation: {has_obfuscation}")
            print(f"    Description: {description}")

            if success:
                passed += 1
            print()

        except Exception as e:
            print(f"❌ ERROR {url}: {str(e)}")
            print()

    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("🎉 All homograph detection tests passed!")
        return True
    else:
        print("⚠️  Some tests failed. Check implementation.")
        return False

def test_feature_extraction():
    """Test that feature extraction works without errors"""

    extractor = URLFeatureExtractor()

    test_urls = [
        "https://google.com",
        "https://g00gle.com",
        "https://example.co.uk/path?param=value",
        "http://192.168.1.1/admin",
        "https://sub.domain.example.com/path/to/file.html",
    ]

    print("\n🔧 Testing Feature Extraction")
    print("=" * 50)

    for url in test_urls:
        try:
            feature_array, feature_names = extractor.extract_features(url)
            features = dict(zip(feature_names, feature_array))
            feature_count = len(features)
            print(f"✅ {url}: {feature_count} features extracted")

            # Check for homograph features
            homograph_features = [k for k in features.keys() if 'homograph' in k.lower() or 'obfuscation' in k.lower()]
            if homograph_features:
                print(f"    Homograph features: {homograph_features}")

        except Exception as e:
            print(f"❌ {url}: ERROR - {str(e)}")

    print("\nFeature extraction test completed.")

if __name__ == "__main__":
    print("🚀 Starting Homograph Detection Tests\n")

    # Test homograph detection
    homograph_success = test_homograph_detection()

    # Test feature extraction
    test_feature_extraction()

    print("\n" + "=" * 50)
    if homograph_success:
        print("🎯 All tests completed successfully!")
        sys.exit(0)
    else:
        print("⚠️  Tests completed with failures.")
        sys.exit(1)
