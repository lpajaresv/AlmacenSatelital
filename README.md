# 📦 Sistema de Control de Inventario

Sistema moderno y completo para la gestión de inventarios desarrollado con **Python FastAPI**.

## 🚀 Características

- ✅ **Gestión de Productos**: Registro completo con código, nombre, unidad y grupo
- ✅ **Control de Movimientos**: Entradas y salidas de inventario con seguimiento detallado
- ✅ **Kardex por Producto**: Historial completo con saldos progresivos
- ✅ **Filtros por Fechas**: Consultas específicas por rangos de tiempo
- ✅ **Dashboard Interactivo**: Resúmenes y estadísticas en tiempo real
- ✅ **Interfaz Moderna**: Diseño responsive y amigable
- ✅ **Base de Datos SQLite**: Fácil configuración y portabilidad

## 🛠️ Tecnologías Utilizadas

- **Backend**: FastAPI (Python)
- **Base de Datos**: SQLite con SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript vanilla
- **Templating**: Jinja2
- **Estilos**: CSS Grid, Flexbox, Gradientes modernos

## 📋 Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd InventarioSatelital
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecutar la Aplicación

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Acceder al Sistema

Abre tu navegador en: `http://localhost:8000`

## 🔄 Control de Versiones

Este proyecto utiliza Git para el control de versiones. Para trabajar con el código:

### Comandos Básicos de Git

```bash
# Ver el estado del repositorio
git status

# Agregar archivos al área de staging
git add .

# Hacer commit de los cambios
git commit -m "Descripción del cambio"

# Ver el historial de commits
git log --oneline

# Crear una nueva rama
git checkout -b nombre-de-la-rama

# Cambiar a una rama existente
git checkout nombre-de-la-rama

# Fusionar ramas
git merge nombre-de-la-rama
```

### Flujo de Trabajo Recomendado

1. **Crear una rama** para cada nueva funcionalidad
2. **Hacer commits** frecuentes con mensajes descriptivos
3. **Probar** los cambios antes de fusionar
4. **Fusionar** a la rama principal cuando esté listo
5. **Hacer push** al repositorio remoto regularmente

### Archivos Excluidos

El archivo `.gitignore` excluye automáticamente:
- Entornos virtuales (`inventario_env/`)
- Archivos de base de datos (`*.db`)
- Archivos de backup (`backups/`)
- Archivos temporales y de sistema
- Archivos de configuración local (`.env`)

## 📊 Estructura del Proyecto

```
inventario/
├── main.py              # Aplicación principal FastAPI
├── database.py          # Configuración de base de datos
├── models.py            # Modelos SQLAlchemy
├── schemas.py           # Esquemas Pydantic
├── requirements.txt     # Dependencias Python
├── inventario.db        # Base de datos SQLite (se crea automáticamente)
├── templates/           # Plantillas HTML
│   ├── base.html
│   ├── dashboard.html
│   ├── productos.html
│   ├── movimientos.html
│   └── kardex.html
└── static/
    └── style.css        # Estilos CSS
```

## 🎯 Funcionalidades Principales

### 1. Dashboard Principal
- Resumen de productos registrados
- Total de unidades en stock
- Movimientos recientes
- Accesos rápidos

### 2. Gestión de Productos
- Registro de nuevos productos
- Lista completa con stock actual
- Códigos únicos por producto
- Categorización por grupos

### 3. Control de Movimientos
- Entradas y salidas de inventario
- Filtros por producto y fechas
- Descripción detallada de cada movimiento
- Validaciones automáticas

### 4. Kardex de Productos
- Historial completo por producto
- Saldos progresivos
- Filtros por rango de fechas
- Visualización clara de entradas/salidas

## 🔧 Uso del Sistema

### Registrar un Producto
1. Ve a la sección "Productos"
2. Completa el formulario con código, nombre, unidad y grupo
3. Haz clic en "Guardar Producto"

### Registrar Movimientos
1. Ve a la sección "Movimientos"
2. Selecciona el producto
3. Elige tipo (Entrada/Salida)
4. Ingresa cantidad y descripción
5. Confirma la fecha y guarda

### Consultar Kardex
1. Desde "Productos" o "Movimientos", haz clic en "Ver Kardex"
2. Usa los filtros de fecha si necesitas un período específico
3. Revisa el historial completo con saldos

## 🎨 Diseño y UX

- **Responsive Design**: Funciona en desktop, tablet y móvil
- **Colores Modernos**: Gradientes y paleta profesional
- **Iconos Descriptivos**: Emojis para mejor usabilidad
- **Navegación Intuitiva**: Menú claro y accesos rápidos
- **Feedback Visual**: Estados de carga, confirmaciones y validaciones

## 🔒 Consideraciones de Seguridad

- Validación de datos en frontend y backend
- Códigos únicos para productos
- Prevención de movimientos negativos no válidos
- Sanitización de inputs

## 📈 Posibles Mejoras Futuras

- [ ] Autenticación y roles de usuario
- [ ] Reportes en PDF/Excel
- [ ] Códigos de barras/QR
- [ ] Alertas de stock mínimo
- [ ] API REST completa
- [ ] Integración con sistemas externos
- [ ] Backup automático
- [ ] Auditoría de cambios

## 🤝 Contribuir

Este es un proyecto base que puedes expandir según tus necesidades:

1. Fork el proyecto
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

## 📄 Licencia

Proyecto de código abierto para uso educativo y comercial.

---

**¿Necesitas ayuda?** Revisa la documentación o contacta al desarrollador.

¡Disfruta gestionando tu inventario de manera moderna y eficiente! 🚀
