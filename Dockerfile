FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

# Fly.io donne le port via cette variable
ENV PORT 8080
EXPOSE 8080

# On récupère le port dynamiquement depuis l'environnement
CMD ["bash", "-c", "rasa run --enable-api --cors '*' --host 0.0.0.0 --port $PORT --model models/default.tar.gz"]