#!/bin/sh

# Wait until Postgres is ready
# using the pg_isready utility
while ! pg_isready -h db -p 5432 > /dev/null 2> /dev/null; do
  echo "Connecting to Postgres Failed"
  sleep 1
done

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate --noinput

# Start server
echo "Starting server"
python manage.py runserver 0.0.0.0:8000
