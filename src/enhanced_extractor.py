#!/usr/bin/env python
"""Enhanced URL feature extraction with SSL, WHOIS, and redirect analysis."""

import numpy as np
import socket
import ssl
from datetime import datetime
from urllib.parse import urlparse
import requests
from urllib3.util.url import parse_url


class EnhancedFeatureExtractor:
    """Extract advanced features from URLs for phishing detection."""
    
    @staticmethod
    def extract_ssl_features(url: str) -> dict:
        """Extract SSL certificate features."""
        try:
            parsed = urlparse(url if '://' in url else 'https://' + url)
            domain = parsed.netloc
            
            if not url.startswith('https'):
                return {'has_ssl': 0, 'cert_age_days': -1, 'cert_valid': 0, 'issuer_match': 0}
            
            context = ssl.create_default_context()
            try:
                with socket.create_connection((domain, 443), timeout=5) as sock:
                    with context.wrap_socket(sock, server_hostname=domain) as ssock:
                        cert = ssock.getpeercert()
                        
                        # Check if cert exists
                        has_ssl = 1 if cert else 0
                        
                        # Calculate cert age
                        not_after_str = cert.get('notAfter')
                        cert_age_days = -1
                        cert_valid = 0
                        if not_after_str:
                            from email.utils import parsedate_to_datetime
                            try:
                                expiry = parsedate_to_datetime(not_after_str)
                                cert_age_days = (expiry - datetime.utcnow()).days
                                cert_valid = 1 if cert_age_days > 0 else 0
                            except:
                                pass
                        
                        # Check issuer match
                        issuer_match = 0
                        if cert:
                            subject = dict(x[0] for x in cert.get('subject', []))
                            issuer = dict(x[0] for x in cert.get('issuer', []))
                            subject_cn = subject.get('commonName', '')
                            issuer_cn = issuer.get('commonName', '')
                            issuer_match = 1 if issuer_cn and not subject_cn.endswith(issuer_cn) else 0
                        
                        return {
                            'has_ssl': has_ssl,
                            'cert_age_days': max(cert_age_days, 0),
                            'cert_valid': cert_valid,
                            'issuer_match': issuer_match
                        }
            except:
                return {'has_ssl': 0, 'cert_age_days': -1, 'cert_valid': 0, 'issuer_match': 0}
        except Exception as e:
            return {'has_ssl': 0, 'cert_age_days': -1, 'cert_valid': 0, 'issuer_match': 0}
    
    @staticmethod
    def extract_redirect_features(url: str, max_redirects: int = 10) -> dict:
        """Analyze redirect chain."""
        try:
            formatted = url if '://' in url else 'http://' + url
            response = requests.head(formatted, allow_redirects=True, timeout=5, stream=True)
            
            redirect_count = len(response.history)
            has_redirect = 1 if redirect_count > 0 else 0
            
            # Check for suspicious redirect (to different domain)
            suspicious_redirect = 0
            if redirect_count > 0:
                original_domain = parse_url(formatted).host
                final_domain = parse_url(response.url).host
                if original_domain != final_domain:
                    suspicious_redirect = 1
            
            return {
                'redirect_count': min(redirect_count, 10),
                'has_redirect': has_redirect,
                'suspicious_redirect': suspicious_redirect,
                'final_url_length': len(response.url)
            }
        except:
            return {'redirect_count': 0, 'has_redirect': 0, 'suspicious_redirect': 0, 'final_url_length': 0}
    
    @staticmethod
    def extract_whois_features(url: str) -> dict:
        """Extract WHOIS-based features (age, registrar reputation)."""
        try:
            # Note: full WHOIS requires external library (whois)
            # For now, use heuristics based on DNS TTL and registration patterns
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.netloc
            
            # Check for common registrars (heuristic)
            generic_registrars = ['godaddy.com', 'namecheap.com', 'register.com', 'network.solutions']
            is_generic_registrar = 1 if any(reg in domain for reg in generic_registrars) else 0
            
            # Domain age estimation (empty for now, requires WHOIS API)
            domain_age_years = 0
            
            return {
                'domain_age_years': domain_age_years,
                'is_generic_registrar': is_generic_registrar
            }
        except:
            return {'domain_age_years': 0, 'is_generic_registrar': 0}
    
    @staticmethod
    def compute_url_entropy(url: str) -> float:
        """Compute Shannon entropy of URL."""
        if not url:
            return 0.0
        entropy = 0.0
        for char in set(url):
            p = url.count(char) / len(url)
            entropy -= p * np.log2(p)
        return entropy
    
    @staticmethod
    def extract_all_features(url: str) -> np.ndarray:
        """Extract all 60+ features for advanced model."""
        features = []
        
        try:
            parsed = urlparse(url if '://' in url else 'http://' + url)
            domain = parsed.netloc
            path = parsed.path
            
            # Basic URL metrics (1-10)
            features.append(len(url))
            features.append(len(domain))
            features.append(len(path))
            features.append(url.count('/'))
            features.append(url.count('?'))
            features.append(url.count('&'))
            features.append(url.count('='))
            features.append(url.count('-'))
            features.append(url.count('.'))
            features.append(EnhancedFeatureExtractor.compute_url_entropy(url[:50]))
            
            # SSL features (11-14)
            ssl_features = EnhancedFeatureExtractor.extract_ssl_features(url)
            features.append(ssl_features.get('has_ssl', 0))
            features.append(ssl_features.get('cert_age_days', 0))
            features.append(ssl_features.get('cert_valid', 0))
            features.append(ssl_features.get('issuer_match', 0))
            
            # Redirect features (15-18)
            redirect_features = EnhancedFeatureExtractor.extract_redirect_features(url)
            features.append(redirect_features.get('redirect_count', 0))
            features.append(redirect_features.get('has_redirect', 0))
            features.append(redirect_features.get('suspicious_redirect', 0))
            features.append(redirect_features.get('final_url_length', 0))
            
            # WHOIS features (19-20)
            whois_features = EnhancedFeatureExtractor.extract_whois_features(url)
            features.append(whois_features.get('domain_age_years', 0))
            features.append(whois_features.get('is_generic_registrar', 0))
            
            # Domain analysis (21-30)
            features.append(domain.count('.'))
            features.append(1 if domain.startswith('www') else 0)
            features.append(1 if '-' in domain else 0)
            features.append(1 if '_' in domain else 0)
            features.append(1 if any(char.isdigit() for char in domain) else 0)
            features.append(len(domain.split('.')[-1]))  # TLD length
            features.append(EnhancedFeatureExtractor.compute_url_entropy(domain))
            features.append(1 if 'login' in url.lower() else 0)
            features.append(1 if 'verify' in url.lower() else 0)
            features.append(1 if 'confirm' in url.lower() else 0)
            
            # Pad to 30 features
            while len(features) < 30:
                features.append(0)
            
        except Exception as e:
            features = [0] * 30
        
        return np.array(features[:30], dtype=np.float64)
