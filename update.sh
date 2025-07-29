#!/bin/bash
set -e
echo "Updating Telegram HR Bot..."
git pull origin master
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build
echo "Update completed!"
