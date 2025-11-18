# APIs de OSCE - Documentación Técnica

## Estado Actual de las APIs

### ✅ API Funcionando

**Endpoint**: `https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{ruc}`

**Datos Disponibles**:
- RUC
- Razón Social
- Estado (ACTIVO/INACTIVO)
- Condición (HABIDO/NO HABIDO)
- Tipo de Contribuyente
- Teléfonos
- Emails

**Ejemplo de Respuesta**:
```json
{
  "proveedorT01": {
    "numRuc": "20508238143",
    "nomRzsProv": "QUANTUM ANDES S.A.C.",
    "esHabilitado": true,
    "esAptoContratar": true,
    "emails": ["lferreyra@quantumamerica.com"],
    "telefonos": ["(01)2240630-98985055"],
    "tipoPersoneria": 2
  }
}
```

### ❌ APIs NO Disponibles Públicamente

#### 1. Socios y Accionistas
- **Endpoint probado**: `https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/sociedades/{ruc}`
- **Estado**: 404 Not Found
- **Alternativas**:
  - Web scraping del portal OSCE
  - API de SUNAT (requiere credenciales)
  - Portal de transparencia de SUNAT

#### 2. Representantes Legales
- **Endpoint probado**: `https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/representantes/{ruc}`
- **Estado**: 404 Not Found
- **Nota**: Estos datos vienen de SUNARP/SUNAT

#### 3. Órganos de Administración
- **Endpoint probado**: `https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/organos-administracion/{ruc}`
- **Estado**: 404 Not Found
- **Nota**: Estos datos vienen de SUNARP

#### 4. Experiencia/Contratos
- **Endpoint probado**: `https://eap.oece.gob.pe/expprov-bus/1.0/contratos/{ruc}`
- **Estado**: 404 Not Found
- **Alternativa**: Podría estar en otra versión de la API o requerir autenticación

#### 5. Domicilio Fiscal (Departamento/Provincia/Distrito)
- **Datos no incluidos en**: `/perfilprov-bus/1.0/ficha/{ruc}`
- **Origen**: SUNAT
- **Alternativa**: Web scraping de SUNAT o API privada

## Soluciones Propuestas

### Opción 1: Web Scraping (Implementación Inmediata)
Hacer scraping del portal oficial:
- URL: `https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/fichaProveedor/verProveedorCabecera.xhtml?ruc={ruc}`
- Requiere: BeautifulSoup4, requests/httpx
- Ventajas: Todos los datos disponibles
- Desventajas: Frágil ante cambios en el HTML

### Opción 2: API de SUNAT (Recomendado)
Integrar con:
- Consulta RUC SUNAT: `https://e-consultaruc.sunat.gob.pe/`
- SUNARP para datos societarios
- Ventajas: Datos oficiales y actualizados
- Desventajas: Puede requerir autenticación o captcha

### Opción 3: Base de Datos Local (Cache)
- Descargar datos periódicamente del portal OSCE
- Almacenar en PostgreSQL/MySQL
- Actualizar con cron jobs
- Ventajas: Rápido, confiable
- Desventajas: Requiere mantenimiento

### Opción 4: API Premium/Comercial
Servicios como:
- APISPERU
- Consultas SUNAT Premium
- Ventajas: Datos completos, soporte
- Desventajas: Costo mensual

## Implementación Recomendada

Para completar la funcionalidad actual, se recomienda:

1. **Corto Plazo**: Implementar web scraping del portal OSCE
   ```python
   # fup_consult/services/osce_scraper.py
   async def scrape_provider_full_data(ruc: str):
       url = f"https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/fichaProveedor/verProveedorCabecera.xhtml?ruc={ruc}"
       # Parse HTML and extract sociedades, representantes, etc.
   ```

2. **Mediano Plazo**: Integrar con API de SUNAT
   ```python
   # fup_consult/services/sunat_client.py
   async def get_sunat_data(ruc: str):
       # Consultar datos de SUNAT
   ```

3. **Largo Plazo**: Implementar cache/base de datos local

## Referencias

- Portal OSCE: https://prodapp2.seace.gob.pe/
- SUNAT Consulta RUC: https://e-consultaruc.sunat.gob.pe/
- Documentación API OSCE: No disponible públicamente

## Notas para el Desarrollador

- Las URLs con `eap.oece.gob.pe` son APIs internas de OSCE
- Los datos de socios/representantes NO están en la API pública simple
- El portal web de OSCE accede a APIs con autenticación o usa SSR
- Considerar rate limiting al hacer scraping
- Implementar retry logic y circuit breakers

---

**Autor**: Harold Alejandro Villanueva Borda
**Fecha**: 17 de Noviembre de 2025
**Versión**: 1.0
