#!/usr/bin/env python
"""Feature extractor for PhiUSIIL dataset compatibility."""

import numpy as np
from urllib.parse import urlparse
import re


class PhiUSIILFeatureExtractor:
    """Extract 50 features compatible with PhiUSIIL dataset."""
    
    @staticmethod
    def extract_features(url):
        """Extract 50 features from URL."""
        features = []
        
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path.split('/')[0]
            path = parsed.path
            full_url = url
            
            # URL Length (1)
            features.append(len(url))
            
            # Domain metrics (2-4)
            features.append(len(domain))
            features.append(len(domain) if domain else 0)  # Domain Length again for compatibility
            
            # Path metrics (5-6)
            features.append(len(path))
            features.append(len(path) if path else 0)
            
            # IP detection (7)
            is_ip = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+', domain) else 0
            features.append(is_ip)
            
            # TLD metrics (8-10)
            tld = domain.split('.')[-1] if '.' in domain else ""
            features.append(len(tld))
            features.append(len(tld) if tld else 0)
            features.append(len(tld) if tld else 0)
            
            # Subdomain count (11)
            subdomains = domain.count('.')
            features.append(subdomains)
            
            # Special characters (12-20)
            features.append(url.count('='))  # Equals
            features.append(url.count('?'))  # Question mark
            features.append(url.count('&'))  # Ampersand
            spec_chars = len(re.findall(r'[^a-zA-Z0-9\-._/:?=&]', url))
            features.append(spec_chars)  # Other special chars
            features.append(spec_chars / max(len(url), 1))  # Special char ratio
            features.append(url.count('-'))  # Dashes
            features.append(url.count('.'))  # Dots
            features.append(url.count('_'))  # Underscores
            features.append(len(re.findall(r'[^\x00-\x7F]', url)))  # Non-ASCII
            
            # HTTPS check (21)
            features.append(1 if url.startswith('https') else 0)
            
            # Numbers and letters (22-28)
            num_count = sum(1 for c in url if c.isdigit())
            letter_count = sum(1 for c in url if c.isalpha())
            features.append(letter_count)
            features.append(letter_count / max(len(url), 1))
            features.append(num_count)
            features.append(num_count / max(len(url), 1))
            features.append(len(domain.split('.')))  # Dot count in domain
            features.append(domain.count('-'))  # Dashes in domain
            features.append(domain.count('_'))  # Underscores in domain
            
            # URL entropy and patterns (29-35)
            url_entropy = PhiUSIILFeatureExtractor._entropy(url[:50])  # First 50 chars
            features.append(url_entropy)
            features.append(1 if re.search(r'http.*http', url) else 0)  # Double http
            features.append(1 if re.search(r'www.*www', url) else 0)  # Double www
            features.append(url.count('//'))  # Slash slashes
            features.append(1 if 'login' in url.lower() else 0)  # Login keyword
            features.append(1 if 'confirm' in url.lower() else 0)  # Confirm keyword
            features.append(1 if 'verify' in url.lower() else 0)  # Verify keyword
            
            # Domain characteristics (36-45)
            domain_entropy = PhiUSIILFeatureExtractor._entropy(domain)
            features.append(domain_entropy)
            features.append(1 if re.match(r'^[a-z]+$', domain, re.I) else 0)  # Only letters
            features.append(1 if '-' in domain else 0)  # Dash in domain
            features.append(domain.count('-'))  # Dash count
            features.append(1 if re.search(r'\d{1,3}\.\d{1,3}', domain) else 0)  # IP-like but incomplete
            features.append(len(re.findall(r'[a-z]\d', domain, re.I)))  # Letter-number transitions
            features.append(1 if domain.endswith('.com') else 0)  # Common TLD
            features.append(1 if domain.endswith('.net') else 0)  # .net
            features.append(1 if domain.endswith('.org') else 0)  # .org
            features.append(1 if any(c in domain for c in ['@', '!', '#']) else 0)  # Suspicious chars
            
            # Path characteristics (46-50)
            features.append(len(path.split('/')))  # Path segments
            features.append(1 if path.count('/') > 5 else 0)  # Deep path
            features.append(1 if '~' in path else 0)  # Tilde in path
            features.append(path.count('.'))  # Dots in path
            features.append(1 if '../' in path else 0)  # Parent directory
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            features = [0] * 50
        
        # Ensure we have exactly 50 features
        features = features[:50]
        while len(features) < 50:
            features.append(0)
        
        return np.array(features, dtype=np.float64)
    
    @staticmethod
    def _entropy(s):
        """Calculate Shannon entropy."""
        if not s:
            return 0.0
        entropy = 0.0
        for c in set(s):
            p = s.count(c) / len(s)
            entropy -= p * np.log2(p)
        return entropy
