#!/bin/sh

# Collect static files
python manage.py collectstatic --no-input

# Change ownership of static files directory
chown -R www-data:www-data /app/staticfiles

# Migrate
python manage.py migrate

# Remove the default Nginx configuration file
rm /etc/nginx/sites-enabled/default

# Copy the Nginx configuration file
cp server/nginx_secure.conf /etc/nginx/sites-enabled/

# Check and create directory if not exists
[ ! -d "/etc/nginx/ssl/" ] && mkdir -p /etc/nginx/ssl/

# Set domain and email
DOMAIN="api.roronline.com"
EMAIL="iamlogandavidson@gmail.com"

# Start nginx before certbot
service nginx start

# Request certificate
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ]; then
    certbot certonly --standalone --non-interactive --agree-tos --email $EMAIL -d $DOMAIN
fi

# Reload nginx to pick up certs
service nginx reload

# Start Daphne
daphne rorsite.asgi:application --bind 0.0.0.0 --port 8000

# Start certbot renew in the background every 12 hours
while true
do
    certbot renew --quiet
    service nginx reload
    sleep 43200  # 12 hours
done &
