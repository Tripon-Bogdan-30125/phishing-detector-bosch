import re
import math
import tldextract
from urllib.parse import urlparse
from collections import Counter

class LexicalAnalyzer:
    def __init__(self):
        # Acestea sunt cuvintele cheie pe care le vom căuta în URL
        self.phishing_keywords = ['login', 'verify', 'bank', 'update', 'account', 'secure', 'paypal', 'apple']

    def calculate_shannon_entropy(self, string):
        """Calculează gradul de 'aleatoriu' dintr-un text."""
        if not string:
            return 0
        counts = Counter(string)
        probabilities = [float(c) / len(string) for c in counts.values()]
        return -sum(p * math.log2(p) for p in probabilities)

    def calculate_sliding_window_entropy(self, url, window_size=5):
        """Caută secvențe scurte și suspecte de caractere aleatorii în tot URL-ul."""
        if len(url) < window_size:
            return self.calculate_shannon_entropy(url)
        max_entropy = 0
        for i in range(len(url) - window_size + 1):
            window = url[i:i+window_size]
            entropy = self.calculate_shannon_entropy(window)
            if entropy > max_entropy:
                max_entropy = entropy
        return max_entropy

    def is_ip_address(self, hostname):
        """Verifică dacă domeniul este de fapt o adresă IP (ex: 192.168.1.1)."""
        ip_pattern = re.compile(r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')
        return 1 if ip_pattern.match(hostname) else 0

    def extract_features(self, url):
        """Aceasta este funcția principală care primește URL-ul și returnează parametrii."""
        features = {}
        
        # Spargem URL-ul în bucăți
        parsed_url = urlparse(url)
        ext = tldextract.extract(url)
        hostname = parsed_url.hostname or ""
        
        features['url_length'] = len(url)
        features['hostname_length'] = len(hostname)
        features['dot_count'] = url.count('.')
        features['hyphen_count'] = url.count('-')
        
        digits = sum(c.isdigit() for c in url)
        letters = sum(c.isalpha() for c in url)
        features['digit_count'] = digits
        features['digit_letter_ratio'] = digits / letters if letters > 0 else digits
        
        domain_string = f"{ext.domain}.{ext.suffix}"
        features['shannon_entropy'] = self.calculate_shannon_entropy(domain_string)
        features['sliding_entropy'] = self.calculate_sliding_window_entropy(url)
        
        features['has_at_symbol'] = 1 if '@' in url else 0
        
        port = parsed_url.port
        features['non_standard_port'] = 1 if port and port not in [80, 443] else 0
        
        features['is_ip'] = self.is_ip_address(hostname)
        features['subdomain_count'] = len(ext.subdomain.split('.')) if ext.subdomain else 0
        features['has_punycode'] = 1 if 'xn--' in url else 0
        features['has_phishing_keyword'] = 1 if any(kw in url.lower() for kw in self.phishing_keywords) else 0
        
        return features

# --- ZONA DE TESTARE ---
if __name__ == "__main__":
    analyzer = LexicalAnalyzer()
    
    # Testăm cu un site legitim și unul inventat suspect
    test_urls = [
        "https://www.bancatransilvania.ro", 
        "http://192.168.1.1:8080/secure-login-update-account.xn--p1ai@fake-paypal.com"
    ]
    
    for url in test_urls:
        print(f"\n--- Analiză pentru: {url} ---")
        rezultat = analyzer.extract_features(url)
        
        for cheie, valoare in rezultat.items():
            if isinstance(valoare, float):
                print(f"{cheie}: {valoare:.2f}")
            else:
                print(f"{cheie}: {valoare}")