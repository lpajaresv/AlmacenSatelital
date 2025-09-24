from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date, timedelta
import uvicorn

from database import SessionLocal, engine, Base
from models import Producto, Movimiento, Unidad, Grupo, Usuario, RolUsuario
from schemas import ProductoCreate, MovimientoCreate, UnidadCreate, GrupoCreate, UsuarioCreate, UsuarioUpdate, LoginRequest, Token
from auth import (
    authenticate_user, create_access_token, get_current_active_user, 
    get_password_hash, require_admin, require_operador_or_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES, can_access_module
)

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Sistema de Control de Inventario", version="1.0.0")

# Configurar templates y archivos estáticos
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Dependencia para obtener la sesión de base de datos
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rutas principales
@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard principal con resumen del inventario"""
    productos = db.query(Producto).all()
    total_productos = len(productos)
    
    # Calcular stock total y detectar productos con stock bajo
    stock_total = 0
    productos_stock_bajo = []
    
    for producto in productos:
        stock_actual = calcular_stock_actual(db, producto.id)
        stock_total += stock_actual
        
        # Verificar stock bajo
        stock_minimo = producto.stock_minimo or 0
        if stock_minimo > 0 and stock_actual <= stock_minimo:
            productos_stock_bajo.append({
                "producto": producto,
                "stock_actual": stock_actual,
                "stock_minimo": stock_minimo
            })
    
    # Movimientos recientes
    movimientos_recientes = (
        db.query(Movimiento)
        .order_by(Movimiento.fecha.desc(), Movimiento.fecha_creacion.desc())
        .limit(10)
        .all()
    )
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_productos": total_productos,
        "stock_total": stock_total,
        "movimientos_recientes": movimientos_recientes,
        "productos_stock_bajo": productos_stock_bajo,
        "date": date
    })

@app.get("/productos", response_class=HTMLResponse)
async def listar_productos(request: Request, incluir_inactivos: bool = False, db: Session = Depends(get_db)):
    """Página para listar y gestionar productos"""
    if incluir_inactivos:
        productos = db.query(Producto).all()
    else:
        productos = db.query(Producto).filter(Producto.activo == True).all()
    unidades = db.query(Unidad).filter(Unidad.activo == True).order_by(Unidad.nombre.asc()).all()
    grupos = db.query(Grupo).filter(Grupo.activo == True).order_by(Grupo.nombre.asc()).all()
    
    # Calcular stock actual para cada producto
    productos_con_stock = []
    for producto in productos:
        stock_actual = calcular_stock_actual(db, producto.id)
        productos_con_stock.append({
            "producto": producto,
            "stock_actual": stock_actual
        })
    
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos_con_stock": productos_con_stock,
        "unidades": unidades,
        "grupos": grupos,
        "incluir_inactivos": incluir_inactivos,
        "date": date
    })

@app.post("/productos")
async def crear_producto(
    request: Request,
    codigo: str = Form(...),
    nombre: str = Form(...),
    unidad_id: int = Form(...),  # Campo requerido
    grupo_id: int = Form(...),
    stock_minimo: Optional[float] = Form(0.0),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para crear productos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para crear productos")
    # Verificar si el código ya existe
    producto_existente = db.query(Producto).filter(Producto.codigo == codigo).first()
    if producto_existente:
        raise HTTPException(status_code=400, detail="El código de producto ya existe")
    
    # Verificar que la unidad existe y está activa
    unidad = db.query(Unidad).filter(Unidad.id == unidad_id, Unidad.activo == True).first()
    if not unidad:
        raise HTTPException(status_code=400, detail="Unidad no encontrada o inactiva")
    
    # Validar stock mínimo
    if stock_minimo is None or stock_minimo < 0:
        stock_minimo = 0.0
    
    # Verificar que el grupo existe y está activo
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id, Grupo.activo == True).first()
    if not grupo:
        raise HTTPException(status_code=400, detail="Grupo no encontrado o inactivo")
    
    producto = Producto(
        codigo=codigo,
        nombre=nombre,
        unidad_id=unidad_id,
        grupo_id=grupo_id,
        stock_minimo=stock_minimo
    )
    db.add(producto)
    db.commit()
    
    return RedirectResponse(url="/productos", status_code=303)

@app.put("/productos/{producto_id}")
async def editar_producto(
    request: Request,
    producto_id: int,
    codigo: str = Form(...),
    nombre: str = Form(...),
    unidad_id: int = Form(...),  # Campo requerido
    grupo_id: int = Form(...),
    stock_minimo: Optional[float] = Form(0.0),
    activo: str = Form(...),
    db: Session = Depends(get_db)
):
    """Editar un producto existente"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para editar productos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para editar productos")
    # Buscar el producto
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Verificar si el código ya existe en otro producto
    producto_existente = db.query(Producto).filter(
        Producto.codigo == codigo,
        Producto.id != producto_id
    ).first()
    if producto_existente:
        raise HTTPException(status_code=400, detail="El código de producto ya existe")
    
    # Verificar que la unidad existe y está activa
    unidad = db.query(Unidad).filter(Unidad.id == unidad_id, Unidad.activo == True).first()
    if not unidad:
        raise HTTPException(status_code=400, detail="Unidad no encontrada o inactiva")
    
    # Validar stock mínimo
    if stock_minimo is None or stock_minimo < 0:
        stock_minimo = 0.0
    
    # Actualizar el producto
    # Verificar que el grupo existe y está activo
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id, Grupo.activo == True).first()
    if not grupo:
        raise HTTPException(status_code=400, detail="Grupo no encontrado o inactivo")
    
    producto.codigo = codigo
    producto.nombre = nombre
    producto.unidad_id = unidad_id
    producto.grupo_id = grupo_id
    producto.stock_minimo = stock_minimo
    producto.activo = activo.lower() == "true"
    
    db.commit()
    return RedirectResponse(url="/productos", status_code=303)

