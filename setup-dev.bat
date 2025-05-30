@echo off
echo 🚀 Setting up AI Phone Call System for development...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo 📚 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Check if .env exists
if not exist ".env" (
    echo ⚙️ Creating .env file from template...
    copy .env.example .env
    echo 🔧 Please edit .env file with your configuration
)

echo 🎉 Development environment setup complete!
echo.
echo Next steps:
echo 1. Edit .env file with your database and other configurations
echo 2. Start PostgreSQL and Redis services
echo 3. Run database migrations: alembic upgrade head
echo 4. Start the development server: uvicorn main:app --reload
echo.
echo Or use Docker: docker-compose up -d

pause
