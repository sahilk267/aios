#!/bin/bash
# AIOS Initial Setup Script

set -e

echo "Setting up AIOS Development Environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Create data directories
echo "Creating data directories..."
mkdir -p data/sqlite data/qdrant data/logs data/graph
mkdir -p config/prometheus config/grafana/provisioning config/grafana/dashboards config/loki

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
AIOS_ENV=development
AIOS_DEBUG=true
AIOS_LOG_LEVEL=INFO
AIOS_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
AIOS_OLLAMA_URL=http://localhost:11434
EOF
fi

# Initialize database
echo "Initializing database..."
cd backend
alembic upgrade head || echo "Migration will run on first start"
cd ..

echo ""
echo "=================================="
echo "AIOS Setup Complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Start Docker services: docker-compose up -d"
echo "2. Start development server: ./scripts/dev.sh"
echo "3. Or start backend only: cd backend && uvicorn aios.main:app --reload"
echo ""
