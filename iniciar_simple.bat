@echo off
echo ========================================
echo   ALMACEN SATELITAL SAN LUIS
echo   Sistema de Control de Inventario
echo ========================================
echo.

REM Buscar Python en ubicaciones comunes
set "PYTHON_PATH="

REM Buscar en AppData\Local\Programs\Python
for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        goto :found
    )
)

REM Buscar en Program Files
for /d %%i in ("C:\Program Files\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        goto :found
    )
)

REM Buscar en Program Files (x86)
for /d %%i in ("C:\Program Files (x86)\Python*") do (
    if exist "%%i\python.exe" (
        set "PYTHON_PATH=%%i\python.exe"
        goto :found
    )
)

REM Buscar en Microsoft Store
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PYTHON_PATH=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
    goto :found
)

:found
if "%PYTHON_PATH%"=="" (
    echo ERROR: Python no encontrado
    echo Instala Python desde: https://python.org
    pause
    exit /b 1
)

echo Python encontrado: %PYTHON_PATH%
echo.

REM Crear entorno virtual si no existe
if not exist "inventario_env" (
    echo Creando entorno virtual...
    "%PYTHON_PATH%" -m venv inventario_env
)

REM Activar entorno virtual
echo Activando entorno virtual...
call inventario_env\Scripts\activate.bat

REM Instalar dependencias
echo Instalando dependencias...
pip install -r requirements.txt

REM Crear base de datos si no existe
if not exist "inventario.db" (
    echo Creando base de datos...
    "%PYTHON_PATH%" crear_db_produccion.py
)

REM Abrir navegador
echo Abriendo navegador...
start http://localhost:8000

REM Ejecutar servidor
echo Iniciando servidor...
"%PYTHON_PATH%" ejecutar_produccion.py

pause

