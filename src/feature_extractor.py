import re
import numpy as np
import tldextract
from urllib.parse import urlparse
import socket
from difflib import SequenceMatcher

SUSPICIOUS_TOKENS = [
    "login", "signin", "secure", "account", "update", "verify", "bank", "confirm", 
    "password", "wallet", "free", "click", "bonus", "urgent", "ebay", "paypal", 
    "appleid", "microsoft", "amazon", "google", "confirm", "alert", "urgent",
    "suspended", "limited", "unusual", "activity", "reactivate", "resolve",
    "authenticate", "validate", "authorize", "invoice", "receipt",
]

LEGITIMATE_DOMAINS = {
    "google.com", "facebook.com", "github.com", "amazon.com", "microsoft.com",
    "apple.com", "wikipedia.org", "linkedin.com", "twitter.com", "youtube.com",
    "reddit.com", "stackoverflow.com", "github.com", "paypal.com", "ebay.com",
    "stripe.com", "atlassian.com", "nvidia.com", "intel.com", "cisco.com",
}

# Known brands commonly targeted by homograph/lookalike attacks
KNOWN_BRANDS = {
    "google", "amazon", "microsoft", "apple", "facebook", "twitter", "netflix",
    "paypal", "ebay", "instagram", "linkedin", "youtube", "github", "stripe",
    "adobe", "dropbox", "slack", "salesforce", "zoom", "okta", "github",
    "steam", "epic", "discord", "twitch", "reddit", "samsung", "huawei",
    "alibaba", "tencent", "baidu", "bank", "chase", "wellsfargo", "bofa",
    "ing", "ubs", "hsbc", "citibank", "kraken", "coinbase", "binance",
    "tesla", "uber", "spotify", "tiktok", "whatsapp", "telegram",
}

# Character substitution map for homograph attacks
HOMOGRAPH_SUBSTITUTIONS = {
    '0': 'o',  # Zero to letter O
    '1': 'i',  # One to letter I
    '3': 'e',  # Three to letter E
    '4': 'a',  # Four to letter A
    '5': 's',  # Five to letter S
    '7': 't',  # Seven to letter T
    '8': 'b',  # Eight to letter B
    '9': 'g',  # Nine to letter G
    'l': 'i',  # Lowercase L to I
    'rn': 'm',  # RN to M
    'cl': 'd',  # CL to D
}

