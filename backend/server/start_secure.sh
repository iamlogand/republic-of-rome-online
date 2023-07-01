#!/bin/sh

# Collect static files
python manage.py collectstatic --no-input

# Change ownership of static files directory
chown -R www-data:www-data /app/staticfiles

# Migrate
python manage.py migrate

# Install Nginx
apt-get update && apt-get install -y nginx

# Remove the default Nginx configuration file
rm /etc/nginx/sites-enabled/default

# Copy the Nginx configuration file
cp server/nginx_secure.conf /etc/nginx/sites-enabled/

# Check and create directory if not exists
[ ! -d "/etc/nginx/ssl/" ] && mkdir -p /etc/nginx/ssl/

# Download certificates
python server/s3_download.py

# Start Nginx and Daphne
service nginx start && daphne rorsite.asgi:application --bind 0.0.0.0 --port 8000
