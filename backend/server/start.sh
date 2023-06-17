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
cp server/nginx.conf /etc/nginx/sites-enabled/

# Start Nginx and Gunicorn
service nginx start && gunicorn rorsite.wsgi:application --bind 0.0.0.0:8000 --timeout 120
