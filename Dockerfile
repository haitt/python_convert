FROM python:3.11-slim

# Install system dependencies including LibreOffice and MySQL client
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    default-libmysqlclient-dev \
    pkg-config \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for file uploads and conversions
RUN mkdir -p uploads converted

# Expose port
EXPOSE 5001

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5001", "app:app"] 