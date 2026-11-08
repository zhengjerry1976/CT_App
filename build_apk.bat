@echo off
chcp 65001 >nul
echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [X] Failed to install dependencies!
    pause
    exit /b 1
)
echo.
echo [2/3] Starting Flet APK build (First time takes 15-40 mins)...
echo Please wait, do NOT close this window...
flet build apk
if errorlevel 1 (
    echo [X] APK build failed! Check red errors above.
    pause
    exit /b 1
)
echo.
echo [3/3] Build Success!
echo APK location: build\apk\
start "" "build\apk"
echo If folder is empty, check: build\flutter\android\app\outputs\apk\release\
echo.
pause