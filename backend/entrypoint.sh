#!/bin/sh
set -eu

mkdir -p /app/secrets /app/staticfiles

if [ ! -s /app/secrets/oidc.key ]; then
  echo "Generating OIDC RSA private key..."
  openssl genrsa -out /app/secrets/oidc.key 4096
  chmod 600 /app/secrets/oidc.key
fi


echo "Applying migrations..."
python manage.py migrate --noinput


echo "Starting Daphne..."
exec daphne -b 0.0.0.0 -p 8000 config.asgi:application