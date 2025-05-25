FROM python:3.12.2-slim-bullseye

WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_SETTINGS_MODULE=ProjectFiles.settings

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libc6-dev \
    libffi-dev \
    libpq-dev \
    netcat-traditional \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy entrypoint script
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh

# Copy project files
COPY . .

# Create media and static directories
RUN mkdir -p media static

# Run entrypoint script
ENTRYPOINT ["./entrypoint.sh"]

# CMD ["gunicorn", "ProjectFiles.wsgi:application", "--bind", "0.0.0.0:8000"]