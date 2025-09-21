from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, date
import uvicorn

from database import SessionLocal, engine, Base
from models import Producto, Movimiento, Unidad, Grupo
from schemas import ProductoCreate, MovimientoCreate, UnidadCreate, GrupoCreate

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
    codigo: str = Form(...),
    nombre: str = Form(...),
    unidad_id: int = Form(...),  # Campo requerido
    grupo_id: int = Form(...),
    stock_minimo: Optional[float] = Form(0.0),
    db: Session = Depends(get_db)
):
    """Crear un nuevo producto"""
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
    return await editar_producto(producto_id, codigo, nombre, unidad_id, grupo_id, stock_minimo, activo, db)

@app.post("/productos/{producto_id}/toggle")
async def toggle_producto_activo(producto_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar un producto"""
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
    nombre: str = Form(...),
    abreviatura: str = Form(...),
    activo: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    """Crear una nueva unidad de medida"""
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
    nombre: str = Form(...),
    descripcion: str = Form(""),
    activo: bool = Form(default=True),
    db: Session = Depends(get_db)
):
    """Crear un nuevo grupo"""
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
async def toggle_grupo_activo(grupo_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar un grupo"""
    grupo = db.query(Grupo).filter(Grupo.id == grupo_id).first()
    if not grupo:
        raise HTTPException(status_code=404, detail="Grupo no encontrado")
    
    grupo.activo = not grupo.activo
    db.commit()
    
    return RedirectResponse(url="/grupos", status_code=303)

@app.post("/unidades/{unidad_id}/toggle")
async def toggle_unidad_activo(unidad_id: int, db: Session = Depends(get_db)):
    """Activar/desactivar una unidad"""
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
    producto_id: int = Form(...),
    tipo: str = Form(...),
    cantidad: float = Form(...),
    descripcion: Optional[str] = Form(None),
    fecha: str = Form(...),
    db: Session = Depends(get_db)
):
    """Crear un nuevo movimiento de inventario"""
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
