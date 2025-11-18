# OSCE FUP RUC Consultor

Sistema web para consultar la **Ficha Única del Proveedor (FUP)** del OSCE a través del número de RUC. Permite visualizar información completa del proveedor y exportarla a formato Excel.

## Descripción

La Ficha Única del Proveedor es un documento que consolida información relevante sobre los proveedores del Estado Peruano, incluyendo datos generales, conformación societaria, representantes legales, órganos de administración y experiencia en contrataciones públicas.

Este sistema permite:
- ✅ Consultar rápidamente la información de un proveedor mediante su RUC
- ✅ Visualizar datos estructurados en una interfaz web moderna
- ✅ Exportar toda la información a un archivo Excel con múltiples hojas organizadas
- ✅ Acceder a información actualizada desde las APIs públicas del OSCE

## Contexto

El proyecto consulta información pública disponible en el **Buscador de Proveedores del Estado** del OSCE (`https://apps.osce.gob.pe/perfilprov-ui/`), específicamente:

- **Datos generales**: RUC, razón social, estado SUNAT, condición, domicilio, contactos
- **Conformación societaria**: Socios y accionistas con porcentajes de participación
- **Representantes legales**: Personas autorizadas para representar a la empresa
- **Órganos de administración**: Directores, gerentes y otros cargos directivos
- **Experiencia**: Historial de contratos y órdenes con entidades del Estado

El sistema está diseñado respetando los términos de uso del servicio público y sin emplear técnicas que violen políticas anti-bot o restricciones de acceso.

## Arquitectura y Tecnologías

### Stack Tecnológico

- **Backend**: Python 3.11+ con Django 5.0
- **Cliente HTTP**: httpx (asíncrono)
- **Exportación Excel**: openpyxl
- **Frontend**: Bootstrap 5 + Bootstrap Icons
- **Contenerización**: Docker + docker-compose
- **Testing**: pytest + pytest-django
- **Calidad de código**: black, isort, flake8, mypy

### Arquitectura

El proyecto sigue principios de **Clean Architecture** y **SOLID**, con separación clara de responsabilidades:

```
fup_consult/
├── models.py              # Modelos de dominio (dataclasses)
├── forms.py               # Validación de entrada (RUC)
├── views.py               # Capa de presentación HTTP
├── services/
│   ├── osce_client.py     # Cliente de APIs OSCE (infraestructura)
│   └── fup_service.py     # Lógica de negocio (agregación y normalización)
├── exporters/
│   └── excel_exporter.py  # Generación de archivos Excel
├── templates/             # Plantillas HTML
└── tests/                 # Tests unitarios e integración
```

**Decisiones de diseño clave**:

1. **Separación de capas**: Views → Services → Client, cada una con responsabilidad única
2. **Type hints**: Todo el código está tipado para mejor mantenibilidad
3. **Manejo de errores robusto**: Timeouts, errores HTTP y códigos de respuesta API
4. **Logging estructurado**: Trazabilidad de operaciones y errores
5. **Tests exhaustivos**: Cobertura de casos exitosos, errores y edge cases

## Requisitos Previos

- **Docker** y **docker-compose** (recomendado)
- O alternativamente:
  - Python 3.11 o superior
  - pip y virtualenv

## Instalación y Configuración

### Opción 1: Usando Docker (Recomendado)

1. **Clonar el repositorio**

```bash
git clone https://github.com/HarryLexvb/osce-fup-ruc-consultor.git
cd osce-fup-ruc-consultor
```

2. **Configurar variables de entorno**

```bash
cp .env.example .env
```

Editar `.env` si es necesario (los valores por defecto funcionan correctamente).

3. **Construir y levantar los contenedores**

```bash
docker-compose up --build
```

4. **Acceder a la aplicación**

Abrir el navegador en: `http://localhost:8000/`

### Opción 2: Instalación Local

1. **Clonar el repositorio**

```bash
git clone https://github.com/HarryLexvb/osce-fup-ruc-consultor.git
cd osce-fup-ruc-consultor
```

2. **Crear entorno virtual**

```bash
python -m venv venv
```

Activar el entorno:
- Windows: `venv\Scripts\activate`
- Linux/Mac: `source venv/bin/activate`

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**

```bash
cp .env.example .env
```

5. **Aplicar migraciones**

```bash
python manage.py migrate
```

6. **Ejecutar servidor de desarrollo**

```bash
python manage.py runserver
```

7. **Acceder a la aplicación**

Abrir el navegador en: `http://localhost:8000/`

## Uso

### Consulta de Proveedor

1. Ingrese un **RUC de 11 dígitos** en el formulario de búsqueda
2. Haga clic en **"Consultar"**
3. El sistema mostrará:
   - Datos generales del proveedor
   - Lista de socios y accionistas
   - Representantes legales
   - Órganos de administración
   - Resumen de experiencia contractual

### Descarga de Excel

En la página de resultados, haga clic en **"Descargar Excel"** para obtener un archivo `.xlsx` con todas las secciones organizadas en hojas separadas:

- `DatosGenerales`: Información básica del proveedor
- `SociosAccionistas`: Listado de socios con participación
- `Representantes`: Representantes legales
- `OrganosAdministracion`: Directores y gerentes
- `Experiencia`: Contratos y órdenes del proveedor

**Ejemplo de RUC para prueba**: `20508238143` (sustituir por un RUC real del registro SUNAT)

## Ejecución de Tests

El proyecto incluye una suite completa de tests unitarios e integración.

