@echo off
echo ============================================
echo  FraudGuard Pipeline Launcher
echo ============================================
echo.

echo [1/4] Starting Kafka cluster...
docker-compose up -d
echo Waiting 15 seconds for Kafka to be ready...
timeout /t 15 /nobreak >nul

echo.
echo [2/4] Starting Consumer (new terminal)...
start "FraudGuard Consumer" cmd /k "cd /d %~dp0 && python consumer.py"

echo.
echo [3/4] Starting Producer (new terminal)...
timeout /t 3 /nobreak >nul
start "FraudGuard Producer" cmd /k "cd /d %~dp0 && python producer.py"

echo.
echo [4/4] Starting Dashboard (new terminal)...
timeout /t 2 /nobreak >nul
start "FraudGuard Dashboard" cmd /k "cd /d %~dp0 && python -m streamlit run app.py"

echo.
echo ============================================
echo  All components launched!
echo  Dashboard: http://localhost:8501
echo ============================================
echo.
echo Press any key to STOP the Kafka cluster...
pause >nul

echo Stopping Kafka...
docker-compose down
echo Done.
