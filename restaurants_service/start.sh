#!/bin/sh
python manage.py migrate --noinput
# Run only the accounts-related URLs by using a separate settings module OR just run full project
gunicorn config.wsgi:application --bind 0.0.0.0:8001

