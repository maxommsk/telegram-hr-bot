#!/bin/bash
set -e
BACKUP_DIR="./backups"
mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
docker exec hr_bot_postgres pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$BACKUP_DIR/backup_$TIMESTAMP.sql"
echo "Database backup created: backup_$TIMESTAMP.sql"