@app.post("/productos/{producto_id}/edit")
async def editar_producto_post(
    request: Request,
    producto_id: int,
    codigo: str = Form(...),
    nombre: str = Form(...),
    unidad_id: int = Form(...),
    grupo_id: int = Form(...),
    stock_minimo: Optional[float] = Form(0.0),
    activo: str = Form(...),
    db: Session = Depends(get_db)
):
    """Ruta POST para editar producto (compatible con formularios)"""
    return await editar_producto(request, producto_id, codigo, nombre, unidad_id, grupo_id, stock_minimo, activo, db)

@app.post("/productos/{producto_id}/toggle")
async def toggle_producto_activo(request: Request, producto_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar un producto"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para editar productos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para editar productos")
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    # Cambiar el estado activo
    producto.activo = not producto.activo
    db.commit()
    
    return RedirectResponse(url="/productos", status_code=303)

@app.get("/unidades", response_class=HTMLResponse)
async def listar_unidades(request: Request, db: Session = Depends(get_db)):
    """Página para listar y gestionar unidades de medida"""
    unidades = db.query(Unidad).order_by(Unidad.nombre.asc()).all()
    
    return templates.TemplateResponse("unidades.html", {
        "request": request,
        "unidades": unidades,
        "date": date
    })

@app.post("/unidades")
async def crear_unidad(
    request: Request,
    nombre: str = Form(...),
    abreviatura: str = Form(...),
    activo: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    """Crear una nueva unidad de medida"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para crear unidades (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para crear unidades")
    # Verificar si la abreviatura ya existe
    unidad_existente = db.query(Unidad).filter(Unidad.abreviatura == abreviatura).first()
    if unidad_existente:
        raise HTTPException(status_code=400, detail="La abreviatura de unidad ya existe")
    
    unidad = Unidad(
        nombre=nombre,
        abreviatura=abreviatura,
        activo=bool(activo)
    )
    db.add(unidad)
    db.commit()
    
    return RedirectResponse(url="/unidades", status_code=303)

# === RUTAS DE GRUPOS ===
@app.get("/grupos", response_class=HTMLResponse)
async def listar_grupos(request: Request, db: Session = Depends(get_db)):
    """Página para listar y gestionar grupos"""
    grupos = db.query(Grupo).order_by(Grupo.nombre.asc()).all()
    
    return templates.TemplateResponse("grupos.html", {
        "request": request,
        "grupos": grupos,
        "date": date
    })

@app.post("/grupos")
async def crear_grupo(
    request: Request,
    nombre: str = Form(...),
    descripcion: str = Form(""),
    activo: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    """Crear un nuevo grupo"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para crear grupos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para crear grupos")
    # Verificar si el nombre ya existe
    grupo_existente = db.query(Grupo).filter(Grupo.nombre == nombre).first()
    if grupo_existente:
        raise HTTPException(status_code=400, detail="Ya existe un grupo con ese nombre")
    
    grupo = Grupo(
        nombre=nombre,
        descripcion=descripcion if descripcion else None,
        activo=bool(activo)
    )
    db.add(grupo)
    db.commit()
    
    return RedirectResponse(url="/grupos", status_code=303)

