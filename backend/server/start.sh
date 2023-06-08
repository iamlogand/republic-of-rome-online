#!/bin/sh

# Install Nginx
apt-get update && apt-get install -y nginx

# Remove the default Nginx configuration file
rm /etc/nginx/sites-enabled/default

# Copy the Nginx configuration file
cp server/nginx.conf /etc/nginx/sites-enabled/

# Start Nginx and Gunicorn
service nginx start && gunicorn rorsite.wsgi:application --bind 0.0.0.0:8000
