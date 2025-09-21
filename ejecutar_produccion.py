#!/usr/bin/env python3
"""
Script para ejecutar el sistema de inventario en producción (red local)
Configurado para almacén satelital
"""

import os
import uvicorn
from datetime import datetime
import shutil

def crear_backup_bd():
    """Crear backup automático de la base de datos"""
    if os.path.exists("inventario.db"):
        backup_dir = "backups"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{backup_dir}/inventario_backup_{timestamp}.db"
        
        try:
            shutil.copy2("inventario.db", backup_file)
            print(f"✅ Backup creado: {backup_file}")
        except Exception as e:
            print(f"⚠️  Error al crear backup: {e}")

def mostrar_info_red():
    """Mostrar información de acceso en red"""
    import socket
    
    # Obtener IP local
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_local = s.getsockname()[0]
        s.close()
    except:
        ip_local = "localhost"
    
    print("\n" + "="*60)
    print("🏭 SISTEMA DE INVENTARIO - ALMACÉN SATELITAL")
    print("="*60)
    print(f"📡 Servidor iniciado en: http://{ip_local}:8000")
    print(f"🌐 Acceso local: http://localhost:8000")
    print(f"📱 Desde otros equipos en la red: http://{ip_local}:8000")
    print("\n💡 INSTRUCCIONES:")
    print("   • Desde la misma computadora: usa localhost:8000")
    print("   • Desde otras computadoras en la red: usa la IP mostrada")
    print("   • Para detener: presiona Ctrl+C")
    print("\n📋 GESTIÓN DE DATOS:")
    print("   • Base de datos: inventario.db")
    print("   • Backups automáticos en: ./backups/")
    print("   • Para backup manual: copia inventario.db")
    print("="*60 + "\n")

def main():
    print("🚀 Iniciando Sistema de Inventario para Almacén Satelital...")
    
    # Crear backup al iniciar
    crear_backup_bd()
    
    # Mostrar información de red
    mostrar_info_red()
    
    # Configuración para red local
    config = {
        "app": "main:app",
        "host": "0.0.0.0",  # Permite acceso desde toda la red local
        "port": 8000,
        "reload": False,    # Estabilidad en producción
        "workers": 1,       # Suficiente para 1-2 usuarios
        "access_log": True,
        "log_level": "info"
    }
    
    try:
        uvicorn.run(**config)
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor detenido por el usuario")
        print("📁 Base de datos guardada en: inventario.db")
        print("💾 Backups disponibles en: ./backups/")
    except Exception as e:
        print(f"\n❌ Error al iniciar servidor: {e}")

if __name__ == "__main__":
    main()
