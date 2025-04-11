#!/bin/sh
echo "Running migrations..."
python manage.py migrate --noinput

echo "Importing CSV data..."
python manage.py import_csv_data

echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 cardio_care.wsgi:application
