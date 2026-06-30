#!/bin/bash
# AIOS Development Startup Script

set -e

echo "Starting AIOS Development Environment..."

# Create data directories
mkdir -p data/sqlite data/qdrant data/logs data/graph

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Start infrastructure services
echo "Starting infrastructure services..."
docker-compose up -d postgres redis qdrant

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 5

# Run database migrations
echo "Running database migrations..."
cd backend
alembic upgrade head || echo "Migration failed (this is OK for initial setup)"

# Start backend in development mode
echo "Starting backend..."
uvicorn aios.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo ""
echo "=================================="
echo "AIOS Development Environment Ready"
echo "=================================="
echo "Backend: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/api/v1/health"
echo ""
echo "Press Ctrl+C to stop"
echo ""

# Wait for interrupt
trap "kill $BACKEND_PID; docker-compose down; exit 0" INT TERM
wait $BACKEND_PID
