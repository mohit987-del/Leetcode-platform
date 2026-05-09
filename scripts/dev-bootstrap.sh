#!/bin/sh
set -eu

if [ ! -f .env ]; then
  cp .env.example .env
fi

python manage.py migrate
python manage.py import_problems docs/sample-data/problems.json
python manage.py createsuperuser --username admin --email admin@example.com || true
