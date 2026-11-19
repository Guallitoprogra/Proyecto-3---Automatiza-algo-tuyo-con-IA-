@echo off
setlocal
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
    py -3 lanzador.py --reales --cerrar
    exit /b
)
where python >nul 2>nul
if not errorlevel 1 (
    python lanzador.py --reales --cerrar
    exit /b
)
if exist "%APPDATA%\uv\python\cpython-3.14.6-windows-x86_64-none\python.exe" (
    "%APPDATA%\uv\python\cpython-3.14.6-windows-x86_64-none\python.exe" lanzador.py --reales --cerrar
    exit /b
)
echo Instala Python 3.10 o posterior y vuelve a intentarlo.
pause
