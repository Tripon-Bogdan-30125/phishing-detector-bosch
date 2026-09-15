# 1. Imaginea de bază cu Python
FROM python:3.10-slim

# 2. Instalăm Google Chrome și pachetele necesare pentru Selenium (CRITIC pentru tool-ul tău)
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list' \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. Setăm folderul principal în interiorul containerului
WORKDIR /app

# 4. Copiem librăriile și le instalăm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiem tot restul codului din GitHub în container
COPY . .

# 6. Expunem portul standard folosit de Streamlit
EXPOSE 8501

# 7. Comanda de pornire a aplicației
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
