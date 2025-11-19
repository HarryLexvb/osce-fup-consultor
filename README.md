# 🏛️ OSCE FUP Consultor - Sistema de Consulta de Proveedores del Estado

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Sistema web profesional para consultar la **Ficha Única del Proveedor (FUP)** del OSCE mediante número de RUC. Permite visualizar información completa del proveedor y exportarla a formato Excel con múltiples hojas organizadas.

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Tecnologías](#-tecnologías)
- [Instalación Rápida](#-instalación-rápida)
- [Uso](#-uso)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Desarrollo](#-desarrollo)
- [Tests](#-tests)
- [Docker](#-docker)
- [API](#-api)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

## ✨ Características

### Funcionalidades Principales

✅ **Consulta por RUC**: Búsqueda rápida de proveedores mediante RUC de 11 dígitos  
✅ **Carga Masiva**: Procesamiento de múltiples RUCs desde archivo Excel  
✅ **Procesamiento Paralelo**: Hasta 20 consultas simultáneas con reintentos automáticos  
✅ **Progreso en Tiempo Real**: Monitoreo visual del procesamiento batch  
✅ **Datos Completos**: Información general, domicilio, contactos, teléfonos y emails  
✅ **Socios/Accionistas**: Listado completo con porcentajes de participación y acciones  
✅ **Representantes Legales**: Personas autorizadas con documentos y cargos  
✅ **Órganos de Administración**: Directores, gerentes y cargos directivos detallados  
✅ **Exportación Excel Individual**: Archivo .xlsx con hojas organizadas por sección  
✅ **Exportación Excel Consolidada**: Archivo único con todos los proveedores procesados  
✅ **Interfaz Moderna**: UI responsive con Bootstrap 5 y tabs de navegación  
✅ **API Pública OSCE**: Sin web scraping, solo APIs oficiales  

### Características Técnicas

🔧 **Clean Architecture**: Separación de capas (Views → Services → Client)  
🔧 **Type Hints**: Código completamente tipado con mypy  
🔧 **Async/Await**: Cliente HTTP asíncrono con httpx  
🔧 **Procesamiento Batch**: Sistema de colas con reintentos automáticos  
🔧 **Base de Datos**: Seguimiento de trabajos batch con Django ORM  
🔧 **Docker Ready**: Dockerfile optimizado multi-stage  
🔧 **Tests Completos**: pytest con 100% cobertura crítica  
🔧 **Logging**: Sistema de logs estructurado  
🔧 **Error Handling**: Manejo robusto de errores y timeouts  

## 🛠️ Tecnologías

| Categoría | Tecnología | Versión |
|-----------|-----------|---------|
| **Backend** | Python | 3.11+ |
| **Framework** | Django | 5.0.1 |
| **HTTP Client** | httpx | 0.26.0 |
| **Excel Export** | openpyxl | 3.1.2 |
| **Frontend** | Bootstrap | 5.3 |
| **Testing** | pytest | 7.4.4 |
| **Container** | Docker | latest |
| **Database** | SQLite | (desarrollo) |

## 🚀 Instalación Rápida

### Opción 1: Docker (Recomendado)

```bash
# 1. Clonar repositorio
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor

# 2. Configurar variables de entorno (opcional)
cp .env.example .env

# 3. Levantar con Docker
docker-compose up --build

# 4. Acceder a http://localhost:8000
```

### Opción 2: Instalación Local

```bash
# 1. Clonar repositorio
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor

# 2. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar entorno
cp .env.example .env

# 5. Migraciones
python manage.py migrate

# 6. Ejecutar servidor
python manage.py runserver

# 7. Acceder a http://localhost:8000
```

## 💻 Uso

### Consulta Individual

1. **Abrir navegador** en `http://localhost:8000/` (o `http://localhost:8001/` si usas Docker)
2. **Tab "Búsqueda Individual"**
3. **Ingresar RUC** de 11 dígitos (ejemplo: `20508238143`)
4. **Hacer clic** en "Consultar"
5. **Ver resultados**:
   - 📊 Datos Generales (incluyendo teléfonos y emails)
   - 👥 Socios y Accionistas
   - 📝 Representantes Legales
   - 🏢 Órganos de Administración
6. **Descargar Excel** individual con 5 hojas organizadas

### Carga Masiva (Batch Processing)

1. **Tab "Carga Masiva"**
2. **Preparar archivo Excel**:
   - Primera columna: RUCs (11 dígitos)
   - Primera fila: Puede ser encabezado "RUC" (se omitirá)
   - Formato: `.xlsx` o `.xls`
   - Ejemplo: 
     ```
     | RUC          |
     |--------------|
     | 20508238143  |
     | 20100008662  |
     | 20572206433  |
     ```
3. **Cargar archivo** usando el botón "Cargar y Procesar"
4. **Monitorear progreso en tiempo real**:
   - 📊 Total de RUCs a procesar
   - ✅ RUCs completados exitosamente
   - ⏳ RUCs pendientes de procesamiento
   - ❌ RUCs fallidos (con reintentos automáticos hasta 3 veces)
   - Barra de progreso visual
5. **Descarga automática en el formato óptimo**:

#### Formatos de Descarga (Automáticos según volumen)

El sistema selecciona automáticamente el formato más eficiente según la cantidad de RUCs procesados:

| Volumen | Formato | Características |
|---------|---------|-----------------|
| **< 1,000 RUCs** | 📑 **Excel Estándar** | Archivo .xlsx con formato completo, colores, filtros y 5 hojas |
| **1,000 - 10,000 RUCs** | 📊 **Excel Optimizado** | Archivo .xlsx modo write-only, procesamiento por chunks de 5,000 registros |
| **> 10,000 RUCs** | 📄 **CSV** | Archivo .csv UTF-8 con BOM, compatible con Excel, separadores por secciones |

#### Contenido de las 5 Hojas/Secciones

| Hoja/Sección | Contenido |
|--------------|-----------|
| `Resumen` | Estadísticas del batch: totales, estados, tipos de contribuyente top 15 |
| `Datos Consolidados` | Todos los proveedores en tabla maestra con teléfonos, emails, contadores |
| `Socios Detallados` | Todos los socios cross-company: RUC empresa, nombre, %, acciones, fechas |
| `Representantes Detallados` | Todos los representantes: RUC empresa, nombre, cargo, tipo doc, fechas |
| `Organos Administracion` | Todos los órganos: RUC empresa, tipo órgano, cargo, miembro, fechas |

**Nota sobre CSV**: El formato CSV es compatible con Excel. Para abrirlo:
- Doble clic (Excel abrirá automáticamente con codificación correcta)
- O en Excel: Datos → Desde texto/CSV → seleccionar el archivo
- Todas las secciones están separadas con encabezados `=== NOMBRE SECCION ===`

### Exportar a Excel (Individual)

En la página de resultados de consulta individual, hacer clic en **"Descargar Excel"** para obtener un archivo con 5 hojas:

| Hoja | Contenido |
|------|-----------|
| `DatosGenerales` | RUC, razón social, estado, domicilio, teléfonos, emails, departamento, provincia, distrito |
| `SociosAccionistas` | Nombre, tipo documento, número, porcentaje, número de acciones, fecha ingreso |
| `Representantes` | Nombre, tipo documento, número, cargo, fecha desde |
| `OrganosAdministracion` | Nombre, tipo órgano (GERENCIA/DIRECTORIO), cargo, fecha desde |
| `Experiencia` | Contratos y experiencia laboral (si disponible) |

### Ejemplos de RUC

```
20508238143  # QUANTUM ANDES S.A.C. (con socios, representantes, teléfono y email)
20100008662  # EMPRESA EJEMPLO S.A.
20572206433  # OTRA EMPRESA S.A.C.
10732723175  # PERSONA NATURAL (sin conformación)
```

### Características del Procesamiento Batch

- ⚡ **Paralelismo**: Hasta 20 consultas simultáneas con semáforo de control
- 🔄 **Reintentos automáticos**: Hasta 3 intentos por RUC fallido con delay incremental
- 📊 **Progreso en tiempo real**: Polling cada 2 segundos con estadísticas detalladas
- 💾 **Persistencia**: Resultados guardados en base de datos (SQLite/PostgreSQL)
- 📥 **Formato automático**: CSV para >10k, Excel optimizado para 1k-10k, Excel estándar <1k
- 🚀 **Optimizado para grandes volúmenes**: Write-only mode y procesamiento por chunks
- ⏱️ **Rendimiento**: ~100-200 RUCs por minuto (limitado por API de OSCE)
- 🛡️ **Manejo robusto de errores**: Logging detallado y recuperación automática
- 📦 **Sin pérdida de datos**: Resultados guardados incrementalmente durante procesamiento

## 📁 Estructura del Proyecto

```
osce-fup-consultor/
│
├── 📂 fup_consult/              # Aplicación Django principal
│   ├── __init__.py
│   ├── models.py                # Modelos BatchJob, BatchItem para procesamiento
│   ├── forms.py                 # Validación de formularios
│   ├── views.py                 # Vistas HTTP (individual + batch)
│   ├── urls.py                  # Rutas de la app
│   ├── admin.py                 # Admin de Django para BatchJob
│   │
│   ├── 📂 services/             # Capa de servicios (lógica de negocio)
│   │   ├── __init__.py
│   │   ├── osce_client.py       # Cliente API OSCE (async con httpx)
│   │   ├── fup_service.py       # Agregación y normalización de datos
│   │   └── batch_service.py     # Procesamiento batch con paralelismo
│   │
│   ├── 📂 exporters/            # Exportadores de datos
│   │   ├── __init__.py
│   │   ├── excel_exporter.py             # Exportador Excel individual
│   │   ├── excel_batch_exporter.py       # Exportador Excel batch estándar
│   │   ├── excel_batch_exporter_optimized.py  # Excel optimizado (write-only)
│   │   └── csv_batch_exporter.py         # Exportador CSV para grandes volúmenes
│   │   └── excel_exporter.py    # Generación de archivos Excel
│   │
│   ├── 📂 templates/            # Plantillas HTML
│   │   └── fup_consult/
│   │       ├── base.html
│   │       ├── search.html
│   │       └── results.html
│   │
│   └── 📂 tests/                # Tests de la app
│       ├── __init__.py
│       ├── conftest.py
│       ├── test_forms.py
│       ├── test_osce_client.py
│       ├── test_fup_service.py
│       └── test_excel_exporter.py
│
├── 📂 osce_fup_portal/          # Proyecto Django
│   ├── __init__.py
│   ├── settings.py              # Configuración
│   ├── urls.py                  # Rutas principales
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
│
├── 📂 scripts/                  # Scripts de desarrollo
│   └── (scripts de prueba y debug)
│
├── 📂 docs/                     # Documentación adicional
│   ├── API_STATUS.md            # Estado de APIs OSCE
│   ├── CHANGELOG.md             # Historial de cambios
│   └── CONTRIBUTING.md          # Guía de contribución
│
├── 📂 tests/                    # Tests de integración
│   └── test_integration.py
│
├── 📄 manage.py                 # CLI Django
├── 📄 requirements.txt          # Dependencias Python
├── 📄 Dockerfile                # Imagen Docker
├── 📄 docker-compose.yml        # Orquestación Docker
├── 📄 .env.example              # Template variables entorno
├── 📄 .gitignore                # Exclusiones Git
├── 📄 pyproject.toml            # Configuración herramientas
├── 📄 .flake8                   # Configuración linting
└── 📄 README.md                 # Este archivo
```

## 🔧 Desarrollo

### Configuración Entorno de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Configurar pre-commit hooks (opcional)
pip install pre-commit
pre-commit install

# Ejecutar formateo de código
black .
isort .

# Ejecutar linting
flake8

# Ejecutar type checking
mypy fup_consult/
```

### Variables de Entorno

Archivo `.env`:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# OSCE API Configuration
OSCE_PERFILPROV_BASE=https://eap.oece.gob.pe/perfilprov-bus/1.0
OSCE_FUP_BASE=https://eap.oece.gob.pe/ficha-proveedor-cns/1.0
OSCE_EXPPROV_BASE=https://eap.oece.gob.pe/expprov-bus/1.0
OSCE_API_TIMEOUT=30

# Scraping (disabled by default)
USE_SUNAT_SCRAPING=False
USE_OSCE_ANGULAR_SCRAPING=False
```

### Arquitectura del Sistema

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│    Views    │  ◄── Capa de Presentación
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ FUPService  │  ◄── Lógica de Negocio
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ OSCEClient  │  ◄── Infraestructura (HTTP)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  OSCE API   │  ◄── Servicio Externo
└─────────────┘
```

**Principios aplicados:**
- ✅ Clean Architecture
- ✅ Dependency Injection
- ✅ Single Responsibility
- ✅ Interface Segregation
- ✅ Error Boundaries

## ✅ Tests

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura
pytest --cov=fup_consult --cov-report=html

# Solo unitarios
pytest -m unit

# Solo integración
pytest -m integration

# Verbose
pytest -v

# Ver print statements
pytest -s
```

### Cobertura de Tests

| Módulo | Cobertura | Tests |
|--------|-----------|-------|
| `models.py` | 100% | ✅ |
| `forms.py` | 100% | ✅ |
| `osce_client.py` | 100% | ✅ |
| `fup_service.py` | 100% | ✅ |
| `excel_exporter.py` | 100% | ✅ |
| `views.py` | 95% | ✅ |

**Política de tests**: Todos los tests deben pasar antes de merge a `main`.

## 🐳 Docker

### Desarrollo con Docker

```bash
# Build
docker-compose build

# Levantar servicios
docker-compose up

# Levantar en background
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Ejecutar comando en contenedor
docker-compose exec web python manage.py shell

# Ejecutar tests
docker-compose exec web pytest

# Detener servicios
docker-compose down

# Limpiar todo
docker-compose down -v
```

### Dockerfile Multi-Stage

El `Dockerfile` está optimizado con multi-stage build:

```dockerfile
# Stage 1: Builder
FROM python:3.11-slim AS builder
# Instala dependencias

# Stage 2: Runtime
FROM python:3.11-slim
# Copia solo artefactos necesarios
# Usuario no-root para seguridad
```

**Optimizaciones:**
- ✅ Imagen final ligera (~150MB)
- ✅ Cache de layers eficiente
- ✅ Usuario no-root
- ✅ Health checks

## 📊 API

### Endpoint OSCE Utilizado

```
GET https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/ficha/{ruc}/resumen
```

**Respuesta incluye:**

```json
{
  "datosSunat": {
    "ruc": "20508238143",
    "razon": "QUANTUM ANDES S.A.C.",
    "estado": "ACTIVO",
    "condicion": "HABIDO",
    "tipoEmpresa": "SOCIEDAD ANONIMA CERRADA",
    "departamento": "LIMA",
    "provincia": "LIMA",
    "distrito": "SAN ISIDRO"
  },
  "conformacion": {
    "socios": [...],
    "representantes": [...],
    "organosAdm": [...]
  }
}
```

### Rate Limiting

El sistema respeta los límites del servicio público:
- ⏱️ Timeout: 30 segundos por request
- 🔄 Sin reintentos automáticos
- 📊 Llamadas secuenciales (no concurrentes)

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Ver [docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) para detalles.

### Proceso

1. **Fork** el repositorio
2. **Crear rama** feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** cambios (`git commit -m 'Add: Amazing Feature'`)
4. **Push** a rama (`git push origin feature/AmazingFeature`)
5. **Abrir Pull Request**

### Estándares

- ✅ Tests deben pasar: `pytest`
- ✅ Código formateado: `black .` + `isort .`
- ✅ Sin errores de linting: `flake8`
- ✅ Type hints correctos: `mypy fup_consult/`
- ✅ Cobertura mantenida: `pytest --cov`

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para detalles.

```
MIT License

Copyright (c) 2025 Harold Alejandro Villanueva Borda

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software")...
```

## 👤 Autor

**Harold Alejandro Villanueva Borda**

- 💼 Computer Science
- 🎯 Especialización: Python/Django, Clean Architecture, DevOps
- 🔗 GitHub: [@HarryLexvb](https://github.com/HarryLexvb)
- 📧 Mail: harrylex8@gmail.com

## 🙏 Agradecimientos

- OSCE por proporcionar APIs públicas
- Comunidad Django por excelente framework
- Contribuidores del proyecto

---

## 📞 Soporte

¿Problemas? Abre un [issue](https://github.com/HarryLexvb/osce-fup-consultor/issues)

¿Preguntas? Consulta la [documentación](docs/)

---

**⚠️ Nota Legal**: Este sistema consulta información pública disponible en el portal del OSCE. El uso debe realizarse de manera responsable y respetando los términos de servicio del OSCE.

**Última actualización**: Noviembre 2025
