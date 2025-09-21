from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, date
from database import Base

class Grupo(Base):
    __tablename__ = "grupos"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), unique=True, index=True, nullable=False)
    descripcion = Column(String(500), nullable=True)
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relación con productos
    productos = relationship("Producto", back_populates="grupo_rel")

class Unidad(Base):
    __tablename__ = "unidades"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), nullable=False)  # ej: Pieza, Kilogramo, Litro
    abreviatura = Column(String(10), unique=True, index=True, nullable=False)  # ej: pza, kg, lt
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relación con productos
    productos = relationship("Producto", back_populates="unidad_rel")

class Producto(Base):
    __tablename__ = "productos"
    
    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(50), unique=True, index=True, nullable=False)
    nombre = Column(String(200), nullable=False)
    unidad_id = Column(Integer, ForeignKey("unidades.id"), nullable=False)  # Campo requerido
    grupo_id = Column(Integer, ForeignKey("grupos.id"), nullable=False)  # Campo requerido
    stock_minimo = Column(Float, nullable=True, default=0.0)  # Stock mínimo del producto
    activo = Column(Boolean, default=True, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relaciones
    unidad_rel = relationship("Unidad", back_populates="productos")
    grupo_rel = relationship("Grupo", back_populates="productos")
    movimientos = relationship("Movimiento", back_populates="producto")

class Movimiento(Base):
    __tablename__ = "movimientos"
    
    id = Column(Integer, primary_key=True, index=True)
    producto_id = Column(Integer, ForeignKey("productos.id"), nullable=False)
    tipo = Column(String(20), nullable=False)  # "entrada" o "salida"
    cantidad = Column(Float, nullable=False)
    descripcion = Column(String(500))
    fecha = Column(Date, nullable=False)
    fecha_creacion = Column(DateTime, default=datetime.now)
    
    # Relación con producto
    producto = relationship("Producto", back_populates="movimientos")
