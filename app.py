import streamlit as st
import pandas as pd
import pickle
import shap
import matplotlib.pyplot as plt
import tldextract
from urllib.parse import urlparse, urlunparse
from motor_extragere import FeatureExtractorEngine

# 1. Page Configuration
st.set_page_config(page_title="AI Phishing Detector", page_icon="🛡️", layout="wide")

st.title("🛡️ Intelligent Anti-Phishing System (XAI)")
st.markdown("Machine Learning-based cybersecurity application. Enter a URL for live analysis.")

@st.cache_resource
def load_model():
    with open('phishing_model.pkl', 'rb') as f:
        return pickle.load(f)

@st.cache_resource
def load_engine():
    return FeatureExtractorEngine()

try:
    model = load_model()
    motor = load_engine()
except Exception as e:
    st.error(f"[!] Critical error loading resources: {e}")
    st.stop()

# 3. User Interface
url_input = st.text_input("Enter the suspicious URL for analysis:", placeholder="https://www.suspicious-site.com")

if st.button("Scan Live URL", type="primary"):
    if url_input:
        with st.spinner('The engine is extracting the 30 parameters live... Please wait.'):
            try:
                # Extract live vector
                vector = motor.process_url(url_input)
                ext = tldextract.extract(url_input)
                domeniu_complet = f"{ext.domain}.{ext.suffix}"
                enterprise_whitelist = ['microsoft.com', 'azure.com', 'bosch.com', 'github.com', 'youtube.com', 'google.com']

                if domeniu_complet in enterprise_whitelist:
                  # Dacă e domeniu aprobat de companie, forțăm verdictul de Safe
                            predictie = 0
                            probabilitati = [0.99, 0.01]
                            df_features = pd.DataFrame([vector])
                            for col in df_features.columns:
                                df_features[col] = 0.0
                else:
                # Convertim în DataFrame indiferent dacă e listă sau dicționar
                    if isinstance(vector, list):
                        df_features = pd.DataFrame([vector])
                    else:
                        df_features = pd.DataFrame([vector])

                # Curățăm forțat orice text/paranteză reziduală din fiecare celulă
                    for col in df_features.columns:
                     df_features[col] = df_features[col].astype(str).str.replace(r'[\[\]\']', '', regex=True)
                     df_features[col] = pd.to_numeric(df_features[col], errors='coerce').fillna(0.0)

                # Dacă modelul are salvate numele caracteristicilor, le aliniem
                    if hasattr(model, "feature_names_in_"):
                        df_features = df_features[model.feature_names_in_]
                
                # AI Prediction
                    predictie = model.predict(df_features)[0]
                    probabilitati = model.predict_proba(df_features)[0]
                
                st.divider()
                
                # Split screen into two columns
                col1, col2 = st.columns(2)
                
                # Column 1: The Verdict
                with col1:
                    st.subheader("Artificial Intelligence Verdict")
                    if predictie == 1:
                        st.error("🚨 ALERT: This site has been classified as PHISHING!")
                        st.metric(label="Risk Probability", value=f"{probabilitati[1]*100:.2f}%")
                    else:
                        st.success("✅ SAFE: This site has been classified as LEGITIMATE.")
                        st.metric(label="Safety Probability", value=f"{probabilitati[0]*100:.2f}%")
                
                # Column 2: Explainability (SHAP)
                with col2:
                    st.subheader("🧠 Model Explainability (XAI)")
                    st.markdown("The graph displays the most important decision factors. **Red (right)** = phishing suspicion, **Green (left)** = legitimate characteristic.")
                    
                    explainer = shap.TreeExplainer(model)
                    shap_values = explainer.shap_values(df_features)
                    
                    # Adapt to XGBoost format
                    if isinstance(shap_values, list):
                        valori_shap = shap_values[1][0]
                    elif len(shap_values.shape) == 3:
                        valori_shap = shap_values[0, :, 1]
                    else:
                        valori_shap = shap_values[0]

                    # Generate graph
                    shap_df = pd.DataFrame({'Parameter': df_features.columns, 'Impact': valori_shap})
                    shap_df['Absolute_Impact'] = shap_df['Impact'].abs()
                    shap_df = shap_df.sort_values(by='Absolute_Impact', ascending=False).head(8)

                    fig, ax = plt.subplots(figsize=(6, 4))
                    culori = ['#ff4b4b' if x > 0 else '#00cc96' for x in shap_df['Impact']]
                    ax.barh(shap_df['Parameter'], shap_df['Impact'], color=culori)
                    ax.set_xlabel('Impact on Decision')
                    ax.invert_yaxis()
                    st.pyplot(fig)

                # Display raw data
                st.divider()
                with st.expander("🔍 View all 30 extracted raw parameters (Technical Breakdown)"):
                    st.dataframe(df_features.T.rename(columns={0: "Detected Value"}), use_container_width=True)

            except Exception as e:
                st.error(f"An error occurred while connecting to the site: {e}")
    else:
        st.warning("Please enter a valid URL.")
