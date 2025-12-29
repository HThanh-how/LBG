@echo off
REM Script tự động deploy LBG cho Windows
REM Usage: deploy.bat

echo 🚀 Starting deployment...

REM Check if Docker is running
docker version >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Pull latest code (if in git repo)
if exist ".git" (
    echo 📥 Pulling latest code...
    git pull origin main
)

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose -f docker-compose.prod.yml down

REM Build and start containers
echo 🔨 Building and starting containers...
docker-compose -f docker-compose.prod.yml up -d --build

REM Wait a bit
timeout /t 10 /nobreak >nul

echo.
echo 🎉 Deployment complete!
echo.
echo 📊 Services:
echo   - Backend: http://localhost:8000
echo   - Frontend: http://localhost:3000
echo   - API Docs: http://localhost:8000/docs
echo.
echo 📝 Useful commands:
echo   - View logs: docker-compose -f docker-compose.prod.yml logs -f
echo   - Stop: docker-compose -f docker-compose.prod.yml down
echo   - Restart: docker-compose -f docker-compose.prod.yml restart

pause

