from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

class GrupoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    activo: bool = True

class GrupoCreate(GrupoBase):
    pass

class Grupo(GrupoBase):
    id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True

class UnidadBase(BaseModel):
    nombre: str
    abreviatura: str
    activo: bool = True

class UnidadCreate(UnidadBase):
    pass

class Unidad(UnidadBase):
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class ProductoBase(BaseModel):
    codigo: str
    nombre: str
    unidad_id: int  # Campo requerido
    grupo_id: int
    stock_minimo: Optional[float] = 0.0

class ProductoCreate(ProductoBase):
    pass

class Producto(ProductoBase):
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True

class MovimientoBase(BaseModel):
    producto_id: int
    tipo: str  # "entrada" o "salida"
    cantidad: float
    descripcion: Optional[str] = None
    fecha: date

class MovimientoCreate(MovimientoBase):
    pass

class Movimiento(MovimientoBase):
    id: int
    fecha_creacion: datetime
    
    class Config:
        from_attributes = True
