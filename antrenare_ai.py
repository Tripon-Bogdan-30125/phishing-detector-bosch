import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def antreneaza_model():
    # 1. Încărcăm datele colectate
    print("[*] Încărcare dataset...")
    df = pd.read_csv('dataset_phishing.csv')
    
    # Curățăm datele (eliminăm URL-ul text dacă l-ai salvat, păstrăm doar numerele)
    if 'url_text' in df.columns:
        df = df.drop('url_text', axis=1)
    
    # 2. Separăm caracteristicile (X) de rezultat (y - target)
    X = df.drop('target', axis=1)
    y = df['target']
    
    # 3. Împărțim în date de Antrenament (80%) și date de Test (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"[*] Antrenare model pe {len(X_train)} mostre...")
    
    # 4. Configurăm și antrenăm XGBoost
    model = xgb.XGBClassifier(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # 5. Evaluare
    y_pred = model.predict(X_test)
    print("\n" + "="*30)
    print("REZULTATE EVALUARE")
    print("="*30)
    print(f"Acuratețe: {accuracy_score(y_test, y_pred) * 100:.2f}%")
    print("\nRaport detaliat:")
    print(classification_report(y_test, y_pred))
    
    # 6. Salvăm "creierul" (modelul) pentru a-l folosi în interfață
    with open('phishing_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("\n[+] Modelul a fost salvat ca 'phishing_model.pkl'")

    # 7. Vizualizare: Importanța Parametrilor
    plt.figure(figsize=(10, 8))
    xgb.plot_importance(model, max_num_features=15)
    plt.title("Top 15 parametri care decid dacă e Phishing")
    plt.show()

if __name__ == "__main__":
    antreneaza_model()