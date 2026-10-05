@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\windows-launch.py apps
) else (
  python scripts\windows-launch.py apps
)
if errorlevel 1 pause
