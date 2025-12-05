# Base image Rasa (stable)
FROM rasa/rasa:3.6.21-full

# Set working directory
WORKDIR /app

# Switch to root to install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files first
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt || true

# Expose Render port
ENV PORT=10000
EXPOSE 10000

# Disable Rasa telemetry
ENV RASA_TELEMETRY_ENABLED=false

# Run Rasa server
CMD ["rasa", "run", "--enable-api", "--port", "10000", "--cors", "*", "--model", "models/default.tar.gz"]