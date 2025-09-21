#!/usr/bin/env python3
"""
Script para crear base de datos limpia para producción
Almacén Satelital San Luis
"""

import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Producto, Movimiento, Unidad, Grupo
from datetime import datetime

def limpiar_base_datos():
    """Eliminar base de datos existente y crear nueva"""
    print("🧹 CREANDO BASE DE DATOS LIMPIA PARA PRODUCCIÓN")
    print("=" * 60)
    
    # Eliminar base de datos existente
    if os.path.exists("inventario.db"):
        print("⚠️  Eliminando base de datos anterior...")
        os.remove("inventario.db")
    
    # Crear todas las tablas
    print("🏗️  Creando estructura de tablas...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tablas creadas exitosamente")

def agregar_datos_esenciales():
    """Agregar datos básicos esenciales para comenzar"""
    db = SessionLocal()
    
    try:
        print("\n📦 AGREGANDO DATOS ESENCIALES")
        print("-" * 40)
        
        # 1. Unidades de medida básicas
        print("📏 Creando unidades de medida...")
        unidades_basicas = [
            {"nombre": "Unidad", "abreviatura": "Und"},
            {"nombre": "Kilogramo", "abreviatura": "kg"},
            {"nombre": "Litro", "abreviatura": "lt"},
            {"nombre": "Metro", "abreviatura": "m"},
            {"nombre": "Kit", "abreviatura": "Kit"},
            {"nombre": "Balde x 5 Galones", "abreviatura": "Balx5Gal"},
            {"nombre": "Galón", "abreviatura": "gal"}
        ]
        
        for unidad_data in unidades_basicas:
            unidad = Unidad(
                nombre=unidad_data["nombre"],
                abreviatura=unidad_data["abreviatura"],
                activo=True
            )
            db.add(unidad)
        
        db.commit()
        print(f"   ✅ {len(unidades_basicas)} unidades creadas")
        
        # 2. Grupos de productos básicos
        print("🏷️  Creando grupos de productos...")
        grupos_basicos = [
            {"nombre": "Repuestos en General", "descripcion": "Repuestos en general"},
            {"nombre": "Valvulas", "descripcion": "Valvulas"},
            {"nombre": "Sistema Electrico", "descripcion": "Componentes eléctricos y electrónicos"},
            {"nombre": "Filtros", "descripcion": "Filtros de aire, aceite, combustible, etc."},
            {"nombre": "Aceites y Lubricantes", "descripcion": "Aceites, grasas, lubricantes, refrigerantes, etc."},
            {"nombre": "Neumáticos", "descripcion": "Neumáticos y cámaras"},
            {"nombre": "Herramientas", "descripcion": "Herramientas y equipos de trabajo"},
            {"nombre": "General", "descripcion": "Bienes en general"},
            {"nombre": "Implementos para equipos", "descripcion": "Implementos para equipos"},
            {"nombre": "Sensores", "descripcion": "Sensores"},
            {"nombre": "Radios", "descripcion": "Radios para comunicaciones"},
            {"nombre": "Sellos", "descripcion": "Sellos"},
            {"nombre": "Parabrisas", "descripcion": "Parabrisas"},
            {"nombre": "Mangueras", "descripcion": "Mangueras hidráulicas, de motor, etc"},
            {"nombre": "Fajas", "descripcion": "Fajas"}

        ]
        
        for grupo_data in grupos_basicos:
            grupo = Grupo(
                nombre=grupo_data["nombre"],
                descripcion=grupo_data["descripcion"],
                activo=True
            )
            db.add(grupo)
        
        db.commit()
        print(f"   ✅ {len(grupos_basicos)} grupos creados")
        
        print("\n🎯 BASE DE DATOS LISTA PARA PRODUCCIÓN")
        print("=" * 60)
        print("✅ Estructura de tablas: Creada")
        print(f"✅ Unidades de medida: {len(unidades_basicas)} básicas")
        print(f"✅ Grupos de productos: {len(grupos_basicos)} básicos")
        print("✅ Productos: 0 (listo para agregar)")
        print("✅ Movimientos: 0 (listo para registrar)")
        print("\n🚀 El sistema está listo para usar en producción")
        print("📋 Puedes empezar agregando tus productos reales")
        
    except Exception as e:
        print(f"❌ Error al crear datos esenciales: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Función principal"""
    print("🏭 PREPARACIÓN DE BASE DE DATOS PARA PRODUCCIÓN")
    print("   Almacén Satelital San Luis")
    print("=" * 60)
    
    # Proceder automáticamente para crear DB de producción
    print("🚀 Creando base de datos de producción automáticamente...")
    
    # Limpiar y crear nueva base de datos
    limpiar_base_datos()
    
    # Agregar datos esenciales
    agregar_datos_esenciales()
    
    print("\n" + "=" * 60)
    print("🎉 ¡BASE DE DATOS DE PRODUCCIÓN CREADA EXITOSAMENTE!")
    print("   Almacén Satelital San Luis está listo para operar")
    print("=" * 60)

if __name__ == "__main__":
    main()
