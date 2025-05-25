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

# Download certificate
python server/s3_ssl_cert.py download

# Request new certificate
if [ ! -f "/etc/letsencrypt/live/api.roronline.com/fullchain.pem" ] || [ ! -f "/etc/letsencrypt/live/api.roronline.com/privkey.pem" ]; then
    certbot certonly --standalone --non-interactive --agree-tos --email iamlogandavidson@gmail.com -d api.roronline.com
    python server/s3_ssl_cert.py upload
else
    echo "Certificates already exist, skipping Certbot request."
fi

# Apply correct permissions to certificate files
chmod 644 /etc/letsencrypt/live/api.roronline.com/fullchain.pem
chmod 644 /etc/letsencrypt/live/api.roronline.com/privkey.pem
chown www-data:www-data /etc/letsencrypt/live/api.roronline.com/*

# Start nginx
service nginx start

# Start certbot renew in the background every day
while true
do
    certbot renew --quiet
    service nginx reload
    python server/s3_ssl_cert.py upload
    sleep 86400  # 24 hours
done &

# Start Daphne
daphne rorsite.asgi:application --bind 0.0.0.0 --port 8000