### Ejecutar todos los tests

**Con Docker:**

```bash
docker-compose run web pytest
```

**Local:**

```bash
pytest
```

### Ejecutar tests con cobertura

```bash
pytest --cov=fup_consult --cov-report=html
```

Esto generará un reporte de cobertura en `htmlcov/index.html`.

### Ejecutar solo tests unitarios

```bash
pytest -m unit
```

### Ejecutar solo tests de integración

```bash
pytest -m integration
```

### Política de calidad

**⚠️ IMPORTANTE**: No se debe desplegar código o hacer merge a producción si los tests no pasan al 100%. Todos los tests deben ejecutarse exitosamente antes de cualquier release.

## Herramientas de Calidad

### Formateo de código

```bash
# Formatear código automáticamente
black .
isort .
```

### Linting

```bash
# Verificar calidad de código
flake8
```

### Type checking

```bash
# Verificar tipos estáticos
mypy fup_consult/
```

## Buenas Prácticas Implementadas

### 1. Manejo de Errores

- **Timeouts**: Configurables para evitar bloqueos indefinidos
- **Reintentos**: Lógica de retry para APIs transitorias
- **Mensajes amigables**: El usuario nunca ve stack traces, solo mensajes informativos
- **Logging**: Todos los errores se registran para debugging

### 2. Respeto a APIs Públicas

- **Rate limiting**: Llamadas secuenciales para no saturar servicios
- **Timeouts razonables**: 30 segundos por defecto
- **Manejo de respuestas vacías**: El sistema continúa funcionando si alguna sección falla
- **No bypass de seguridad**: No se intenta evitar reCAPTCHA ni controles similares

### 3. Seguridad

- **Variables de entorno**: Credenciales y configuración fuera del código
- **Usuario no-root en Docker**: Contenedor ejecuta con usuario limitado
- **Validación de entrada**: Formularios con validación estricta
- **CSRF protection**: Habilitado en todos los formularios

### 4. Mantenibilidad

- **Type hints**: Todo el código público está tipado
- **Docstrings**: Funciones documentadas con descripción, args y returns
- **Tests exhaustivos**: Cobertura de casos normales, errores y edge cases
- **Código limpio**: Siguiendo PEP 8 y principios SOLID

## Estructura del Proyecto

```
osce-fup-ruc-consultor/
├── docker-compose.yml           # Orquestación de contenedores
├── Dockerfile                   # Imagen Docker optimizada
├── requirements.txt             # Dependencias Python
├── pyproject.toml              # Configuración herramientas (black, pytest, mypy)
├── .flake8                     # Configuración linting
├── .env.example                # Plantilla variables de entorno
├── .gitignore                  # Archivos excluidos de Git
├── LICENSE                     # Licencia MIT
├── README.md                   # Este archivo
├── manage.py                   # CLI Django
├── osce_fup_portal/            # Proyecto Django principal
│   ├── settings.py             # Configuración Django
│   ├── urls.py                 # Rutas principales
│   └── wsgi.py                 # WSGI application
└── fup_consult/                # Aplicación principal
    ├── models.py               # Modelos de dominio
    ├── forms.py                # Formularios y validación
    ├── views.py                # Vistas HTTP
    ├── urls.py                 # Rutas de la app
    ├── services/               # Capa de servicios
    │   ├── osce_client.py      # Cliente APIs OSCE
    │   └── fup_service.py      # Lógica de negocio
    ├── exporters/              # Exportadores
    │   └── excel_exporter.py   # Generación Excel
    ├── templates/              # Plantillas HTML
    │   └── fup_consult/
    │       ├── base.html
    │       ├── search.html
    │       ├── results.html
    │       └── error.html
    └── tests/                  # Tests
        ├── conftest.py         # Fixtures pytest
        ├── test_forms.py
        ├── test_osce_client.py
        ├── test_fup_service.py
        ├── test_excel_exporter.py
        └── test_integration.py
```

## Roadmap y Mejoras Futuras

- [ ] Cache de consultas frecuentes con Redis
- [ ] API REST para integración con otros sistemas
- [ ] Descarga en formato PDF además de Excel
- [ ] Comparación de múltiples proveedores
- [ ] Alertas de cambios en proveedores favoritos
- [ ] Dashboard administrativo con estadísticas

## Troubleshooting

### Error: "En este momento no se puede obtener la información desde OSCE"

**Causa**: APIs de OSCE no disponibles o timeout.

**Solución**: Verificar conectividad, aumentar timeout en `.env`:

```
OSCE_API_TIMEOUT=60
```

### Tests fallan con "Connection Error"

**Causa**: Tests de integración necesitan mocking de httpx.

**Solución**: Asegurar que `pytest-httpx` está instalado y los mocks configurados.

### Docker no inicia correctamente

**Solución**:

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up
```

## Licencia

Este proyecto está licenciado bajo la Licencia MIT. Ver archivo [LICENSE](LICENSE) para más detalles.

## Autor

**Harold Alejandro Villanueva Borda**

Ingeniero de Software especializado en desarrollo full-stack con Python/Django, arquitectura de software y DevOps. Este proyecto demuestra la aplicación de principios de ingeniería de software de calidad empresarial, incluyendo Clean Architecture, TDD, contenerización y automatización de calidad de código.

---

**Nota**: Este sistema consulta información pública disponible en el portal del OSCE. El uso de esta herramienta debe realizarse de manera responsable y respetando los términos de servicio del OSCE.
