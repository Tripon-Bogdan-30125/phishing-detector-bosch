import pandas as pd
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import pickle
import matplotlib.pyplot as plt
import seaborn as sns

def train_final_model():
    print("[*] Loading large dataset...")
    # Load the new dataset
    df = pd.read_csv('dataset_final_dizertatie.csv')
    
    print(f"[*] Found {len(df)} websites in total.")
    
    # Clean the data (remove URL text if present)
    if 'url_text' in df.columns:
        df = df.drop('url_text', axis=1)
        
    # Drop rows with NaN values resulting from collection errors (Data Cleaning)
    df = df.dropna()
    
    # Separate features (X) from the target (y)
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split the data: 80% Training, 20% Testing (Final Evaluation)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"[*] Training XGBoost model on {len(X_train)} instances. Please wait...")
    
    # Configure the model (added parameters to prevent overfitting)
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        use_label_encoder=False,
        eval_metric='logloss'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate on the test data
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred) * 100
    
    print("\n" + "="*40)
    print(" FINAL AI EVALUATION - RESULTS")
    print("="*40)
    print(f"Achieved Accuracy: {accuracy:.2f}%")
    print("\nDetailed Report (Class 0 = Legitimate, Class 1 = Phishing):")
    print(classification_report(y_test, y_pred))
    
    # Save the newly trained model over the old one
    with open('phishing_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print("[+] New AI model successfully saved as 'phishing_model.pkl'.")

    # ==========================================
    # GENERATE CONFUSION MATRIX FOR THE THESIS
    # ==========================================
    cm = confusion_matrix(y_test, y_pred)

    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['Legitimate (0)', 'Phishing (1)'], 
                yticklabels=['Legitimate (0)', 'Phishing (1)'],
                linewidths=1, linecolor='black')

    plt.ylabel('Actual Label', fontsize=12)
    plt.xlabel('Predicted Label', fontsize=12)
    plt.title('XGBoost Confusion Matrix', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save high-resolution image directly to the folder
    plt.savefig('Confusion_Matrix_Thesis.png', dpi=300)
    plt.close() # Close the plot to free memory
    # ==========================================
    # ==========================================

    # Draw the Feature Importance plot
    fig, ax = plt.subplots(figsize=(12, 8))
    xgb.plot_importance(model, max_num_features=15, height=0.5, ax=ax)
    plt.title("Top 15 Feature Importances (XGBoost Model)", fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save image to folder
    plt.savefig('Feature_Importance_Thesis.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    train_final_model()