# Script para iniciar el Sistema de Inventario - Almacén Satelital San Luis
# Ejecutar: .\iniciar_sistema.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   ALMACEN SATELITAL SAN LUIS" -ForegroundColor Yellow
Write-Host "   Sistema de Control de Inventario" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar si Python está instalado
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python encontrado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Por favor instala Python 3.7+ desde https://python.org" -ForegroundColor Yellow
    Read-Host "Presiona Enter para salir"
    exit 1
}

# Verificar si existe el entorno virtual
if (-not (Test-Path "inventario_env")) {
    Write-Host "🔧 Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv inventario_env
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "✅ Entorno virtual creado" -ForegroundColor Green
}

# Activar entorno virtual
Write-Host "🔄 Activando entorno virtual..." -ForegroundColor Yellow
& "inventario_env\Scripts\Activate.ps1"

# Instalar dependencias
Write-Host "📦 Verificando dependencias..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt -q
    Write-Host "✅ Dependencias verificadas" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Instalando dependencias..." -ForegroundColor Yellow
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
}

# Verificar si existe la base de datos
if (-not (Test-Path "inventario.db")) {
    Write-Host "🗄️  Creando base de datos de producción..." -ForegroundColor Yellow
    python crear_db_produccion.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ ERROR: No se pudo crear la base de datos" -ForegroundColor Red
        Read-Host "Presiona Enter para salir"
        exit 1
    }
    Write-Host "✅ Base de datos creada" -ForegroundColor Green
}

# Obtener IP local
Write-Host "🌐 Obteniendo dirección IP..." -ForegroundColor Yellow
try {
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object {$_.IPAddress -like "192.168.*" -or $_.IPAddress -like "10.*" -or $_.IPAddress -like "172.*"} | Select-Object -First 1).IPAddress
} catch {
    $ip = "localhost"
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SISTEMA INICIANDO..." -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "📡 Servidor: http://localhost:8000" -ForegroundColor Green
Write-Host "🌐 Red local: http://$ip:8000" -ForegroundColor Green
Write-Host ""
Write-Host "⏳ Iniciando servidor en 3 segundos..." -ForegroundColor Yellow
Write-Host "   (Presiona Ctrl+C para detener)" -ForegroundColor Gray
Write-Host ""

# Esperar 3 segundos
Start-Sleep -Seconds 3

# Abrir navegador
Write-Host "🌐 Abriendo navegador..." -ForegroundColor Yellow
Start-Process "http://localhost:8000"

# Ejecutar servidor
Write-Host "🚀 Iniciando servidor de inventario..." -ForegroundColor Green
python ejecutar_produccion.py

# Si el servidor se detiene, mostrar mensaje
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SERVIDOR DETENIDO" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "El sistema se ha detenido." -ForegroundColor Gray
Write-Host "Para volver a iniciar, ejecuta este script nuevamente." -ForegroundColor Gray
Write-Host ""
Read-Host "Presiona Enter para salir"

