# 📂 Estructura del Proyecto OSCE FUP Consultor

Este documento describe la organización completa del proyecto.

## 🗂️ Estructura de Directorios

```
osce-fup-consultor/
│
├── 📂 fup_consult/                     # Aplicación Django principal
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py                        # Formularios de validación de RUC
│   ├── models.py                       # Modelos de dominio (dataclasses)
│   ├── urls.py                         # Rutas de la aplicación
│   ├── views.py                        # Controladores HTTP
│   │
│   ├── 📂 services/                    # Capa de servicios (lógica de negocio)
│   │   ├── __init__.py
│   │   ├── osce_client.py              # Cliente HTTP para API OSCE
│   │   ├── fup_service.py              # Agregación y normalización de datos
│   │   ├── sunat_scraper.py            # [Legacy] Scraper SUNAT (deshabilitado)
│   │   ├── osce_angular_scraper.py     # [Legacy] Scraper Angular (deshabilitado)
│   │   └── osce_camoufox_scraper.py    # [Legacy] Scraper Camoufox (deshabilitado)
│   │
│   ├── 📂 exporters/                   # Exportadores de datos
│   │   ├── __init__.py
│   │   └── excel_exporter.py           # Generación de archivos Excel (.xlsx)
│   │
│   ├── 📂 templates/                   # Plantillas HTML
│   │   └── fup_consult/
│   │       ├── base.html               # Plantilla base con Bootstrap
│   │       ├── search.html             # Formulario de búsqueda
│   │       ├── results.html            # Página de resultados
│   │       └── error.html              # Página de error
│   │
│   ├── 📂 static/                      # Archivos estáticos
│   │   └── fup_consult/
│   │       ├── css/
│   │       ├── js/
│   │       └── images/
│   │
│   └── 📂 tests/                       # Tests de la aplicación
│       ├── __init__.py
│       ├── conftest.py                 # Fixtures y configuración pytest
│       ├── test_forms.py               # Tests de formularios
│       ├── test_osce_client.py         # Tests del cliente OSCE
│       ├── test_fup_service.py         # Tests del servicio FUP
│       ├── test_excel_exporter.py      # Tests del exportador Excel
│       └── test_views.py               # Tests de vistas
│
├── 📂 osce_fup_portal/                 # Proyecto Django
│   ├── __init__.py
│   ├── asgi.py                         # Configuración ASGI
│   ├── settings.py                     # Configuración del proyecto
│   ├── urls.py                         # Rutas principales
│   └── wsgi.py                         # Configuración WSGI
│
├── 📂 scripts/                         # Scripts de desarrollo y testing
│   ├── test_*.py                       # Scripts de prueba individuales
│   ├── scrape_*.py                     # Scripts de scraping (research)
│   ├── debug_*.py                      # Scripts de debugging
│   └── find_*.py                       # Scripts de investigación de APIs
│
├── 📂 docs/                            # Documentación del proyecto
│   ├── API_STATUS.md                   # Estado de APIs OSCE investigadas
│   ├── CHANGELOG.md                    # Historial de cambios
│   ├── CONTRIBUTING.md                 # Guía de contribución
│   ├── INSTALLATION.md                 # Guía de instalación detallada
│   └── PROJECT_STRUCTURE.md            # Este archivo
│
├── 📂 tests/                           # Tests de integración
│   └── test_integration.py             # Tests end-to-end
│
├── 📂 temp/                            # Archivos temporales (ignorados por git)
│   ├── *.html                          # Páginas capturadas para debugging
│   ├── *.json                          # Respuestas API guardadas
│   ├── *.txt                           # Logs y debug output
│   └── *.png                           # Screenshots de prueba
│
├── 📂 staticfiles/                     # Static files colectados (producción)
│   └── (generado por collectstatic)
│
├── 📂 media/                           # Archivos de usuario
│   └── (uploads, si los hubiera)
│
├── 📄 manage.py                        # CLI de Django
├── 📄 requirements.txt                 # Dependencias Python
├── 📄 Dockerfile                       # Imagen Docker
├── 📄 docker-compose.yml               # Orquestación Docker
├── 📄 .env                             # Variables de entorno (no en git)
├── 📄 .env.example                     # Template de variables de entorno
├── 📄 .gitignore                       # Archivos ignorados por git
├── 📄 pyproject.toml                   # Configuración de herramientas Python
├── 📄 .flake8                          # Configuración de linting
├── 📄 setup.sh                         # Script de setup para Linux/Mac
├── 📄 setup.bat                        # Script de setup para Windows
├── 📄 LICENSE                          # Licencia MIT
├── 📄 README.md                        # Documentación principal
└── 📄 Makefile                         # Comandos make (opcional)
```

## 📝 Descripción de Componentes

### Aplicación Principal (`fup_consult/`)

#### Modelos de Dominio (`models.py`)

Dataclasses que representan las entidades del dominio:

- `GeneralData`: Información general del proveedor
- `Socio`: Socios y accionistas
- `Representante`: Representantes legales
- `OrganoAdministracion`: Órganos de administración
- `ContratoExperiencia`: Historial de contratos
- `ProviderData`: Agregación completa de datos

