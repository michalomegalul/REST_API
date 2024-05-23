#!/bin/sh

poetry run flask db upgrade
exec poetry run gunicorn -b :5000 --access-logfile - --error-logfile - "app:app"
