@echo off

title Update GitHub Repository

echo ============================================
echo      Updating GitHub Repository
echo ============================================
echo.

cd /d "%~dp0.."

echo Current folder:
cd

echo.
set /p msg=Commit message: 

echo.
echo Adding files...
git add .

echo.
echo Creating commit...
git commit -m "%msg%"

echo.
echo Pushing to GitHub...
git push origin main

echo.
echo ============================================
echo              UPDATE COMPLETE
echo ============================================
echo.

pause