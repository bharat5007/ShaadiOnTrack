#!/bin/bash

# Wedding Core Service - Local Development Setup Script

echo "========================================"
echo "Wedding Core Service - Setup Script"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL client not found. Please install PostgreSQL."
    echo "   macOS: brew install postgresql"
    echo "   Ubuntu: sudo apt-get install postgresql postgresql-contrib"
    exit 1
fi

echo "✅ PostgreSQL found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi
echo ""

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt
echo "✅ Dependencies installed"
echo ""

# Copy .env.example to .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please update .env file with your database credentials"
else
    echo "✅ .env file already exists"
fi
echo ""

# Check if database exists
echo "🗄️  Checking database..."
DB_NAME=$(grep DB_NAME .env | cut -d '=' -f2)
DB_USER=$(grep DB_USER .env | cut -d '=' -f2)
DB_HOST=$(grep DB_HOST .env | cut -d '=' -f2)

if PGPASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2) psql -h $DB_HOST -U $DB_USER -lqt | cut -d \| -f 1 | grep -qw $DB_NAME; then
    echo "✅ Database '$DB_NAME' exists"
else
    echo "⚠️  Database '$DB_NAME' does not exist"
    echo "   Creating database..."
    PGPASSWORD=$(grep DB_PASSWORD .env | cut -d '=' -f2) psql -h $DB_HOST -U $DB_USER -c "CREATE DATABASE $DB_NAME;" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Database '$DB_NAME' created successfully"
    else
        echo "⚠️  Could not create database. Please create it manually:"
        echo "   psql -U $DB_USER -c \"CREATE DATABASE $DB_NAME;\""
    fi
fi
echo ""

echo "========================================"
echo "✅ Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Update .env file with your configuration"
echo "2. Run: source .venv/bin/activate"
echo "3. Run: python run.py"
echo ""
echo "Or simply run: ./run.sh"
echo ""