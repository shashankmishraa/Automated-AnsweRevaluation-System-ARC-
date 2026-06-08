@echo off
echo ========================================
echo  ARC Professional UI Setup
echo ========================================
echo.

cd ui-react

echo [1/2] Installing dependencies...
echo This may take a few minutes on first run...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check your Node.js installation.
    pause
    exit /b 1
)

echo.
echo [2/2] Installation complete!
echo.
echo ========================================
echo  Starting Development Server
echo ========================================
echo.
echo The app will be available at: http://localhost:3000
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
