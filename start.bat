@echo off
echo ========================================
echo   Compensar Gym Scheduler - Inicio
echo ========================================
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Verificar si las dependencias están instaladas
python -c "import flask" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements.txt
    echo.
)

REM Iniciar aplicación web
echo Iniciando servidor web...
echo.
echo La aplicacion estara disponible en:
echo   http://localhost:5000
echo.
echo Presiona Ctrl+C para detener el servidor
echo.

python app.py

pause
