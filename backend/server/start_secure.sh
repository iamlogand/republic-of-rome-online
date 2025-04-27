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
[ ! -d "/etc/nginx/ssl/" ] && mkdir -p /etc/nginx/ssl/  # TODO: check if this can be deleted

# Download certificate
python server/s3_ssl_cert_download.py

DOMAIN="api.roronline.com,temp.roronline.com"

# Request certificate
if [ ! -f "/etc/letsencrypt/live/$DOMAIN/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/$DOMAIN/privkey.pem" ]; then
    certbot certonly --standalone --non-interactive --agree-tos --email iamlogandavidson@gmail.com -d $DOMAIN
    python server/s3_ssl_cert_upload.py
else
    echo "Certificates already exist, skipping Certbot request."
fi

# Apply correct permissions to certificate files
chmod 644 /etc/letsencrypt/live/$DOMAIN/fullchain.pem
chmod 644 /etc/letsencrypt/live/$DOMAIN/privkey.pem
chown www-data:www-data /etc/letsencrypt/live/$DOMAIN/*

# Start nginx
service nginx start

# Start Daphne
daphne rorsite.asgi:application --bind 0.0.0.0 --port 8000

# Start certbot renew in the background every day
while true
do
    certbot renew --quiet
    service nginx reload
    python server/s3_ssl_cert_upload.py

    sleep 86400  # 24 hours
done &
