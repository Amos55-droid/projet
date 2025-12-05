FROM python:3.8-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    python3-dev \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Fly.io impose le port 8080
ENV PORT=8080

EXPOSE 8080

# ⚠ Important : ajouter --host 0.0.0.0
CMD ["rasa", "run", "--enable-api", "--cors", "*", "--port", "8080", "--host", "0.0.0.0", "--model", "models/default.tar.gz"]