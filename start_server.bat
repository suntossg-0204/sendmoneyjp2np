@echo off
cd /d D:\Projects\sendmoneyjp2np

echo.
echo ==================================
echo   RemitTracker Local Server
echo ==================================
echo.
echo PC:
echo   http://localhost:8000
echo.
echo Mobile:
echo   http://192.168.1.16:8000
echo.

python -m http.server 8000 --bind 0.0.0.0

pause