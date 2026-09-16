from bs4 import BeautifulSoup
import tldextract
import difflib
import time

# Importăm Selenium 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class SandboxAnalyzer:
    def __init__(self):
        

        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless") # Ascunde fereastra
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--window-size=1920,1080")
        # Configurăm Google Chrome să ruleze în modul "Headless" (Invizibil)
       
        # Ne punem o "mască" de utilizator normal de Windows
        self.chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.target_brands = ['paypal', 'apple', 'microsoft', 'google', 'facebook', 'netflix', 'emag', 'bancatransilvania']

    def calculate_similarity(self, word, brand):
        return difflib.SequenceMatcher(None, word, brand).ratio()

    def extract_features(self, url):
        """Vizitează link-ul cu un browser real, rulează JavaScript-ul și extrage datele."""
        features = {
            'redirect_count': 0,
            'diff_domain_redirect': 0,
            'has_password_field': 0,
            'iframe_count': 0,
            'has_anti_analysis_scripts': 0,
            'brand_spoofing_ratio': 0.0
        }
        
        if not url.startswith('http'):
            url = 'http://' + url
            
        driver = None
        try:
            # Pormim browserul 
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=self.chrome_options)
            
            # Setăm o limită de timp ca să nu se blocheze la infinit
            driver.set_page_load_timeout(10)
            
            # Extragem domeniul inițial
            initial_ext = tldextract.extract(url)
            initial_domain = f"{initial_ext.domain}.{initial_ext.suffix}"

            
            driver.get(url)
            
            time.sleep(2)
            
            final_url = driver.current_url
            final_ext = tldextract.extract(final_url)
            final_domain = f"{final_ext.domain}.{final_ext.suffix}"
            
            if initial_domain != final_domain:
                features['diff_domain_redirect'] = 1
                features['redirect_count'] = 1 
                
            
            html_text = driver.page_source.lower()
            soup = BeautifulSoup(html_text, 'html.parser')
            
            features['has_password_field'] = 1 if soup.find_all('input', type='password') else 0
            
            features['iframe_count'] = len(soup.find_all('iframe'))
        
            anti_analysis_keywords = ['contextmenu', 'preventdefault', 'event.button == 2']
            if any(kw in html_text for kw in anti_analysis_keywords):
                features['has_anti_analysis_scripts'] = 1
                
            # 7. Similitudine Vizuală (Brand Spoofing)
            max_sim = 0
            for brand in self.target_brands:
                sim = self.calculate_similarity(final_ext.domain, brand)
                if sim > max_sim:
                    max_sim = sim
            features['brand_spoofing_ratio'] = max_sim if max_sim < 1.0 else 0.0

        except Exception as e:
            
            pass
        finally:
            
            if driver:
                driver.quit()
            
        return features

# --- ZONA DE TESTARE ---
if __name__ == "__main__":
    analyzer = SandboxAnalyzer()
    
    test_url = "https://www.facebook.com"
    print(f"[*] Analizez dinamic cu Robotul Selenium: {test_url}")
    print("    ... pornesc browserul invizibil (durează 3-5 secunde) ...")
    
    rezultat = analyzer.extract_features(test_url)
    for cheie, valoare in rezultat.items():
        print(f"  {cheie}: {valoare}")
