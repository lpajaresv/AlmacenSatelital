#!/usr/bin/env python3
"""
Script para importar inventario inicial desde Excel
Almacén Satelital San Luis
"""

import pandas as pd
import os
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Producto, Movimiento, Unidad, Grupo
from datetime import datetime, date

def validar_archivo_excel(archivo_excel):
    """Validar que el archivo Excel existe y tiene la estructura correcta"""
    if not os.path.exists(archivo_excel):
        print(f"❌ Error: No se encontró el archivo {archivo_excel}")
        return False
    
    try:
        # Leer solo la primera fila para validar columnas
        df_test = pd.read_excel(archivo_excel, nrows=1)
        columnas_esperadas = ['Codigo', 'Nombre', 'Unidad', 'Grupo', 'Cantidad Inicial']
        
        for col in columnas_esperadas:
            if col not in df_test.columns:
                print(f"❌ Error: Falta la columna '{col}' en el archivo Excel")
                print(f"📋 Columnas encontradas: {list(df_test.columns)}")
                return False
        
        print("✅ Archivo Excel validado correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error al leer el archivo Excel: {e}")
        return False

def obtener_mapas_referencia(db):
    """Obtener mapas de unidades y grupos existentes"""
    # Mapa de unidades (por abreviatura y nombre)
    unidades = db.query(Unidad).filter(Unidad.activo == True).all()
    mapa_unidades = {}
    for unidad in unidades:
        mapa_unidades[unidad.abreviatura.lower()] = unidad.id
        mapa_unidades[unidad.nombre.lower()] = unidad.id
    
    # Mapa de grupos (por nombre)
    grupos = db.query(Grupo).filter(Grupo.activo == True).all()
    mapa_grupos = {}
    for grupo in grupos:
        mapa_grupos[grupo.nombre.lower()] = grupo.id
    
    print(f"📏 Unidades disponibles: {', '.join([u.abreviatura for u in unidades])}")
    print(f"🏷️  Grupos disponibles: {', '.join([g.nombre for g in grupos])}")
    
    return mapa_unidades, mapa_grupos

def procesar_fila(fila, mapa_unidades, mapa_grupos, db, errores):
    """Procesar una fila del Excel y crear producto + movimiento"""
    try:
        # Obtener datos de la fila
        codigo = str(fila['Codigo']).strip()
        nombre = str(fila['Nombre']).strip()
        unidad_str = str(fila['Unidad']).strip()
        grupo_str = str(fila['Grupo']).strip()
        cantidad_inicial = float(fila['Cantidad Inicial']) if pd.notna(fila['Cantidad Inicial']) else 0.0
        
        # Validar datos básicos
        if not codigo or codigo == 'nan':
            errores.append(f"Fila sin código válido: {fila.to_dict()}")
            return False
        
        if not nombre or nombre == 'nan':
            errores.append(f"Producto {codigo}: Sin nombre válido")
            return False
        
        # Buscar unidad
        unidad_id = None
        unidad_key = unidad_str.lower()
        if unidad_key in mapa_unidades:
            unidad_id = mapa_unidades[unidad_key]
        else:
            errores.append(f"Producto {codigo}: Unidad '{unidad_str}' no encontrada")
            return False
        
        # Buscar grupo
        grupo_id = None
        grupo_key = grupo_str.lower()
        if grupo_key in mapa_grupos:
            grupo_id = mapa_grupos[grupo_key]
        else:
            errores.append(f"Producto {codigo}: Grupo '{grupo_str}' no encontrado")
            return False
        
        # Verificar si el producto ya existe
        producto_existente = db.query(Producto).filter(Producto.codigo == codigo).first()
        if producto_existente:
            errores.append(f"Producto {codigo}: Ya existe en la base de datos")
            return False
        
        # Crear producto
        producto = Producto(
            codigo=codigo,
            nombre=nombre,
            unidad_id=unidad_id,
            grupo_id=grupo_id,
            stock_minimo=0.0,  # Se puede ajustar manualmente después
            activo=True
        )
        db.add(producto)
        db.flush()  # Para obtener el ID del producto
        
        # Crear movimiento de entrada inicial si hay cantidad
        # Usar producto_id en lugar de codigo_producto (corregido para nueva estructura)
        if cantidad_inicial > 0:
            movimiento = Movimiento(
                producto_id=producto.id,
                tipo="entrada",
                cantidad=cantidad_inicial,
                descripcion="Retorno de correctivos X14 del 17/09/2025)",
                fecha=date.today()
            )
            db.add(movimiento)
        
        print(f"   ✅ {codigo} - {nombre} (Stock: {cantidad_inicial})")
        return True
        
    except Exception as e:
        errores.append(f"Error procesando fila {codigo if 'codigo' in locals() else 'desconocido'}: {str(e)}")
        return False

