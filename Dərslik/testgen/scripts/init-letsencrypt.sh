#!/bin/bash
# Run this ONCE on the server before starting production stack.
# Usage: ./scripts/init-letsencrypt.sh
set -e

if [ ! -f .env.prod ]; then
  echo "ERROR: .env.prod not found in current directory. cd to testgen and ensure .env.prod exists."
  exit 1
fi

DOMAIN="e-tehsil.me"
EMAIL="alonewithpc@gmail.com"
STAGING=0  # Set to 1 for testing to avoid rate limits

mkdir -p ./certbot/conf ./certbot/www

# Create temporary self-signed cert so nginx can start
if [ ! -d "./certbot/conf/live/$DOMAIN" ]; then
  echo "### Creating temporary self-signed certificate for $DOMAIN ..."
  mkdir -p "./certbot/conf/live/$DOMAIN"
  openssl req -x509 -nodes -newkey rsa:4096 -days 1 \
    -keyout "./certbot/conf/live/$DOMAIN/privkey.pem" \
    -out "./certbot/conf/live/$DOMAIN/fullchain.pem" \
    -subj "/CN=localhost" 2>/dev/null
fi

echo "### Starting nginx ..."
docker compose -f docker-compose.prod.yml --env-file .env.prod up -d nginx

echo "### Waiting for nginx to be ready ..."
sleep 5

echo "### Removing temporary certificate ..."
rm -rf "./certbot/conf/live/$DOMAIN"

STAGING_FLAG=""
if [ $STAGING -eq 1 ]; then
  STAGING_FLAG="--staging"
  echo "### Using Let's Encrypt STAGING environment (test run)"
fi

echo "### Requesting Let's Encrypt certificate for $DOMAIN ..."
# docker-compose.prod.yml-də certbot xidmətinin entrypoint-i "renew" döngüsüdür; certonly üçün birbaşa image işlədirik
docker run --rm \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  certbot/certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  $STAGING_FLAG \
  --email "$EMAIL" \
  --agree-tos \
  --no-eff-email \
  -d "$DOMAIN" \
  -d "www.$DOMAIN"

echo "### Reloading nginx with real certificate ..."
docker compose -f docker-compose.prod.yml --env-file .env.prod exec nginx nginx -s reload

echo "### Done! Certificate issued for $DOMAIN"
echo "### Now start the full stack: bash deploy.sh   (or: docker compose -f docker-compose.prod.yml --env-file .env.prod up -d)"
