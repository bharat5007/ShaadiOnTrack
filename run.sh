#!/bin/bash

# Wedding Core Service - Run Script

echo "========================================"
echo "Starting Wedding Core Service"
echo "========================================"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "🔌 Activating virtual environment..."
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  Virtual environment not found. Running setup.sh..."
    ./setup.sh
    source .venv/bin/activate
fi
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please run setup.sh first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

echo "🚀 Starting server on port ${SERVICE_PORT:-8000}..."
echo "📖 API Documentation: http://localhost:${SERVICE_PORT:-8000}/docs"
echo "🏥 Health Check: http://localhost:${SERVICE_PORT:-8000}/health"
echo ""
echo "Press CTRL+C to stop the server"
echo ""

# Run the application
uvicorn app.main:app --host 0.0.0.0 --port ${SERVICE_PORT:-8000} --reload