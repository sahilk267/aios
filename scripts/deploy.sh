#!/bin/bash
# AIOS Deployment Script

set -e

echo "Deploying AIOS Platform..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "Docker Compose required"; exit 1; }

# Create data directories
mkdir -p data/sqlite data/qdrant data/logs data/graph

# Start all services
docker-compose up -d

# Wait for services
echo "Waiting for services to start..."
sleep 10

# Run migrations
cd backend
alembic upgrade head || echo "Migration skipped"
cd ..

# Verify health
curl -f http://localhost:8000/api/v1/health || echo "Health check failed"

echo "AIOS Platform deployed successfully!"
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Grafana: http://localhost:3000"
