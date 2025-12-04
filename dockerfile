# Utiliser Python 3.10.14
FROM python:3.10.14-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 10000

CMD ["rasa", "run", "--enable-api", "--port", "10000"]