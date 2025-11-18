# 🚀 Guía de Instalación y Despliegue

Este documento proporciona instrucciones detalladas para instalar y desplegar el sistema OSCE FUP Consultor.

## 📋 Tabla de Contenidos

- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación con Docker](#instalación-con-docker)
- [Instalación Local](#instalación-local)
- [Configuración](#configuración)
- [Despliegue en Producción](#despliegue-en-producción)
- [Troubleshooting](#troubleshooting)

## 💻 Requisitos del Sistema

### Para Docker (Recomendado)

- **Docker**: 20.10+ ([Instalar Docker](https://docs.docker.com/get-docker/))
- **Docker Compose**: 2.0+ (incluido con Docker Desktop)
- **Memoria RAM**: Mínimo 2GB disponible
- **Disco**: 1GB de espacio libre

### Para Instalación Local

- **Python**: 3.11 o superior
- **pip**: 23.0+
- **virtualenv**: Recomendado
- **Memoria RAM**: Mínimo 1GB disponible
- **Disco**: 500MB de espacio libre

## 🐳 Instalación con Docker

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor
```

### Paso 2: Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar si es necesario (valores por defecto funcionan)
nano .env  # o usar tu editor preferido
```

### Paso 3: Construir y Levantar Contenedores

```bash
# Construir imagen
docker-compose build

# Levantar servicios
docker-compose up

# O en background
docker-compose up -d
```

### Paso 4: Verificar Instalación

Abrir navegador en: `http://localhost:8000/`

Deberías ver la página de búsqueda de RUC.

### Comandos Útiles Docker

```bash
# Ver logs
docker-compose logs -f web

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar tests
docker-compose exec web pytest

# Entrar al contenedor
docker-compose exec web bash

# Detener servicios
docker-compose down

# Limpiar todo (incluyendo volúmenes)
docker-compose down -v
```

## 🔧 Instalación Local

### Paso 1: Clonar el Repositorio

```bash
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor
```

### Paso 2: Crear Entorno Virtual

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
venv\Scripts\activate
```

### Paso 3: Instalar Dependencias

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar configuración
# Windows: notepad .env
# Linux/Mac: nano .env
```

### Paso 5: Aplicar Migraciones

```bash
python manage.py migrate
```

### Paso 6: Ejecutar Servidor de Desarrollo

```bash
python manage.py runserver
```

### Paso 7: Verificar Instalación

Abrir navegador en: `http://localhost:8000/`

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1

# OSCE API Endpoints
OSCE_PERFILPROV_BASE=https://eap.oece.gob.pe/perfilprov-bus/1.0
OSCE_FUP_BASE=https://eap.oece.gob.pe/ficha-proveedor-cns/1.0
OSCE_EXPPROV_BASE=https://eap.oece.gob.pe/expprov-bus/1.0
OSCE_API_TIMEOUT=30

# Features (optional)
USE_SUNAT_SCRAPING=False
USE_OSCE_ANGULAR_SCRAPING=False
```

### Configuración Avanzada

Para modificar configuraciones adicionales, editar `osce_fup_portal/settings.py`:

```python
# Timeout de requests (en segundos)
OSCE_API_TIMEOUT = int(os.getenv("OSCE_API_TIMEOUT", "30"))

# Logging level
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'osce_fup_portal.log',
        },
    },
    # ...
}
```

## 🚀 Despliegue en Producción

### Checklist Pre-Despliegue

- [ ] `DEBUG=False` en `.env`
- [ ] `SECRET_KEY` único y seguro
- [ ] `ALLOWED_HOSTS` configurado correctamente
- [ ] Migraciones aplicadas
- [ ] Static files colectados
- [ ] Tests pasando al 100%
- [ ] HTTPS configurado
- [ ] Logs configurados

### Opción 1: Docker en Servidor

```bash
# En el servidor
git clone https://github.com/HarryLexvb/osce-fup-consultor.git
cd osce-fup-consultor

# Configurar .env para producción
cp .env.example .env
nano .env  # Ajustar DEBUG=False, SECRET_KEY, etc.

# Levantar con docker-compose
docker-compose up -d

# Verificar logs
docker-compose logs -f
```

### Opción 2: Deploy con Gunicorn + Nginx

1. **Instalar Gunicorn**

```bash
pip install gunicorn
```

2. **Crear archivo de servicio systemd**

`/etc/systemd/system/osce-fup.service`:

```ini
[Unit]
Description=OSCE FUP Consultor
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/osce-fup-consultor
Environment="PATH=/opt/osce-fup-consultor/venv/bin"
ExecStart=/opt/osce-fup-consultor/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/opt/osce-fup-consultor/osce_fup.sock \
          osce_fup_portal.wsgi:application

[Install]
WantedBy=multi-user.target
```

3. **Configurar Nginx**

`/etc/nginx/sites-available/osce-fup`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location /static/ {
        alias /opt/osce-fup-consultor/staticfiles/;
    }

    location /media/ {
        alias /opt/osce-fup-consultor/media/;
    }

    location / {
        proxy_pass http://unix:/opt/osce-fup-consultor/osce_fup.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

4. **Activar y iniciar servicios**

```bash
sudo systemctl enable osce-fup
sudo systemctl start osce-fup
sudo systemctl enable nginx
sudo systemctl restart nginx
```

### Opción 3: Deploy en Cloud (AWS/GCP/Azure)

Ver guías específicas en:
- [AWS Elastic Beanstalk](https://docs.aws.amazon.com/elasticbeanstalk/)
- [Google Cloud Run](https://cloud.google.com/run/docs)
- [Azure App Service](https://docs.microsoft.com/azure/app-service/)

## 🔍 Troubleshooting

### Error: "Port 8000 is already in use"

**Solución:**

```bash
# Encontrar proceso usando el puerto
lsof -i :8000  # Linux/Mac
netstat -ano | findstr :8000  # Windows

# Matar proceso
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# O cambiar puerto
python manage.py runserver 8080
```

### Error: "ModuleNotFoundError: No module named 'django'"

**Solución:**

```bash
# Verificar que el entorno virtual está activado
which python  # Debe apuntar al venv

# Reinstalar dependencias
pip install -r requirements.txt
```

### Error: "OSCE API timeout"

**Solución:**

1. Verificar conectividad a internet
2. Aumentar timeout en `.env`:

```env
OSCE_API_TIMEOUT=60
```

3. Verificar que la API de OSCE está disponible:

```bash
curl https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/ficha/20508238143/resumen
```

### Error: "Static files not found"

**Solución:**

```bash
# Colectar static files
python manage.py collectstatic --noinput

# Verificar configuración en settings.py
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
```

### Docker: "Cannot connect to the Docker daemon"

**Solución:**

```bash
# Iniciar Docker
sudo systemctl start docker  # Linux
# O abrir Docker Desktop  # Windows/Mac

# Verificar estado
docker ps
```

## 📚 Recursos Adicionales

- [Documentación Django](https://docs.djangoproject.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Gunicorn Documentation](https://docs.gunicorn.org/)
- [Nginx Documentation](https://nginx.org/en/docs/)

## 📞 Soporte

Si encuentras problemas no cubiertos aquí:

1. Revisa [Issues en GitHub](https://github.com/HarryLexvb/osce-fup-consultor/issues)
2. Abre un nuevo issue con detalles del error
3. Incluye logs relevantes y pasos para reproducir

---

**Última actualización**: Noviembre 2025
