@echo off
title GitHub Auto Update

cd /d "C:\Users\zacks\Persona Bot"

echo ============================
echo Updating GitHub Repository
echo ============================
echo.

git add .

set /p msg=Commit message: 

git commit -m "%msg%"

git push

echo.
echo ============================
echo Upload Complete
echo ============================
pause