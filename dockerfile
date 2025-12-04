# Image Rasa stable avec Python 3.8
FROM rasa/rasa:3.6.21-full

# Répertoire de travail
WORKDIR /app

# Installer les dépendances système nécessaires pour compiler certaines librairies Python
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste du projet Rasa
COPY . .

# Port utilisé par Render
ENV PORT=10000
EXPOSE 10000

# Lancer Rasa avec API activée et CORS ouvert
CMD ["rasa", "run", "--enable-api", "--port", "10000", "--cors", "*", "--model", "models/default.tar.gz"]