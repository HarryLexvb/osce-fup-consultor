@echo off
echo ==========================================
echo OSCE FUP RUC Consultor - Setup Script
echo ==========================================
echo.

REM Check if .env exists
if not exist .env (
    echo Creating .env file from .env.example...
    copy .env.example .env
    echo [OK] .env file created
) else (
    echo [OK] .env file already exists
)

echo.
echo Building Docker containers...
docker-compose build

echo.
echo Starting services...
docker-compose up -d

echo.
echo Waiting for services to be ready...
timeout /t 5 /nobreak > nul

echo.
echo Running migrations...
docker-compose exec -T web python manage.py migrate

echo.
echo ==========================================
echo [OK] Setup complete!
echo ==========================================
echo.
echo Application is running at: http://localhost:8000/
echo.
echo Useful commands:
echo   - View logs:        docker-compose logs -f
echo   - Run tests:        docker-compose run web pytest
echo   - Stop services:    docker-compose down
echo.

pause
