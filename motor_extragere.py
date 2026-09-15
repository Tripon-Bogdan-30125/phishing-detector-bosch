import requests
import base64
from modul1_lexical import LexicalAnalyzer
from modul2_osint import OSINTAnalyzer
from modul3_sandbox import SandboxAnalyzer

class FeatureExtractorEngine:
    def __init__(self):
        self.lexical = LexicalAnalyzer()
        self.osint = OSINTAnalyzer()
        self.sandbox = SandboxAnalyzer()
        # API-ul tău VirusTotal
        self.vt_api_key = "df789cad495e3a9e30aec8eafe18297449825554164a06599c4c975bf1a9c4dd"

    def get_reputation_api(self, url):
        reputation = {'tranco_rank': -1, 'virustotal_score': 0, 'google_safe_browsing': 0}
        try:
            
            url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
            vt_url = f"https://www.virustotal.com/api/v3/urls/{url_id}"
            headers = {"x-apikey": self.vt_api_key}
            
            response = requests.get(vt_url, headers=headers, timeout=5)
            
            if response.status_code == 200:
                json_res = response.json()
                if 'data' in json_res and 'attributes' in json_res['data']:
                    attr = json_res['data']['attributes']
                    
                    
                    if 'last_analysis_stats' in attr:
                        stats = attr['last_analysis_stats']
                        reputation['virustotal_score'] = stats.get('malicious', 0) + stats.get('phishing', 0)
                    
                    
                    if 'last_analysis_results' in attr:
                        results = attr['last_analysis_results']
                        if 'Google Safe Browsing' in results:
                            verdict = results['Google Safe Browsing'].get('result', '').lower()
                            if verdict in ['malicious', 'phishing', 'social engineering']:
                                reputation['google_safe_browsing'] = 1
                                
            elif response.status_code == 404:
                print("[!] URL-ul nu a fost găsit în baza de date VirusTotal. Necesită scanare nouă.")
        except Exception as e:
            print(f"[!] Eroare API VirusTotal: {e}")
            
        return reputation

    def process_url(self, url):
        vector = {}
        # 1-14. Extragem parametrii Lexicali
        vector.update(self.lexical.extract_features(url))
        
        # 15-20. Extragem parametrii OSINT + SSL
        osint_res = self.osint.extract_features(url)
        # Salvăm ASN separat pentru a respecta ordinea de la final
        asn_val = osint_res.pop('asn_number', 0) 
        vector.update(osint_res)
        
        # 21-26. Extragem parametrii Sandbox (Selenium)
        vector.update(self.sandbox.extract_features(url))
        
        # 27-30. Extragem parametrii de Reputație (API-uri)
        api_res = self.get_reputation_api(url)
        vector['tranco_rank'] = api_res['tranco_rank']
        vector['asn_number'] = asn_val
        vector['virustotal_score'] = api_res['virustotal_score']
        vector['google_safe_browsing'] = api_res['google_safe_browsing']
        
        return vector

# TEST
if __name__ == "__main__":
    motor = FeatureExtractorEngine()
    # Test link Phishtank
    test_url = "www.google.com"
    
    print(f"\n[*] ANALIZĂ REALĂ (30 PARAMETRI) PENTRU: {test_url}")
    print("[*] Pornire motoare și interogare API-uri...")
    
    rezultate = motor.process_url(test_url)
    
    print(f"\n[SUCCESS] Parametri extrași:")
    for i, (k, v) in enumerate(rezultate.items(), 1):
        print(f"  {i:02d}. {k:25}: {v}")