#!/usr/bin/env python3
"""
Script para crear el usuario administrador inicial del sistema.
Ejecutar: python crear_admin.py
"""

from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Usuario, RolUsuario
from auth import get_password_hash
import sys

def crear_usuario_admin():
    """Crear usuario administrador inicial"""
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Verificar si ya existe un admin
        admin_existente = db.query(Usuario).filter(Usuario.rol == RolUsuario.ADMIN.value).first()
        if admin_existente:
            print(f"❌ Ya existe un usuario administrador: {admin_existente.username}")
            return False
        
        # Crear usuario administrador
        admin = Usuario(
            username="admin",
            email="admin@almacensatelital.com",
            nombre_completo="Administrador del Sistema",
            hashed_password=get_password_hash("admin123"),
            rol=RolUsuario.ADMIN.value,
            activo=True
        )
        
        db.add(admin)
        db.commit()
        
        print("✅ Usuario administrador creado exitosamente!")
        print(f"   Usuario: admin")
        print(f"   Contraseña: admin123")
        print(f"   Email: admin@almacensatelital.com")
        print("\n⚠️  IMPORTANTE: Cambia la contraseña después del primer login")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al crear usuario administrador: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def crear_usuarios_ejemplo():
    """Crear usuarios de ejemplo para testing"""
    
    db = SessionLocal()
    try:
        usuarios_ejemplo = [
            {
                "username": "hpajares",
                "email": "hector.pajares@caralmaq.pe",
                "nombre_completo": "Héctor Pajares",
                "rol": RolUsuario.OPERADOR.value
            },
            {
                "username": "equispe",
                "email": "edgar.quispe@caralmaq.pe",
                "nombre_completo": "Edgar Quispe",
                "rol": RolUsuario.CONSULTA.value
            }
        ]
        
        for user_data in usuarios_ejemplo:
            # Verificar si ya existe
            usuario_existente = db.query(Usuario).filter(Usuario.username == user_data["username"]).first()
            if usuario_existente:
                print(f"⚠️  Usuario {user_data['username']} ya existe, omitiendo...")
                continue
            
            usuario = Usuario(
                username=user_data["username"],
                email=user_data["email"],
                nombre_completo=user_data["nombre_completo"],
                hashed_password=get_password_hash("password123"),
                rol=user_data["rol"],
                activo=True
            )
            
            db.add(usuario)
        
        db.commit()
        print("✅ Usuarios de ejemplo creados exitosamente!")
        print("   Usuarios: operador1, consulta1")
        print("   Contraseña para ambos: password123")
        
    except Exception as e:
        print(f"❌ Error al crear usuarios de ejemplo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 Configurando sistema de usuarios...")
    print("=" * 50)
    
    # Crear usuario administrador
    if crear_usuario_admin():
        print("\n" + "=" * 50)
        
        # Preguntar si crear usuarios de ejemplo
        respuesta = input("¿Crear usuarios de ejemplo? (s/n): ").lower().strip()
        if respuesta in ['s', 'si', 'sí', 'y', 'yes']:
            crear_usuarios_ejemplo()
    
    print("\n" + "=" * 50)
    print("🎉 Configuración completada!")
    print("   Ejecuta: python main.py")
    print("   Accede a: http://localhost:8000")




