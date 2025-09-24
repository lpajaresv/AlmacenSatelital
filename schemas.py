from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional
from enum import Enum

class RolUsuario(str, Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    CONSULTA = "consulta"

# Schemas para Usuarios
class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: str
    rol: RolUsuario = RolUsuario.CONSULTA
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str

class UsuarioUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    nombre_completo: Optional[str] = None
    rol: Optional[RolUsuario] = None
    activo: Optional[bool] = None

class UsuarioChangePassword(BaseModel):
    password_actual: str
    password_nueva: str

class Usuario(UsuarioBase):
    id: int
    fecha_creacion: datetime
    ultimo_acceso: Optional[datetime] = None

    class Config:
        from_attributes = True

# Schemas para Autenticación
class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

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
