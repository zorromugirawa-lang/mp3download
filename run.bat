@echo off
echo ========================================
echo   YouTube Downloader - Starting...
echo ========================================
echo.

cd backend

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Starting backend server...
echo Server akan berjalan di http://localhost:8000
echo.

start http://localhost:8000/frontend/index.html

echo [3/3] Server running...
echo Tekan Ctrl+C untuk menghentikan server
echo ========================================

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload