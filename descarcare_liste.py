import requests

def pregateste_liste():
    print("[*] Pasul 1: Descarc lista de Phishing (OpenPhish)...")
    try:
        r_phish = requests.get("https://openphish.com/feed.txt", timeout=10)
        if r_phish.status_code == 200:
            with open("phishing_masiv.txt", "w", encoding="utf-8") as f:
                f.write(r_phish.text)
            print(f"[+] SUCCES! 'phishing_masiv.txt' a fost creat ({len(r_phish.text.splitlines())} URL-uri).")
        else:
            print("[!] Eroare la descărcarea listei de phishing.")
    except Exception as e:
        print(f"[!] Eroare conexiune OpenPhish: {e}")

    print("\n[*] Pasul 2: Descarc lista de site-uri Legitime (Top 1000 Global)...")
    try:
        # Am schimbat link-ul cu un repository GitHub foarte vechi și stabil
        url_legit = "https://raw.githubusercontent.com/bensooter/URLchecker/master/top-1000-websites.txt"
        r_legit = requests.get(url_legit, timeout=10)
        
        if r_legit.status_code == 200:
            count = 0
            with open("legit_masiv.txt", "w", encoding="utf-8") as f:
                for line in r_legit.text.splitlines():
                    domeniu = line.strip()
                    # Dacă linia nu e goală, o scriem în fișier adăugând https://www.
                    if domeniu and not domeniu.startswith('#'):
                        f.write(f"https://www.{domeniu}\n")
                        count += 1
            print(f"[+] SUCCES! 'legit_masiv.txt' a fost creat ({count} URL-uri).")
        else:
            print(f"[!] Eroare la serverul GitHub. Cod: {r_legit.status_code}")
    except Exception as e:
        print(f"[!] Eroare conexiune GitHub: {e}")

if __name__ == "__main__":
    pregateste_liste()