FROM python:3.8-slim

# Empêche les questions interactives
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système minimales
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    git \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

# Installer pip + les dépendances
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Le port utilisé par Render
ENV PORT=10000

# Lancer le serveur Rasa
CMD ["rasa", "run", "--enable-api", "--port", "10000", "--cors", "*"]