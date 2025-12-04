FROM python:3.8-slim

# Empêche les questions interactives
ENV DEBIAN_FRONTEND=noninteractive

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
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]