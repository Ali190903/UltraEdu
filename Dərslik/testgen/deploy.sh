#!/bin/bash
# TestGen AI — DigitalOcean production deploy script
# Run once on fresh droplet:  bash deploy.sh

set -e

echo "=== TestGen AI Deploy ==="

# 1. Check .env.prod exists
if [ ! -f .env.prod ]; then
  echo "ERROR: .env.prod not found. Copy .env.prod.example and fill in values."
  exit 1
fi

# 2. Load env to get NEXT_PUBLIC_API_URL for build arg
source .env.prod

# 3. Pull latest code (if using git on server)
# git pull origin main

# 4. Build and start production containers
docker compose -f docker-compose.prod.yml --env-file .env.prod build \
  --build-arg NEXT_PUBLIC_API_URL="${NEXT_PUBLIC_API_URL}"

docker compose -f docker-compose.prod.yml --env-file .env.prod up -d

echo ""
echo "=== Running DB migrations ==="
docker compose -f docker-compose.prod.yml --env-file .env.prod exec backend alembic upgrade head

echo ""
echo "=== Deploy complete! ==="
echo "App is running at: ${NEXT_PUBLIC_API_URL:-http://localhost}"
