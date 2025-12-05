FROM rasa/rasa:3.6.21-full

WORKDIR /app

USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt || true

COPY . .

ENV PORT=10000
EXPOSE 10000

CMD ["rasa", "run", "--enable-api", "--port", "10000", "--cors", "*", "--model", "models/default.tar.gz"]