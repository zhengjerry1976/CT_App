@echo off
chcp 65001 >nul
echo ============================================
echo [1/6] Checking Python...
python --version
if errorlevel 1 echo [X] Python NOT found! Please install Python 3.10+ and check "Add to PATH".
echo.
echo [2/6] Checking Pip...
pip --version
echo.
echo [3/6] Checking Flet...
flet --version
if errorlevel 1 echo [X] Flet NOT found! Will auto-install later.
echo.
echo [4/6] Checking Files...
if exist main.py (echo [OK] main.py found) else (echo [X] main.py MISSING!)
if exist requirements.txt (echo [OK] requirements.txt found) else (echo [X] requirements.txt MISSING!)
if exist pyproject.toml (echo [OK] pyproject.toml found) else (echo [X] pyproject.toml MISSING!)
echo.
echo [5/6] Checking JDK (for APK build)...
java -version 2>&1 | findstr "version"
if errorlevel 1 echo [!] JDK not found (needed for APK). Install Temurin JDK 17.
echo.
echo [6/6] Checking Flutter (for APK build)...
flutter --version 2>nul
if errorlevel 1 echo [!] Flutter not found (auto-downloaded by Flet on first build).
echo.
echo ============================================
echo Check done. If no [X] errors, you can run build_apk.bat
echo ============================================
pause