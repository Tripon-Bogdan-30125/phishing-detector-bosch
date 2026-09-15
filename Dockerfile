# 1. Imaginea de bază cu Python
FROM python:3.10-slim

# 2. Instalăm dependențele de sistem și Google Chrome direct prin pachetul .deb
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    libxi6 \
    libgconf-2-4 \
    libnss3 \
    && wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y ./google-chrome-stable_current_amd64.deb \
    && rm google-chrome-stable_current_amd64.deb \
    && rm -rf /var/lib/apt/lists/*

# 3. Setăm folderul principal în interiorul containerului
WORKDIR /app

# 4. Copiem librăriile și le instalăm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copiem tot restul codului în container
COPY . .

# 6. Expunem portul standard folosit de Streamlit
EXPOSE 8501

# 7. Comanda de pornire a aplicației
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
