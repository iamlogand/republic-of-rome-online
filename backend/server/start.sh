#!/bin/sh

# Collect static files
python manage.py collectstatic --no-input

# Change ownership of static files directory
chown -R www-data:www-data /app/staticfiles

# Migrate
python manage.py migrate

# Remove the default nginx configuration file
rm /etc/nginx/sites-enabled/default

# Copy the nginx configuration file
cp server/nginx.conf /etc/nginx/sites-enabled/

# Start nginx and Daphne
service nginx start && daphne rorsite.asgi:application --bind 0.0.0.0 --port 8000
