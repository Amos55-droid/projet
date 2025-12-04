# --- Image de base Rasa complète (avec Python et toutes les dépendances) ---
FROM rasa/rasa:3.7.0-full

# --- Répertoire de travail ---
WORKDIR /app

# --- Copier les fichiers de dépendances pour actions ---
COPY requirements.txt .

# --- Installer les dépendances Python pour les actions personnalisées ---
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# --- Copier tout le projet Rasa ---
COPY . .

# --- Définir le port utilisé par Render ---
ENV PORT=10000

# --- Exposer le port pour Render ---
EXPOSE 10000

# --- Commande pour lancer Rasa avec API activée et CORS ouvert ---
CMD ["rasa", "run", "--enable-api", "--port", "10000", "--cors", "*", "--model", "models/default.tar.gz"]