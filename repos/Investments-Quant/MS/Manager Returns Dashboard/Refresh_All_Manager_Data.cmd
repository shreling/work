@echo off
setlocal

set SCRIPT_DIR=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%refresh_manager_dashboard_caches.ps1"

if errorlevel 1 (
  echo.
  echo Refresh failed. See errors above.
  exit /b 1
)

echo.
echo Refresh completed successfully.
exit /b 0
