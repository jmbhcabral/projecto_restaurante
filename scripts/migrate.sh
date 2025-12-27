#!/bin/sh
set -e
echo "Executando Migrate.sh"

/venv/bin/python manage.py migrate --noinput