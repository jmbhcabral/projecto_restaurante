#!/bin/sh
set -e
echo "Executando Makemigrations.sh"

# Use venv python explicitly
/venv/bin/python manage.py makemigrations --noinput