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

# Copy the SSL certificates from the Docker secrets
aws s3 cp s3://api-roronline-com-ssl/api_roronline_com.crt /etc/nginx/ssl/api_roronline_com.crt
aws s3 cp s3://api-roronline-com-ssl/certificate.key /etc/nginx/ssl/certificate.key
aws s3 cp s3://api-roronline-com-ssl/ca_bundle.crt /etc/nginx/ssl/ca_bundle.crt

# Start Nginx and Gunicorn
service nginx start && gunicorn rorsite.wsgi:application -c gunicorn.conf.py