@app.post("/grupos/{grupo_id}/toggle")
async def toggle_grupo_activo(request: Request, grupo_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar un grupo"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para editar grupos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para editar grupos")
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    grupo.activo = not grupo.activo
    db.commit()
    
    return RedirectResponse(url="/grupos", status_code=303)

@app.post("/unidades/{unidad_id}/toggle")
async def toggle_unidad_activo(request: Request, unidad_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar una unidad"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para editar unidades (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para editar unidades")
    unidad = db.query(Unidad).filter(Unidad.id == unidad_id).first()
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    unidad.activo = not unidad.activo
    db.commit()
    
    return RedirectResponse(url="/unidades", status_code=303)

@app.get("/movimientos", response_class=HTMLResponse)
async def listar_movimientos(
    request: Request,
    producto_id: Optional[int] = None,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Página para listar movimientos con filtros"""
    query = db.query(Movimiento)
    
    # Aplicar filtros
    if producto_id:
        query = query.filter(Movimiento.producto_id == producto_id)
    
    if fecha_inicio:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        query = query.filter(Movimiento.fecha >= fecha_inicio_obj)
    
    if fecha_fin:
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        query = query.filter(Movimiento.fecha <= fecha_fin_obj)
    
    movimientos = query.order_by(Movimiento.fecha.desc(), Movimiento.fecha_creacion.desc()).all()
    productos = db.query(Producto).filter(Producto.activo == True).all()
    
    return templates.TemplateResponse("movimientos.html", {
        "request": request,
        "movimientos": movimientos,
        "productos": productos,
        "filtros": {
            "producto_id": producto_id,
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "date": date
    })

@app.post("/movimientos")
async def crear_movimiento(
    request: Request,
    producto_id: int = Form(...),
    tipo: str = Form(...),
    cantidad: float = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha: str = Form(...),
    db: Session = Depends(get_db)
):
    """Crear un nuevo movimiento de inventario"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que tenga permisos para crear movimientos (operador o admin)
    if current_user.rol not in [RolUsuario.OPERADOR.value, RolUsuario.ADMIN.value]:
        raise HTTPException(status_code=403, detail="Se requiere rol de operador o administrador para crear movimientos")
    # Verificar que el producto existe
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d").date()
    
    movimiento = Movimiento(
        producto_id=producto_id,
        tipo=tipo,
        cantidad=cantidad,
        descripcion=descripcion,
        fecha=fecha_obj
    )
    db.add(movimiento)
    db.commit()
    
    return RedirectResponse(url="/movimientos", status_code=303)

@app.get("/kardex/{producto_id}", response_class=HTMLResponse)
async def kardex_producto(
    request: Request,
    producto_id: int,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Página del kardex de un producto específico"""
    producto = db.query(Producto).filter(Producto.id == producto_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    
    query = db.query(Movimiento).filter(Movimiento.producto_id == producto_id)
    
    # Aplicar filtros de fecha
    if fecha_inicio:
        fecha_inicio_obj = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        query = query.filter(Movimiento.fecha >= fecha_inicio_obj)
    
    if fecha_fin:
        fecha_fin_obj = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
        query = query.filter(Movimiento.fecha <= fecha_fin_obj)
    
    # Obtener movimientos ordenados cronológicamente para cálculo de saldos
    movimientos_cronologicos = query.order_by(Movimiento.fecha.asc(), Movimiento.fecha_creacion.asc()).all()
    
    # Calcular saldos progresivos
    kardex = []
    saldo = 0
    
    for movimiento in movimientos_cronologicos:
        if movimiento.tipo == "entrada":
            saldo += movimiento.cantidad
        else:  # salida
            saldo -= movimiento.cantidad
        
        kardex.append({
            "movimiento": movimiento,
            "saldo": saldo
        })
    
    # Invertir el kardex para mostrar los movimientos más recientes primero
    kardex.reverse()
    
    return templates.TemplateResponse("kardex.html", {
        "request": request,
        "producto": producto,
        "kardex": kardex,
        "filtros": {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin
        },
        "date": date
    })

def calcular_stock_actual(db: Session, producto_id: int) -> float:
    """Calcular el stock actual de un producto"""
    movimientos = db.query(Movimiento).filter(
        Movimiento.producto_id == producto_id
    ).all()
    
    stock = 0
    for movimiento in movimientos:
        if movimiento.tipo == "entrada":
            stock += movimiento.cantidad
        else:  # salida
            stock -= movimiento.cantidad
    
    return stock

# ===== RUTAS DE AUTENTICACIÓN Y GESTIÓN DE USUARIOS =====

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Página de login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """Autenticar usuario"""
    print(f"Intento de login para usuario: {username}")
    
    user = authenticate_user(db, username, password)
    if not user:
        print(f"Login fallido para usuario: {username}")
        return templates.TemplateResponse("login.html", {
            "request": request,
            "error": "Usuario o contraseña incorrectos"
        })
    
    print(f"Login exitoso para usuario: {username}, rol: {user.rol}")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    print(f"Token creado: {access_token[:50]}...")
    
    # Crear respuesta de redirección con token
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(
        key="access_token", 
        value=access_token, 
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        secure=False,  # Cambiar a True en producción con HTTPS
        samesite="lax"
    )
    
    print("Redirigiendo a /")
    return response

@app.get("/logout")
async def logout():
    """Cerrar sesión"""
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(key="access_token")
    return response

@app.get("/usuarios", response_class=HTMLResponse)
async def listar_usuarios(
    request: Request, 
    db: Session = Depends(get_db)
):
    """Listar usuarios (solo admin)"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que sea administrador
    if current_user.rol != RolUsuario.ADMIN.value:
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    
    usuarios = db.query(Usuario).order_by(Usuario.nombre_completo.asc()).all()
    return templates.TemplateResponse("usuarios.html", {
        "request": request,
        "usuarios": usuarios,
        "roles": [rol.value for rol in RolUsuario],
        "current_user": current_user
    })

@app.post("/usuarios")
async def crear_usuario(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    nombre_completo: str = Form(...),
    password: str = Form(...),
    rol: str = Form(...),
    db: Session = Depends(get_db)
):
    """Crear nuevo usuario (solo admin)"""
    print(f"Intentando crear usuario: {username}, email: {email}, rol: {rol}")
    
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        print("No hay usuario autenticado")
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que sea administrador
    if current_user.rol != RolUsuario.ADMIN.value:
        print(f"Usuario {current_user.username} no es administrador, rol: {current_user.rol}")
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    
    # Verificar si el username ya existe
    usuario_existente = db.query(Usuario).filter(Usuario.username == username).first()
    if usuario_existente:
        print(f"Username {username} ya existe")
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    
    # Verificar si el email ya existe
    email_existente = db.query(Usuario).filter(Usuario.email == email).first()
    if email_existente:
        print(f"Email {email} ya existe")
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    
    # Validar rol
    if rol not in [r.value for r in RolUsuario]:
        print(f"Rol inválido: {rol}")
        raise HTTPException(status_code=400, detail="Rol inválido")
    
    try:
        usuario = Usuario(
            username=username,
            email=email,
            nombre_completo=nombre_completo,
            hashed_password=get_password_hash(password),
            rol=rol
        )
        
        db.add(usuario)
        db.commit()
        print(f"Usuario {username} creado exitosamente")
        
        return RedirectResponse(url="/usuarios", status_code=303)
    except Exception as e:
        print(f"Error al crear usuario: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")

@app.post("/usuarios/{usuario_id}/toggle")
async def toggle_usuario_activo(
    request: Request,
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """Activar/desactivar usuario (solo admin)"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que sea administrador
    if current_user.rol != RolUsuario.ADMIN.value:
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # No permitir desactivar el propio usuario
    if usuario.id == current_user.id:
        raise HTTPException(status_code=400, detail="No puedes desactivar tu propio usuario")
    
    usuario.activo = not usuario.activo
    db.commit()
    
    return RedirectResponse(url="/usuarios", status_code=303)

@app.post("/usuarios/{usuario_id}/cambiar-password")
async def cambiar_password_usuario(
    request: Request,
    usuario_id: int,
    password_nueva: str = Form(...),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña de usuario (solo admin)"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar que sea administrador
    if current_user.rol != RolUsuario.ADMIN.value:
        raise HTTPException(status_code=403, detail="Se requiere rol de administrador")
    
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    usuario.hashed_password = get_password_hash(password_nueva)
    db.commit()
    
    return RedirectResponse(url="/usuarios", status_code=303)

@app.get("/perfil", response_class=HTMLResponse)
async def perfil_usuario(
    request: Request
):
    """Página de perfil del usuario"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    return templates.TemplateResponse("perfil.html", {
        "request": request,
        "usuario": current_user
    })

@app.post("/perfil/cambiar-password")
async def cambiar_password_perfil(
    request: Request,
    password_actual: str = Form(...),
    password_nueva: str = Form(...),
    db: Session = Depends(get_db)
):
    """Cambiar contraseña del perfil actual"""
    # Obtener usuario actual del middleware
    current_user = getattr(request.state, 'current_user', None)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    
    from auth import verify_password
    
    if not verify_password(password_actual, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Contraseña actual incorrecta")
    
    current_user.hashed_password = get_password_hash(password_nueva)
    db.commit()
    
    return RedirectResponse(url="/perfil?success=password_changed", status_code=303)

# ===== MIDDLEWARE DE AUTENTICACIÓN =====

@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    """Middleware para verificar autenticación en rutas protegidas"""
    # Rutas que no requieren autenticación
    public_routes = ["/login", "/static", "/docs", "/openapi.json", "/favicon.ico"]
    
    if any(request.url.path.startswith(route) for route in public_routes):
        response = await call_next(request)
        return response
    
    # Verificar token en cookie
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login", status_code=303)
    
    # Verificar token (simplificado para middleware)
    try:
        from auth import verify_token
        token_data = verify_token(token)
        
        # Agregar usuario a la request para uso posterior
        db = SessionLocal()
        try:
            user = db.query(Usuario).filter(Usuario.username == token_data.username).first()
            if user and user.activo:
                request.state.current_user = user
            else:
                return RedirectResponse(url="/login", status_code=303)
        finally:
            db.close()
            
    except Exception as e:
        print(f"Error en middleware de auth: {e}")
        return RedirectResponse(url="/login", status_code=303)
    
    response = await call_next(request)
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
