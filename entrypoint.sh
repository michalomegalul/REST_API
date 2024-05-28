#!/bin/sh

echo "Waiting for the database to be ready..."
while true; do
    if nc -z db 5432; then
        echo "Connected to the database."
        break
    else
        echo "Failed to connect to the database."
        sleep 1
    fi
done

echo "Database is ready. ........................................................................................................................................................................................"

# Run migrations
poetry run flask db upgrade

# Start the application
exec poetry run gunicorn -b :5000 --access-logfile - --error-logfile - "app:app"
