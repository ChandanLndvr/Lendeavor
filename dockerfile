# =========================
# Base Image
# =========================
FROM python:3.11-slim

# =========================
# Environment Variables
# =========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================
# Work Directory
# =========================
WORKDIR /app

# =========================
# System Dependencies
# =========================
RUN apt-get update && apt-get install -y \
    build-essential \
    default-libmysqlclient-dev \
    libssl-dev \
    libffi-dev \
    libjpeg-dev \
    zlib1g-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# =========================
# Upgrade pip & setuptools wheel
# =========================
RUN pip install --upgrade pip
RUN pip install --upgrade pip setuptools wheel


# =========================
# Copy Requirements
# =========================
COPY requirements.txt /app/

# =========================
# Install Python Dependencies
# =========================
RUN pip install --no-cache-dir -r requirements.txt

# =========================
# Copy Project Files
# =========================
COPY . /app/

# =========================
# Expose Port
# =========================
EXPOSE 8000

# =========================
# Start Server (Gunicorn)
# =========================
CMD ["gunicorn", "lndvr_site.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
