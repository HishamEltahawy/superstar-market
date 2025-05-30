#!/bin/bash

# Wait for Redis to be ready
echo "Waiting for Redis..."
while ! nc -z redis 6379; do
  sleep 1
done
echo "Redis is ready!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (will skip if exists)
python manage.py createsuperuser --noinput || true

# Start the application
# exec python manage.py runserver 0.0.0.0:8000
exec gunicorn ProjectFiles.wsgi:application --bind 0.0.0.0:8000