#### Formularios (`forms.py`)

- `RUCSearchForm`: Validación de RUC (11 dígitos, solo números)

#### Vistas (`views.py`)

- `search_view`: Página de búsqueda
- `results_view`: Página de resultados
- `download_excel_view`: Descarga de archivo Excel

### Servicios (`fup_consult/services/`)

#### Cliente OSCE (`osce_client.py`)

Cliente HTTP asíncrono que consume la API pública de OSCE:

- Endpoint principal: `/ficha/{ruc}/resumen`
- Manejo de errores y timeouts
- Logging de requests
- Type hints completos

#### Servicio FUP (`fup_service.py`)

Capa de lógica de negocio que:

- Orquesta llamadas al cliente OSCE
- Normaliza datos de API a modelos de dominio
- Maneja errores gracefully
- Proporciona interfaz simplificada a las vistas

### Exportadores (`fup_consult/exporters/`)

#### Exportador Excel (`excel_exporter.py`)

Genera archivos .xlsx con múltiples hojas:

1. **DatosGenerales**: Info básica del proveedor
2. **SociosAccionistas**: Listado de socios
3. **Representantes**: Representantes legales
4. **OrganosAdministracion**: Cargos directivos

### Templates (`fup_consult/templates/`)

Plantillas HTML con Bootstrap 5:

- **base.html**: Layout base con navbar y footer
- **search.html**: Formulario de búsqueda con validación
- **results.html**: Visualización de datos en cards y tablas
- **error.html**: Página amigable de errores

### Tests (`fup_consult/tests/`)

Suite completa de tests con pytest:

- **Unitarios**: Modelos, formularios, servicios
- **Integración**: Cliente OSCE, exportador Excel
- **Cobertura**: >95% en componentes críticos

## 🔧 Configuración

### Variables de Entorno (`.env`)

```env
# Django
DJANGO_SECRET_KEY=xxx
DJANGO_DEBUG=True/False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# OSCE API
OSCE_FUP_BASE=https://eap.oece.gob.pe/ficha-proveedor-cns/1.0
OSCE_API_TIMEOUT=30

# Features
USE_SUNAT_SCRAPING=False
USE_OSCE_ANGULAR_SCRAPING=False
```

### Archivos de Configuración

- **pyproject.toml**: black, isort, pytest, mypy
- **.flake8**: Reglas de linting
- **requirements.txt**: Dependencias Python
- **docker-compose.yml**: Orquestación de contenedores

## 📊 Arquitectura

### Clean Architecture

```
Views (HTTP) → Services (Business Logic) → Client (Infrastructure) → API (External)
```

### Principios SOLID

- ✅ **Single Responsibility**: Cada clase una responsabilidad
- ✅ **Open/Closed**: Abierto a extensión, cerrado a modificación
- ✅ **Liskov Substitution**: Interfaces intercambiables
- ✅ **Interface Segregation**: Interfaces específicas
- ✅ **Dependency Inversion**: Dependencias de abstracciones

## 🧪 Testing

### Estrategia de Tests

```
tests/
├── unit/           # Tests aislados de componentes
├── integration/    # Tests de interacción entre componentes
└── e2e/            # Tests end-to-end del flujo completo
```

### Comandos

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=fup_consult

# Solo unitarios
pytest -m unit

# Solo integración
pytest -m integration
```

## 🐳 Docker

### Arquitectura Docker

- **Imagen base**: python:3.11-slim
- **Multi-stage build**: No (imagen única optimizada)
- **Usuario**: appuser (no-root)
- **Volumes**: staticfiles, media

### Comandos Docker

```bash
# Build
docker-compose build

# Run
docker-compose up

# Logs
docker-compose logs -f web

# Shell
docker-compose exec web bash

# Tests
docker-compose exec web pytest
```

## 📈 Flujo de Datos

```
1. Usuario ingresa RUC en formulario
   ↓
2. Vista valida formulario
   ↓
3. Servicio FUP consulta cliente OSCE
   ↓
4. Cliente hace request HTTP a API OSCE
   ↓
5. API responde con JSON
   ↓
6. Cliente parsea respuesta
   ↓
7. Servicio normaliza a modelos de dominio
   ↓
8. Vista renderiza template con datos
   ↓
9. Usuario ve resultados o descarga Excel
```

## 🔐 Seguridad

- ✅ Variables sensibles en `.env`
- ✅ Usuario no-root en Docker
- ✅ CSRF protection habilitado
- ✅ Validación de entrada (formularios)
- ✅ Sanitización de salida (templates)
- ✅ HTTPS en producción (recomendado)

## 📚 Recursos

- [Django Documentation](https://docs.djangoproject.com/)
- [httpx Documentation](https://www.python-httpx.org/)
- [pytest Documentation](https://docs.pytest.org/)
- [Docker Documentation](https://docs.docker.com/)

---

**Última actualización**: Noviembre 2025
