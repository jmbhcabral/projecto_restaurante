#!/bin/sh
set -e
echo "Executando collectstatic.sh"

/venv/bin/python manage.py collectstatic --noinput