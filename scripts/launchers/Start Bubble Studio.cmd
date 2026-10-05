@echo off
chcp 65001 >nul
cd /d "%~dp0..\.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\windows-launch.py studio
) else (
  python scripts\windows-launch.py studio
)
if errorlevel 1 pause
