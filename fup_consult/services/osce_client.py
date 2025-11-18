"""
OSCE API client for fetching provider information.

This module provides a client to interact with OSCE's public APIs for retrieving
provider information including general data, shareholders, representatives, and
contract experience.
"""

import logging
from typing import Any, Dict, Optional

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


class OSCEAPIException(Exception):
    """Exception raised when OSCE API returns an error."""

    pass


class OSCEClient:
    """Client for interacting with OSCE APIs."""

    def __init__(
        self,
        perfilprov_base: Optional[str] = None,
        fup_base: Optional[str] = None,
        expprov_base: Optional[str] = None,
        timeout: Optional[int] = None,
    ) -> None:
        """
        Initialize OSCE API client.

        Args:
            perfilprov_base: Base URL for perfilprov-bus service
            fup_base: Base URL for ficha-proveedor-cns service
            expprov_base: Base URL for expprov-bus service
            timeout: Request timeout in seconds
        """
        self.perfilprov_base = perfilprov_base or settings.OSCE_PERFILPROV_BASE
        self.fup_base = fup_base or settings.OSCE_FUP_BASE
        self.expprov_base = expprov_base or settings.OSCE_EXPPROV_BASE
        self.timeout = timeout or settings.OSCE_API_TIMEOUT

    async def _make_request(self, url: str) -> Dict[str, Any]:
        """
        Make HTTP request to OSCE API.

        Args:
            url: Full URL to request

        Returns:
            JSON response as dictionary

        Raises:
            OSCEAPIException: If request fails or API returns error
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Making request to: {url}")
                response = await client.get(url)
                response.raise_for_status()

                data = response.json()

                # Check if API returned an error code
                resultado = data.get("resultadoT01", {})
                codigo = resultado.get("codigo", "")
                mensaje = resultado.get("mensaje", "")

                if codigo != "00":
                    error_msg = f"API returned error code {codigo}: {mensaje}"
                    logger.error(error_msg)
                    raise OSCEAPIException(error_msg)

                return data

        except httpx.TimeoutException as e:
            error_msg = f"Request timeout: {str(e)}"
            logger.error(error_msg)
            raise OSCEAPIException(error_msg) from e

        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error {e.response.status_code}: {str(e)}"
            logger.error(error_msg)
            raise OSCEAPIException(error_msg) from e

        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            raise OSCEAPIException(error_msg) from e

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            raise OSCEAPIException(error_msg) from e

    async def get_provider_general_data(self, ruc: str) -> Dict[str, Any]:
        """
        Get complete provider data including conformacion from ficha-proveedor-cns/resumen.
        This endpoint includes:
        - datosSunat: Basic data (RUC, razon social, estado, domicilio, etc.)
        - conformacion: socios, representantes, organosAdm

        Args:
            ruc: Provider's RUC number

        Returns:
            Provider complete data dictionary with parsed structure

        Raises:
            OSCEAPIException: If request fails
        """
        url = f"{self.fup_base}/ficha/{ruc}/resumen"
        data = await self._make_request(url)
        
        # Parse and structure the response
        datos_sunat = data.get("datosSunat", {})
        conformacion = data.get("conformacion", {})
        
        if not datos_sunat:
            raise OSCEAPIException(f"No data found for RUC {ruc}")
        
        # Extract socios
        socios = []
        for socio in conformacion.get("socios", []):
            socios.append({
                "nombre_completo": socio.get("razonSocial", "").strip(),
                "tipo_documento": socio.get("siglaDocIde", ""),
                "numero_documento": socio.get("nroDocumento", ""),
                "porcentaje_participacion": socio.get("porcentajeAcciones")
            })
        
        # Extract representantes
        representantes = []
        for rep in conformacion.get("representantes", []):
            representantes.append({
                "nombre_completo": rep.get("razonSocial", "").strip(),
                "tipo_documento": rep.get("siglaDocIde", ""),
                "numero_documento": rep.get("nroDocumento", ""),
                "cargo": "REPRESENTANTE LEGAL"
            })
        
        # Extract organos
        organos = []
        for org in conformacion.get("organosAdm", []):
            organos.append({
                "nombre_completo": org.get("apellidosNomb", "").strip(),
                "tipo_documento": org.get("siglaDocIde", ""),
                "numero_documento": org.get("nroDocumento", ""),
                "cargo": org.get("descCargo", "")
            })
        
        # Build domicilio
        departamento = datos_sunat.get("departamento", "")
        provincia = datos_sunat.get("provincia", "")
        distrito = datos_sunat.get("distrito", "")
        domicilio = f"{distrito}, {provincia}, {departamento}" if distrito else ""
        
        return {
            "ruc": datos_sunat.get("ruc"),
            "razon_social": datos_sunat.get("razon"),
            "estado": datos_sunat.get("estado", ""),
            "condicion": datos_sunat.get("condicion", ""),
            "tipo_contribuyente": datos_sunat.get("tipoEmpresa", ""),
            "domicilio": domicilio,
            "telefonos": [],  # Not in this endpoint
            "emails": [],  # Not in this endpoint
            "socios": socios,
            "representantes": representantes,
            "organos": organos
        }

    async def get_sociedades(self, ruc: str) -> Dict[str, Any]:
        """
        Get shareholders/partners data.
        Note: This endpoint currently returns 404. Data needs to be obtained from another source.

        Args:
            ruc: Provider's RUC number

        Returns:
            Shareholders data dictionary

        Raises:
            OSCEAPIException: If request fails
        """
        # TODO: Find correct API endpoint for sociedades data
        # The perfilprov-bus/1.0/ficha endpoint doesn't include this information
        # May need to use SUNAT API or web scraping
        url = f"{self.fup_base}/sociedades/{ruc}"
        try:
            return await self._make_request(url)
        except OSCEAPIException as e:
            logger.warning(f"Could not fetch sociedades for {ruc}: {e}")
            return {"listaSocios": []}

    async def get_representantes(self, ruc: str) -> Dict[str, Any]:
        """
        Get legal representatives data.

        Args:
            ruc: Provider's RUC number

        Returns:
            Representatives data dictionary

        Raises:
            OSCEAPIException: If request fails
        """
        url = f"{self.fup_base}/representantes/{ruc}"
        try:
            return await self._make_request(url)
        except OSCEAPIException as e:
            logger.warning(f"Could not fetch representantes for {ruc}: {e}")
            return {"listaRepresentantes": []}

    async def get_organos_administracion(self, ruc: str) -> Dict[str, Any]:
        """
        Get administrative bodies data.

        Args:
            ruc: Provider's RUC number

        Returns:
            Administrative bodies data dictionary

        Raises:
            OSCEAPIException: If request fails
        """
        url = f"{self.fup_base}/organos-administracion/{ruc}"
        try:
            return await self._make_request(url)
        except OSCEAPIException as e:
            logger.warning(f"Could not fetch organos for {ruc}: {e}")
            return {"listaOrganos": []}

    async def get_experiencia(self, ruc: str, limit: int = 50) -> Dict[str, Any]:
        """
        Get provider experience/contracts data.

        Args:
            ruc: Provider's RUC number
            limit: Maximum number of contracts to retrieve

        Returns:
            Contracts data dictionary

        Raises:
            OSCEAPIException: If request fails
        """
        url = f"{self.expprov_base}/contratos/{ruc}?limite={limit}"
        try:
            return await self._make_request(url)
        except OSCEAPIException as e:
            logger.warning(f"Could not fetch experiencia for {ruc}: {e}")
            return {"listaContratos": []}
