# 🚀 Quick Start Guide - OSCE FUP Consultor

Guía rápida para empezar a usar el proyecto en 5 minutos.

## ⚡ Inicio Rápido con Docker

### Requisitos

- Docker Desktop instalado y corriendo
- Git instalado

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor

# 2. Levantar con Docker (¡Eso es todo!)
docker-compose up --build

# 3. Abrir navegador
# http://localhost:8001
```

**¡Listo!** La aplicación está corriendo.

---

## 💻 Inicio Rápido Local (Sin Docker)

### Requisitos

- Python 3.11+
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar entorno (opcional)
cp .env.example .env

# 6. Migraciones
python manage.py migrate

# 7. Ejecutar servidor
python manage.py runserver

# 8. Abrir navegador
# http://localhost:8000
```

---

## 🎯 Primer Uso

### Modo 1: Consulta Individual

1. Ir a la página principal
2. Tab **"Búsqueda Individual"**
3. Ingresar un RUC de 11 dígitos
   - Ejemplo: `20508238143` (QUANTUM ANDES S.A.C.)
4. Click en **"Consultar"**
5. Ver información completa del proveedor
6. (Opcional) Click en **"Descargar Excel"** para exportar

### Modo 2: Carga Masiva

1. Ir a la página principal
2. Tab **"Carga Masiva"**
3. Preparar un archivo Excel (.xlsx) con RUCs:
   ```
   | RUC          |
   |--------------|
   | 20508238143  |
   | 20100008662  |
   | 20572206433  |
   ```
4. Click en **"Cargar y Procesar"**
5. Monitorear progreso en tiempo real:
   - 📊 Total de RUCs
   - ✅ Completados
   - ⏳ Pendientes
   - ❌ Fallidos (con reintentos automáticos hasta 3 veces)
   - Barra de progreso visual
6. Al finalizar, el sistema muestra:
   - 📄 **Formato automático**: CSV (>10k RUCs), Excel Optimizado (1k-10k), o Excel Estándar (<1k)
   - 📥 **Botón de descarga** con el formato detectado
7. Click en **"Descargar [Formato]"** para obtener archivo consolidado

**Formatos de descarga:**
- **CSV**: Para grandes volúmenes (>10,000 RUCs). Compatible con Excel, UTF-8 con BOM
- **Excel Optimizado**: Para volúmenes medios (1,000-10,000 RUCs). Modo write-only, procesamiento por chunks
- **Excel Estándar**: Para volúmenes pequeños (<1,000 RUCs). Con formato completo, colores y filtros

**Nota**: El archivo siempre incluye 5 hojas/secciones:
1. Resumen (estadísticas)
2. Datos Consolidados (tabla maestra)
3. Socios Detallados
4. Representantes Detallados
5. Órganos de Administración

### 2. Ver Resultados

#### Consulta Individual


Verás:
- 📊 **Datos Generales**: RUC, razón social, estado, domicilio
- 👥 **Socios**: Con porcentajes de participación
- 📝 **Representantes**: Con documentos
- 🏢 **Órganos**: Cargos directivos

### 3. Descargar Excel

Click en **"Descargar Excel"** para obtener archivo `.xlsx` con todas las secciones.

---

## 🧪 Verificar Instalación

### Ejecutar Tests

```bash
# Con Docker
docker-compose exec web pytest

# Sin Docker (con venv activado)
pytest
```

**Resultado esperado**: Todos los tests deben pasar ✅

---

## 🔧 Comandos Útiles

### Docker

```bash
# Ver logs en vivo
docker-compose logs -f web

# Detener
docker-compose down

# Reiniciar
docker-compose restart

# Limpiar todo
docker-compose down -v
```

### Local

```bash
# Crear superusuario (admin)
python manage.py createsuperuser

# Shell interactivo
python manage.py shell

# Verificar código
black .
flake8
mypy fup_consult/
```

---

## 🐛 Troubleshooting Común

### "Port 8000 already in use"

**Solución Docker:**
Cambiar puerto en `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Usar 8001 en lugar de 8000
```

**Solución Local:**
```bash
python manage.py runserver 8001
```

### "Module not found"

**Solución:**
```bash
# Verificar que venv está activado
which python  # Debe apuntar a venv

# Reinstalar dependencias
pip install -r requirements.txt
```

### "OSCE API timeout"

**Solución:**
1. Verificar conexión a internet
2. Aumentar timeout en `.env`:
```env
OSCE_API_TIMEOUT=60
```

---

## 📚 Próximos Pasos

1. **Ver documentación completa**: [README.md](README.md)
2. **Entender la arquitectura**: [docs/PROJECT_STRUCTURE.md](docs/PROJECT_STRUCTURE.md)
3. **Contribuir**: [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md)
4. **Instalación avanzada**: [docs/INSTALLATION.md](docs/INSTALLATION.md)

---

## ❓ ¿Necesitas Ayuda?

- 📖 **Documentación**: Ver carpeta `docs/`
- 🐛 **Reportar bug**: [GitHub Issues](https://github.com/HarryLexvb/osce-fup-consultor/issues)
- 💬 **Preguntas**: Abrir un issue con la etiqueta `question`

---

## ⭐ ¿Te Gusta el Proyecto?

Dale una estrella ⭐ en [GitHub](https://github.com/HarryLexvb/osce-fup-consultor)!

---

**¡Feliz consulta de proveedores! 🎉**
