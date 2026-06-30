#!/bin/bash
# AIOS Test Runner Script

set -e

echo "Running AIOS Tests..."

cd backend

# Run linting first
echo "Running Ruff linter..."
ruff check aios/ tests/

# Run type checking
echo "Running MyPy type checker..."
mypy aios/ --ignore-missing-imports

# Run security scan
echo "Running Bandit security scan..."
bandit -r aios/ -ll

# Run tests with coverage
echo "Running tests with coverage..."
python -m pytest tests/ -v --cov=aios --cov-report=term-missing --cov-report=html

echo ""
echo "All tests passed!"
