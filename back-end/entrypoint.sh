#!/bin/sh
set -e

# Wait for the database to be ready (optional, if necessary)
# echo "Waiting for the database to be ready..."
# sleep 5

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Execute the container's main command
exec "$@"