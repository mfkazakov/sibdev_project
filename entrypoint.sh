#!/bin/bash

python manage.py flush --no-input

python manage.py makemigrations
python manage.py migrate
gunicorn sibdev_project.wsgi:application -c gunicorn_config.py
exec "$@"

