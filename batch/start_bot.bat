@echo off

title Persona Bot

echo ============================================
echo          STARTING PERSONA BOT
echo ============================================

cd /d "%~dp0.."

python -m bot.main

pause