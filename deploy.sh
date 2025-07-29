#!/bin/bash
set -e
echo "Deploying Telegram HR Bot..."
docker-compose -f docker-compose.production.yml up -d --build
echo "Deployment completed!"
