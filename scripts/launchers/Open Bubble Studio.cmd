@echo off
cd /d "%~dp0..\.."
where py >nul 2>nul
if %errorlevel%==0 (
  py -3 scripts\login-start.py --studio
) else (
  python scripts\login-start.py --studio
)
