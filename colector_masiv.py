import pandas as pd
import time
import os
import random
from motor_extragere import FeatureExtractorEngine

def incarca_lista(fisier, limita=1500):
    """Încarcă URL-urile, dar le limitează la un număr maxim pentru a nu bloca sistemul."""
    if not os.path.exists(fisier):
        print(f"[!] Fisierul {fisier} nu exista!")
        return []
    with open(fisier, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
        # Eliminăm duplicatele
        urls = list(set(urls))
        # Amestecăm lista și luăm doar primele 'limita'
        random.shuffle(urls)
        return urls[:limita]

def start_colectare_masiva():
    fisier_salvare = 'dataset_final_dizertatie.csv'
    
    # Funcția de RESUME (dacă se oprește, o ia de unde a rămas)
    date_existente = []
    url_uri_procesate = set()
    
    if os.path.exists(fisier_salvare):
        try:
            df_exista = pd.read_csv(fisier_salvare)
            date_existente = df_exista.to_dict('records')
            if 'url_text' in df_exista.columns:
                url_uri_procesate = set(df_exista['url_text'].tolist())
            print(f"[*] Am găsit {len(url_uri_procesate)} rânduri deja procesate. Reluăm de unde am rămas...")
        except:
            pass

    print("[*] Încărcare baze de date brute...")
    # Luăm maxim 1500 legit și 1500 phishing (3000 total)
    legit = incarca_lista('legit_masiv.txt', 1500)
    phishing = incarca_lista('phishing_masiv.txt', 1500)

    toate_taskurile = [(u, 0) for u in legit] + [(u, 1) for u in phishing]
    
    # Păstrăm doar URL-urile pe care NU le-am procesat încă
    taskuri_noi = [(u, l) for u, l in toate_taskurile if u not in url_uri_procesate]
    
    total_de_facut = len(taskuri_noi)
    if total_de_facut == 0:
        print("[!] Nu mai sunt URL-uri noi de procesat. Dataset-ul este complet!")
        return

    print(f"[*] Au mai rămas de procesat {total_de_facut} URL-uri noi.")
    motor = FeatureExtractorEngine()

    for i, (url, label) in enumerate(taskuri_noi, 1):
        # Afișăm doar primele 50 de caractere ca să nu facem spam pe ecran
        print(f"[{i}/{total_de_facut}] Analizez (Clasa {label}): {url[:50]}...", end=" ", flush=True)
        
        try:
            vector = motor.process_url(url)
            vector['target'] = label
            vector_cu_url = {'url_text': url}
            vector_cu_url.update(vector)
            
            date_existente.append(vector_cu_url)
            print("OK!")
            
            # Salvăm progresul la fiecare 5 site-uri
            if i % 5 == 0:
                df_temp = pd.DataFrame(date_existente)
                df_temp.to_csv(fisier_salvare, index=False)
                print("   [+] Progres salvat pe hard-disk.")
                
        except Exception as e:
            print(f"EROARE! Trecem peste. ({str(e)[:30]})")

        # Pauză de 15 secunde (Rate Limiting) pentru a nu enerva VirusTotal
        time.sleep(15)

    # Salvare finală absolută
    pd.DataFrame(date_existente).to_csv(fisier_salvare, index=False)
    print(f"\n[GATA] Colectare masivă finalizată! Ai adunat {len(date_existente)} instanțe.")

if __name__ == "__main__":
    start_colectare_masiva()