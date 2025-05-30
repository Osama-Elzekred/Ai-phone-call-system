#!/bin/bash

# Development setup script for AI Phone Call System

echo "🚀 Setting up AI Phone Call System for development..."

# Check if Python 3.11+ is installed
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
if [[ $(echo "$python_version < 3.11" | bc -l) -eq 1 ]]; then
    echo "❌ Python 3.11 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env file from template..."
    cp .env.example .env
    echo "🔧 Please edit .env file with your configuration"
fi

echo "🎉 Development environment setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database and other configurations"
echo "2. Start PostgreSQL and Redis services"
echo "3. Run database migrations: alembic upgrade head"
echo "4. Start the development server: uvicorn main:app --reload"
echo ""
echo "Or use Docker: docker-compose up -d"