class URLFeatureExtractor:
    """Extracts advanced features from URLs for phishing detection."""
    
    @staticmethod
    def normalize_url(url: str) -> str:
        """Normalize URL format."""
        url = url.strip()
        if not url:
            return url
        if not re.match(r"^https?://", url):
            url = "http://" + url
        return url
    
    @staticmethod
    def is_ip_address(hostname: str) -> bool:
        """Check if hostname is IP address."""
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(pattern, hostname):
            try:
                parts = hostname.split('.')
                return all(0 <= int(part) <= 255 for part in parts)
            except:
                return False
        return False
    
    @staticmethod
    def calculate_entropy(text: str) -> float:
        """Calculate Shannon entropy of text."""
        if not text:
            return 0.0
        counts = [text.count(c) for c in set(text)]
        probs = np.array(counts) / sum(counts)
        entropy = -(probs * np.log2(probs + 1e-9)).sum()
        return float(entropy)
    
    @staticmethod
    def get_domain_age_risk(domain: str) -> float:
        """Estimate domain age risk (higher = more suspicious)."""
        # Popular TLDs get lower risk
        popular_tlds = {'.com', '.org', '.edu', '.gov', '.net', '.gov.uk', '.co.uk'}
        if domain.endswith(tuple(popular_tlds)):
            return 0.0
        # Suspicious TLDs get higher risk
        suspicious_tlds = {'.tk', '.ml', '.ga', '.cf', '.work', '.gq'}
        if domain.endswith(tuple(suspicious_tlds)):
            return 1.0
        return 0.5
    
    @staticmethod
    def normalize_homograph_domain(domain: str) -> str:
        """
        Normalize a domain by replacing common homograph substitutions.
        Example: g00gle -> google, amaz0n -> amazon, rnicrosoft -> microsoft
        """
        normalized = domain.lower()
        
        # Apply multi-character substitutions first (longest first to avoid conflicts)
        for replacement, original in sorted(HOMOGRAPH_SUBSTITUTIONS.items(), key=lambda x: -len(x[0])):
            normalized = normalized.replace(replacement, original)
        
        return normalized
    
    @staticmethod
    def calculate_similarity(str1: str, str2: str) -> float:
        """Calculate similarity ratio between two strings (0-1)."""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    @staticmethod
    def detect_homograph_attack(domain: str) -> dict:
        """
        Detect if domain is a homograph/lookalike of a known brand.
        Returns: {
            'is_homograph': bool,
            'similarity_score': float (0-1),
            'matched_brand': str or None,
            'normalized_domain': str,
            'substitution_count': int
        }
        """
        domain_lower = domain.lower()
        normalized = URLFeatureExtractor.normalize_homograph_domain(domain)
        
        # Count obfuscation substitutions (digits + letter combos)
        digit_substitutions = {'0', '1', '3', '4', '5', '7', '8', '9'}
        letter_substitutions = {'rn', 'cl'}  # Common letter combos that look like other letters
        
        digit_obf_count = sum(1 for c in domain_lower if c in digit_substitutions)
        letter_obf_count = sum(1 for combo in letter_substitutions if combo in domain_lower)
        total_obf_count = digit_obf_count + letter_obf_count
        
        # Check for matches against known brands
        best_match = None
        best_similarity = 0.0
        
        for brand in KNOWN_BRANDS:
            # Check both original and normalized versions
            sim_original = URLFeatureExtractor.calculate_similarity(domain_lower, brand)
            sim_normalized = URLFeatureExtractor.calculate_similarity(normalized, brand)
            
            max_sim = max(sim_original, sim_normalized)
            
            # If similarity is high enough, track best match
            if max_sim > best_similarity:
                best_similarity = max_sim
                best_match = brand
        
        # Determine if it's a homograph attack:
        # Has obfuscation chars AND good similarity, OR
        # Very similar with typo-like issues (hyphens, letter substitutions)
        is_homograph = (total_obf_count > 0 and best_similarity > 0.7)
        
        # Also flag if removed obfuscations makes it a perfect brand match
        if not is_homograph and total_obf_count > 0:
            normalized_for_check = URLFeatureExtractor.normalize_homograph_domain(domain)
            for brand in KNOWN_BRANDS:
                if normalized_for_check == brand:
                    is_homograph = True
                    best_match = brand
                    best_similarity = 1.0
                    break
        
        return {
            'is_homograph': is_homograph,
            'similarity_score': float(best_similarity),
            'matched_brand': best_match,
            'normalized_domain': normalized,
            'substitution_count': int(total_obf_count)
        }
    
    @staticmethod
    def has_obfuscation_characters(domain: str) -> bool:
        """Check if domain contains common homograph obfuscation characters."""
        obfuscation_chars = {'0', '1', '3', '4', '5', '7', '8', '9'}
        return any(char in domain for char in obfuscation_chars)
    
    @staticmethod
    def extract_features(url: str) -> tuple:
        """
        Extract 28+ features from URL for enhanced detection.
        Includes homograph/lookalike attack detection.
        Returns: (features_array, feature_names)
        """
        url = URLFeatureExtractor.normalize_url(url)
        parsed = tldextract.extract(url)
        host = parsed.domain + ("." + parsed.suffix if parsed.suffix else "")
        path = re.sub(r"^https?://[^/]+", "", url)
        
        features = {}
        
        # Basic URL structure (5 features)
        features["url_length"] = len(url)
        features["host_length"] = len(host)
        features["path_length"] = len(path)
        features["domain_length"] = len(parsed.domain)
        features["tld_length"] = len(parsed.suffix)
        
        # Special character counts (10 features)
        features["num_dots"] = url.count(".")
        features["num_hyphens"] = url.count("-")
        features["num_at"] = url.count("@")
        features["num_question"] = url.count("?")
        features["num_equals"] = url.count("=")
        features["num_underscore"] = url.count("_")
        features["num_slash"] = url.count("/")
        features["num_digits"] = sum(c.isdigit() for c in url)
        features["num_uppercase"] = sum(c.isupper() for c in url)
        features["num_special"] = len([c for c in url if not c.isalnum() and c not in '.:/?#[]@!$&\'()*+,;=-_'])
        
        # Domain characteristics (5 features)
        features["has_ip"] = float(URLFeatureExtractor.is_ip_address(parsed.subdomain + "." + parsed.domain if parsed.subdomain else parsed.domain))
        features["subdomain_depth"] = len(parsed.subdomain.split('.')) if parsed.subdomain else 0
        features["domain_entropy"] = URLFeatureExtractor.calculate_entropy(parsed.domain)
        features["tld_entropy"] = URLFeatureExtractor.calculate_entropy(parsed.suffix) if parsed.suffix else 0.0
        features["is_legitimate_domain"] = float(host.lower() in LEGITIMATE_DOMAINS)
        
        # Suspicious patterns (5 features)
        features["has_suspicious_token"] = float(any(tok in url.lower() for tok in SUSPICIOUS_TOKENS))
        features["has_double_slash_in_path"] = float("//" in path if path else 0)
        features["has_url_shortener"] = float(any(short in url.lower() for short in ['bit.ly', 'tinyurl', 'short.link', 'goo.gl', 'ow.ly']))
        features["common_phishing_domains"] = float(any(phish in url.lower() for phish in ['secure', 'verify', 'login', 'signin']))
        features["domain_age_risk"] = URLFeatureExtractor.get_domain_age_risk(parsed.suffix)
        
        # Protocol analysis (2 features)
        features["uses_https"] = float(url.startswith("https://"))
        features["has_no_scheme"] = float(not url.startswith(("http://", "https://")))
        
        # Advanced patterns (3 features)
        features["redirect_count"] = len(re.findall(r'[?&]redirect|[?&]return|[?&]target', url.lower()))
        features["typosquatting_risk"] = float(len(parsed.domain) < 3 or any(c.isdigit() for c in parsed.domain[0:3]))
        features["port_suspicious"] = float(any(f":{port}" in url for port in ['81', '8080', '8888', '3000', '5000']))
        
        # URL path analysis (2 features)
        parameter_count = len(re.findall(r'[?&]', path))
        features["parameter_count"] = parameter_count
        path_entropy = URLFeatureExtractor.calculate_entropy(path) if path else 0.0
        features["path_entropy"] = path_entropy
        
        # Homograph/Lookalike attack detection (3 new features)
        homograph_info = URLFeatureExtractor.detect_homograph_attack(parsed.domain)
        features["is_homograph"] = float(homograph_info['is_homograph'])
        features["homograph_similarity_score"] = homograph_info['similarity_score']
        features["has_obfuscation_chars"] = float(URLFeatureExtractor.has_obfuscation_characters(parsed.domain))
        
        feature_array = np.array(list(features.values()), dtype=float)
        feature_names = list(features.keys())
        
        return feature_array, feature_names
    
    @staticmethod
    def batch_extract_features(urls: list) -> tuple:
        """Extract features from multiple URLs."""
        X = []
        names = None
        for url in urls:
            feats, names = URLFeatureExtractor.extract_features(url)
            X.append(feats)
        return np.vstack(X) if X else np.array([]), names
