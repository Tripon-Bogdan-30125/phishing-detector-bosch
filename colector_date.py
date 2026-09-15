import pandas as pd
import time
import os
from motor_extragere import FeatureExtractorEngine

def incarca_url_uri(cale_fisier):
    with open(cale_fisier, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def colecteaza_date():
    motor = FeatureExtractorEngine()
    dataset = []
    
    # Încărcăm listele
    legit_urls = incarca_url_uri('urls_legit.txt')
    phishing_urls = incarca_url_uri('urls_phishing.txt')
    
    # Combinăm listele: (url, este_phishing)
    toate_urls = [(u, 0) for u in legit_urls] + [(u, 1) for u in phishing_urls]
    
    print(f"[*] Încep colectarea pentru {len(toate_urls)} URL-uri...")
    
    for i, (url, label) in enumerate(toate_urls, 1):
        print(f"[{i}/{len(toate_urls)}] Analizez: {url}")
        
        try:
            # Extragem cei 30 de parametri
            vector = motor.process_url(url)
            vector['target'] = label
            dataset.append(vector)
            
            df_temp = pd.DataFrame(dataset)
            df_temp.to_csv('dataset_phishing.csv', index=False)
            
        except Exception as e:
            print(f"    [!] Eroare la {url}: {e}")
        
        time.sleep(1)

    print("\n[SUCCESS] Colectare finalizată! Fișierul 'dataset_phishing.csv' este gata.")

if __name__ == "__main__":
    colecteaza_date()