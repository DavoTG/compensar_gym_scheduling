@echo off
echo ========================================
echo   Configuracion del Entorno Virtual
echo ========================================
echo.

REM Verificar si el entorno virtual existe
if exist "venv\" (
    echo El entorno virtual ya existe.
    echo.
) else (
    echo Creando entorno virtual...
    python -m venv venv
    echo Entorno virtual creado.
    echo.
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ========================================
echo   Configuracion completada!
echo ========================================
echo.
echo Para iniciar la aplicacion, ejecuta:
echo   start.bat
echo.

pause
