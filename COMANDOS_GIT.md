# Guía de Comandos Git - Sistema de Inventario Satelital

## 🔗 Conectar repositorio local con GitHub

### Configurar repositorio remoto
```bash
# Agregar repositorio remoto
git remote add origin https://github.com/tu-usuario/nombre-del-repositorio.git

# Verificar repositorios remotos
git remote -v

# Subir código por primera vez
git push -u origin master
```

## 📋 Flujo de trabajo básico

### 1. Verificar estado
```bash
git status
```

### 2. Agregar archivos al staging
```bash
# Agregar archivo específico
git add nombre-del-archivo.py

# Agregar todos los archivos modificados
git add .

# Agregar archivos por tipo
git add *.py
```

### 3. Hacer commit
```bash
git commit -m "Descripción clara del cambio realizado"
```

### 4. Subir cambios
```bash
# Primera vez
git push -u origin master

# Subsecuentes veces
git push
```

## 🌿 Trabajo con ramas

### Crear y cambiar ramas
```bash
# Crear y cambiar a nueva rama
git checkout -b nombre-de-la-rama
git switch -c nombre-de-la-rama  # Comando moderno

# Cambiar a rama existente
git checkout nombre-de-la-rama
git switch nombre-de-la-rama  # Comando moderno
```

### Ver ramas
```bash
# Ver ramas locales
git branch

# Ver todas las ramas (locales y remotas)
git branch -a

# Ver rama actual
git branch --show-current
```

### Fusionar ramas
```bash
# Cambiar a rama principal
git checkout master

# Fusionar rama de desarrollo
git merge nombre-de-la-rama
```

### Eliminar ramas
```bash
# Eliminar rama local
git branch -d nombre-de-la-rama

# Eliminar rama remota
git push origin --delete nombre-de-la-rama
```

## 🔍 Comandos de consulta

### Ver historial
```bash
# Ver últimos commits
git log --oneline -5

# Ver historial completo
git log --oneline
```

### Ver diferencias
```bash
# Ver diferencias antes del commit
git diff

# Ver diferencias entre ramas
git diff master..nombre-de-rama

# Ver commits únicos de una rama
git log master..nombre-de-rama
```

## ⚠️ Comandos de emergencia

### Deshacer cambios
```bash
# Deshacer cambios en archivo específico (antes del commit)
git checkout -- nombre-del-archivo.py

# Deshacer todos los cambios (antes del commit)
git checkout -- .

# Deshacer último commit (manteniendo cambios)
git reset --soft HEAD~1
```

### Renombrar rama
```bash
# Renombrar rama actual
git branch -m nuevo-nombre
```

## 📝 Convenciones de nombres para ramas

- `feature/nombre-funcionalidad` - Para nuevas características
- `bugfix/descripcion-error` - Para corrección de errores
- `hotfix/descripcion-urgente` - Para correcciones urgentes
- `release/version-x.x.x` - Para preparar releases

## 💡 Ejemplos de mensajes de commit

### Formato recomendado
```
tipo: Descripción breve del cambio
```

### Tipos comunes
- `feat:` - Nueva funcionalidad
- `fix:` - Corrección de error
- `docs:` - Cambios en documentación
- `style:` - Cambios de formato (espacios, comas, etc.)
- `refactor:` - Refactorización de código
- `test:` - Agregar o modificar tests
- `chore:` - Cambios en herramientas, configuración, etc.

### Ejemplos
```bash
git commit -m "feat: Agregar funcionalidad de exportar a Excel"
git commit -m "fix: Corregir error en cálculo de inventario"
git commit -m "docs: Actualizar documentación del API"
git commit -m "style: Mejorar formato del código"
git commit -m "refactor: Optimizar consultas de base de datos"
```

## 🚀 Flujo completo de ejemplo

### Para nueva funcionalidad
```bash
# 1. Actualizar master
git checkout master
git pull origin master

# 2. Crear rama para la funcionalidad
git checkout -b feature/nueva-funcionalidad

# 3. Trabajar y hacer commits
git add .
git commit -m "feat: Implementar nueva funcionalidad"

# 4. Subir rama
git push -u origin feature/nueva-funcionalidad

# 5. Fusionar con master
git checkout master
git merge feature/nueva-funcionalidad
git push origin master

# 6. Limpiar (opcional)
git branch -d feature/nueva-funcionalidad
```

## 📋 Checklist de buenas prácticas

- [ ] Hacer `git status` antes de cada commit
- [ ] Usar mensajes de commit descriptivos
- [ ] Hacer commits frecuentes y pequeños
- [ ] Hacer push regularmente
- [ ] Usar ramas para nuevas funcionalidades
- [ ] Revisar cambios antes de fusionar
- [ ] Mantener master estable

## 🔧 Comandos útiles adicionales

```bash
# Ver configuración de Git
git config --list

# Configurar usuario (si no está configurado)
git config --global user.name "Tu Nombre"
git config --global user.email "tu-email@ejemplo.com"

# Ver archivos ignorados
git status --ignored

# Ver cambios en archivo específico
git diff archivo.py
```

---
*Archivo creado para el proyecto Sistema de Inventario Satelital*
*Última actualización: $(date)*
