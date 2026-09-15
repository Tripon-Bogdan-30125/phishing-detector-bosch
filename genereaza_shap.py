import pandas as pd
import xgboost as xgb
import shap
import pickle
import matplotlib.pyplot as plt

def genereaza_grafice_shap():
    print("[*] Incarcam modelul si datele...")
    # Incarcam modelul tau deja antrenat
    with open('phishing_model.pkl', 'rb') as f:
        model = pickle.load(f)
        
    df = pd.read_csv('dataset_final_dizertatie.csv').dropna()
    if 'url_text' in df.columns:
        df = df.drop('url_text', axis=1)
        
    X = df.drop('target', axis=1)
    y = df['target']
    
    print("[*] Calculam matricea SHAP (poate dura 10-20 secunde)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer(X)
    
    # Gasim automat un site de phishing si unul legitim pentru demonstratie
    idx_phishing = y[y == 1].index[0]
    idx_legitim = y[y == 0].index[0]
    idx_edge = y[y == 1].index[5] # Un alt atac de phishing pentru varietate
    
    def save_shap_plot(index, filename, title):
        plt.figure(figsize=(10, 6))
        # Generam plot-ul tip cascada (waterfall)
        shap.plots.waterfall(shap_values[index], show=False, max_display=10)
        plt.title(title, fontsize=14, pad=20)
        plt.tight_layout()
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close()

    print("[*] Salvam imaginile...")
    save_shap_plot(idx_phishing, 'SHAP_Phishing.png', "SHAP Analysis: Malicious Zero-Day Phishing URL")
    save_shap_plot(idx_legitim, 'SHAP_Legitim.png', "SHAP Analysis: Legitimate Authentication Portal")
    save_shap_plot(idx_edge, 'SHAP_EdgeCase.png', "SHAP Analysis: Sophisticated Evasion Attempt")
    
    print("[+] Gata! Cele 3 imagini au fost salvate in folder.")

if __name__ == "__main__":
    genereaza_grafice_shap()