#!/bin/bash
# AIOS Rollback Script

set -e

echo "Rolling back AIOS deployment..."

# Stop services
docker-compose down

# Restore database backup if available
if [ -f "data/sqlite/aios.db.backup" ]; then
    cp data/sqlite/aios.db.backup data/sqlite/aios.db
    echo "Database restored from backup"
fi

# Restart services
docker-compose up -d

echo "Rollback complete"