def importar_inventario_desde_excel(archivo_excel):
    """Función principal para importar inventario desde Excel"""
    print("📊 IMPORTACIÓN DE INVENTARIO INICIAL DESDE EXCEL")
    print("   Almacén Satelital San Luis")
    print("=" * 60)
    
    # Validar archivo
    if not validar_archivo_excel(archivo_excel):
        return False
    
    # Leer archivo Excel
    try:
        print(f"📖 Leyendo archivo: {archivo_excel}")
        df = pd.read_excel(archivo_excel)
        print(f"📋 Productos encontrados en Excel: {len(df)}")
        
        if len(df) == 0:
            print("⚠️  El archivo Excel está vacío")
            return False
        
    except Exception as e:
        print(f"❌ Error al leer Excel: {e}")
        return False
    
    # Conectar a base de datos
    db = SessionLocal()
    errores = []
    productos_creados = 0
    movimientos_creados = 0
    
    try:
        # Obtener mapas de referencia
        print("\n🔍 Obteniendo datos de referencia...")
        mapa_unidades, mapa_grupos = obtener_mapas_referencia(db)
        
        print(f"\n📦 PROCESANDO {len(df)} PRODUCTOS")
        print("-" * 50)
        
        # Procesar cada fila
        for index, fila in df.iterrows():
            if procesar_fila(fila, mapa_unidades, mapa_grupos, db, errores):
                productos_creados += 1
                # Contar movimientos (solo si hay cantidad inicial > 0)
                if pd.notna(fila['Cantidad Inicial']) and float(fila['Cantidad Inicial']) > 0:
                    movimientos_creados += 1
        
        # Confirmar cambios
        db.commit()
        
        # Mostrar resultados
        print(f"\n🎯 RESULTADOS DE LA IMPORTACIÓN")
        print("=" * 50)
        print(f"✅ Productos creados: {productos_creados}")
        print(f"✅ Movimientos de entrada: {movimientos_creados}")
        print(f"⚠️  Errores encontrados: {len(errores)}")
        
        if errores:
            print(f"\n📝 ERRORES DETALLADOS:")
            print("-" * 30)
            for i, error in enumerate(errores, 1):
                print(f"{i:2d}. {error}")
        
        if productos_creados > 0:
            print(f"\n🚀 ¡INVENTARIO INICIAL IMPORTADO EXITOSAMENTE!")
            print(f"   El almacén satelital San Luis está listo con {productos_creados} productos")
        
        return productos_creados > 0
        
    except Exception as e:
        print(f"❌ Error durante la importación: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    """Función principal"""
    print("🏭 IMPORTADOR DE INVENTARIO INICIAL")
    print("=" * 60)
    
    # Buscar archivo Excel en el directorio actual
    archivos_excel = [f for f in os.listdir('.') if f.endswith('.xlsx') or f.endswith('.xls')]
    
    if not archivos_excel:
        print("❌ No se encontraron archivos Excel (.xlsx o .xls) en el directorio actual")
        print("📁 Coloca tu archivo Excel en la misma carpeta que este script")
        return
    
    if len(archivos_excel) == 1:
        archivo_excel = archivos_excel[0]
        print(f"📊 Archivo Excel encontrado: {archivo_excel}")
    else:
        print("📊 Archivos Excel encontrados:")
        for i, archivo in enumerate(archivos_excel, 1):
            print(f"   {i}. {archivo}")
        
        try:
            seleccion = int(input("\nSelecciona el número del archivo a importar: ")) - 1
            archivo_excel = archivos_excel[seleccion]
        except (ValueError, IndexError):
            print("❌ Selección inválida")
            return
    
    # Importar inventario
    exito = importar_inventario_desde_excel(archivo_excel)
    
    if exito:
        print(f"\n🎉 ¡IMPORTACIÓN COMPLETADA!")
        print("   Puedes ejecutar 'python ejecutar_produccion.py' para iniciar el sistema")
    else:
        print(f"\n❌ La importación no se completó exitosamente")

if __name__ == "__main__":
    main()

