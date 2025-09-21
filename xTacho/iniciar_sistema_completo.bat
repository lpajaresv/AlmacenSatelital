@echo off
echo ========================================
echo   ALMACEN SATELITAL SAN LUIS
echo   Sistema de Control de Inventario
echo ========================================
echo.

REM Verificar si Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo Python no encontrado en PATH, buscando en ubicaciones comunes...
    
    REM Buscar Python en ubicaciones comunes
    set "PYTHON_CMD="
    
    REM Buscar en AppData\Local\Programs\Python
    for /d %%i in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_CMD=%%i\python.exe"
            goto :found_python
        )
    )
    
    REM Buscar en Program Files
    for /d %%i in ("C:\Program Files\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_CMD=%%i\python.exe"
            goto :found_python
        )
    )
    
    REM Buscar en Program Files (x86)
    for /d %%i in ("C:\Program Files (x86)\Python*") do (
        if exist "%%i\python.exe" (
            set "PYTHON_CMD=%%i\python.exe"
            goto :found_python
        )
    )
    
    REM Buscar en Microsoft Store
    if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
        set "PYTHON_CMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
        goto :found_python
    )
    
    :found_python
    if "%PYTHON_CMD%"=="" (
        echo ERROR: Python no encontrado en el sistema
        echo Por favor instala Python 3.7+ desde https://python.org
        echo O asegurate de que este en el PATH del sistema
        pause
        exit /b 1
    ) else (
        echo Python encontrado en: %PYTHON_CMD%
        set "PYTHON_CMD=%PYTHON_CMD%"
    )
) else (
    set "PYTHON_CMD=python"
)

echo ✅ Python encontrado
echo.

REM Verificar si existe el entorno virtual
if not exist "inventario_env" (
    echo 🔧 Creando entorno virtual...
    %PYTHON_CMD% -m venv inventario_env
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo ✅ Entorno virtual creado
)

REM Activar entorno virtual
echo 🔄 Activando entorno virtual...
call inventario_env\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)

REM Instalar dependencias si es necesario
echo 📦 Verificando dependencias...
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

REM Verificar si existe la base de datos
if not exist "inventario.db" (
    echo 🗄️  Creando base de datos de producción...
    %PYTHON_CMD% crear_db_produccion.py
    if errorlevel 1 (
        echo ERROR: No se pudo crear la base de datos
        pause
        exit /b 1
    )
    echo ✅ Base de datos creada
)

REM Obtener IP local
echo 🌐 Obteniendo direccion IP...
for /f "tokens=2 delims=:" %%i in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "ip=%%i"
    goto :found_ip
)
:found_ip
set "ip=%ip: =%"

echo.
echo ========================================
echo   SISTEMA INICIANDO...
echo ========================================
echo 📡 Servidor: http://localhost:8000
echo 🌐 Red local: http://%ip%:8000
echo.
echo ⏳ Iniciando servidor en 3 segundos...
echo    (Presiona Ctrl+C para detener)
echo.

REM Esperar 3 segundos
timeout /t 3 /nobreak >nul

REM Abrir navegador
echo 🌐 Abriendo navegador...
start http://localhost:8000

REM Ejecutar servidor
echo 🚀 Iniciando servidor de inventario...
%PYTHON_CMD% ejecutar_produccion.py

REM Si el servidor se detiene, mostrar mensaje
echo.
echo ========================================
echo   SERVIDOR DETENIDO
echo ========================================
echo El sistema se ha detenido.
echo Para volver a iniciar, ejecuta este archivo nuevamente.
echo.
pause
