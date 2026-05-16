@echo off
title Persona Bot - Auto Fix Tool

echo ====================================
echo   PERSONA BOT - AUTO FIX TOOL
echo ====================================

cd /d %~dp0\..

echo.
echo [1/4] Running Ruff auto-fix...
ruff check bot --fix

echo.
echo [2/4] Formatting code...
ruff format bot

echo.
echo [3/4] Removing pycache files...
for /r %%x in (*.pyc) do del "%%x" 2>nul

echo.
echo [4/4] Checking remaining issues...
ruff check bot

echo.
echo ====================================
echo DONE
echo ====================================
pause