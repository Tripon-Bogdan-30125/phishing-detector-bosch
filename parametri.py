import pandas as pd

# Încărcăm fișierul tău principal de date
df = pd.read_csv('dataset_final_dizertatie.csv')

# Eliminăm coloana 'target' (pentru că acesta este rezultatul: 0 sau 1, nu un parametru extras)
if 'target' in df.columns:
    df = df.drop('target', axis=1)

# Eliminăm și 'url_text' dacă a rămas în dataset, deoarece este doar textul link-ului
if 'url_text' in df.columns:
    df = df.drop('url_text', axis=1)

# Preluăm numele tuturor coloanelor (parametrii)
parametri = df.columns.tolist()

# Afișăm rezultatul numerotat pe ecran
print(f"[*] S-au găsit exact {len(parametri)} parametri în dataset:")
print("-" * 40)
for index, parametru in enumerate(parametri, start=1):
    print(f"{index}. {parametru}")
print("-" * 40)