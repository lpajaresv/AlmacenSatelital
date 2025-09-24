from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Usuario, RolUsuario
from schemas import TokenData

# Configuración de seguridad
SECRET_KEY = "tu-clave-secreta-super-segura-cambiar-en-produccion"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Configuración de hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración de autenticación
security = HTTPBearer()

def get_db():
    """Dependencia para obtener la sesión de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generar hash de contraseña"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Crear token de acceso JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_credentials_exception():
    """Obtener excepción de credenciales"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

def verify_token(token: str, credentials_exception=None):
    """Verificar token JWT"""
    if credentials_exception is None:
        credentials_exception = get_credentials_exception()
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        return token_data
    except JWTError:
        raise credentials_exception

def authenticate_user(db: Session, username: str, password: str) -> Optional[Usuario]:
    """Autenticar usuario"""
    user = db.query(Usuario).filter(Usuario.username == username).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    if not user.activo:
        return None
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """Obtener usuario actual desde el token"""
    credentials_exception = get_credentials_exception()
    
    token = credentials.credentials
    token_data = verify_token(token, credentials_exception)
    
    user = db.query(Usuario).filter(Usuario.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    # Actualizar último acceso
    user.ultimo_acceso = datetime.now()
    db.commit()
    
    return user

def get_current_active_user(current_user: Usuario = Depends(get_current_user)) -> Usuario:
    """Obtener usuario activo actual"""
    if not current_user.activo:
        raise HTTPException(status_code=400, detail="Usuario inactivo")
    return current_user

def require_role(required_role: RolUsuario):
    """Decorador para requerir un rol específico"""
    def role_checker(current_user: Usuario = Depends(get_current_active_user)):
        if current_user.rol != required_role.value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción"
            )
        return current_user
    return role_checker

def require_admin(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """Requerir rol de administrador"""
    if current_user.rol != RolUsuario.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador"
        )
    return current_user

def require_operador_or_admin(current_user: Usuario = Depends(get_current_active_user)) -> Usuario:
    """Requerir rol de operador o administrador"""
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de operador o administrador"
        )
    return current_user

def can_access_module(current_user: Usuario, module: str) -> bool:
    """Verificar si el usuario puede acceder a un módulo específico"""
    if current_user.rol == RolUsuario.ADMIN.value:
        return True
    
    # Definir permisos por módulo
    permissions = {
        "productos": [RolUsuario.ADMIN.value, RolUsuario.OPERADOR.value, RolUsuario.CONSULTA.value],
        "movimientos": [RolUsuario.ADMIN.value, RolUsuario.OPERADOR.value],
        "usuarios": [RolUsuario.ADMIN.value],
        "reportes": [RolUsuario.ADMIN.value, RolUsuario.OPERADOR.value, RolUsuario.CONSULTA.value],
        "configuracion": [RolUsuario.ADMIN.value]
    }
    
    return current_user.rol in permissions.get(module, [])
