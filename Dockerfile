FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt fastapi uvicorn

# Copy project code
COPY . .

# Expose port (Render automatically sets $PORT)
ENV PORT=8080
EXPOSE 8080

CMD uvicorn api.main:app --host 0.0.0.0 --port ${PORT}
