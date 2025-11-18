"""
FUP service for aggregating and normalizing provider data.

This module provides a high-level service that coordinates calls to multiple
OSCE APIs and normalizes the data into a unified ProviderData structure.
"""

import logging
from typing import Any, Dict, List

from fup_consult.models import (
    ContratoExperiencia,
    GeneralData,
    OrganoAdministracion,
    ProviderData,
    Representante,
    Socio,
)
from fup_consult.services.osce_client import OSCEAPIException, OSCEClient

logger = logging.getLogger(__name__)


class FUPService:
    """Service for retrieving and normalizing FUP data."""

    def __init__(self, client: OSCEClient = None) -> None:
        """
        Initialize FUP service.

        Args:
            client: OSCE API client (creates new one if not provided)
        """
        self.client = client or OSCEClient()

    async def get_provider_data(self, ruc: str) -> ProviderData:
        """
        Get complete provider data for given RUC.

        Args:
            ruc: Provider's RUC number

        Returns:
            Complete provider data
        """
        try:
            # Fetch general data (required)
            general_data_raw = await self.client.get_provider_general_data(ruc)
            general_data = self._normalize_general_data(general_data_raw)

            # Fetch optional data (non-blocking if fails)
            sociedades_raw = await self.client.get_sociedades(ruc)
            socios = self._normalize_socios(sociedades_raw)

            representantes_raw = await self.client.get_representantes(ruc)
            representantes = self._normalize_representantes(representantes_raw)

            organos_raw = await self.client.get_organos_administracion(ruc)
            organos = self._normalize_organos(organos_raw)

            experiencia_raw = await self.client.get_experiencia(ruc)
            experiencia = self._normalize_experiencia(experiencia_raw)

            return ProviderData(
                general=general_data,
                socios=socios,
                representantes=representantes,
                organos_administracion=organos,
                experiencia=experiencia,
            )

        except OSCEAPIException as e:
            logger.error(f"Failed to get provider data for {ruc}: {e}")
            # Return minimal ProviderData with error message
            return ProviderData(
                general=GeneralData(
                    ruc=ruc,
                    razon_social="",
                    estado="",
                    condicion="",
                    tipo_contribuyente="",
                    departamento="",
                    provincia="",
                    distrito="",
                    direccion="",
                    telefonos=[],
                    emails=[],
                ),
                socios=[],
                representantes=[],
                organos_administracion=[],
                experiencia=[],
                error_message=str(e),
            )

    def _normalize_general_data(self, raw_data: Dict[str, Any]) -> GeneralData:
        """
        Normalize general provider data from API response.

        Args:
            raw_data: Raw API response

        Returns:
            Normalized GeneralData object
        """
        proveedor = raw_data.get("proveedorT01", {})

        return GeneralData(
            ruc=proveedor.get("ruc", ""),
            razon_social=proveedor.get("razonSocial", ""),
            estado=proveedor.get("estado", ""),
            condicion=proveedor.get("condicion", ""),
            tipo_contribuyente=proveedor.get("tipoContribuyente", ""),
            departamento=proveedor.get("departamento", ""),
            provincia=proveedor.get("provincia", ""),
            distrito=proveedor.get("distrito", ""),
            direccion=proveedor.get("direccion", ""),
            telefonos=proveedor.get("telefonos", []),
            emails=proveedor.get("emails", []),
            fecha_inscripcion=proveedor.get("fechaInscripcion"),
            sistema_emision=proveedor.get("sistemaEmision"),
            actividad_economica=proveedor.get("actividadEconomica"),
        )

    def _normalize_socios(self, raw_data: Dict[str, Any]) -> List[Socio]:
        """
        Normalize shareholders data from API response.

        Args:
            raw_data: Raw API response

        Returns:
            List of Socio objects
        """
        lista_socios = raw_data.get("listaSocios", [])
        socios = []

        for socio_raw in lista_socios:
            socio = Socio(
                nombre_completo=socio_raw.get("nombreCompleto", ""),
                tipo_documento=socio_raw.get("tipoDocumento", ""),
                numero_documento=socio_raw.get("numeroDocumento", ""),
                porcentaje_participacion=socio_raw.get("porcentajeParticipacion"),
            )
            socios.append(socio)

        return socios

    def _normalize_representantes(self, raw_data: Dict[str, Any]) -> List[Representante]:
        """
        Normalize legal representatives data from API response.

        Args:
            raw_data: Raw API response

        Returns:
            List of Representante objects
        """
        lista_representantes = raw_data.get("listaRepresentantes", [])
        representantes = []

        for rep_raw in lista_representantes:
            rep = Representante(
                nombre_completo=rep_raw.get("nombreCompleto", ""),
                tipo_documento=rep_raw.get("tipoDocumento", ""),
                numero_documento=rep_raw.get("numeroDocumento", ""),
                cargo=rep_raw.get("cargo"),
                fecha_desde=rep_raw.get("fechaDesde"),
            )
            representantes.append(rep)

        return representantes

    def _normalize_organos(self, raw_data: Dict[str, Any]) -> List[OrganoAdministracion]:
        """
        Normalize administrative bodies data from API response.

        Args:
            raw_data: Raw API response

        Returns:
            List of OrganoAdministracion objects
        """
        lista_organos = raw_data.get("listaOrganos", [])
        organos = []

        for org_raw in lista_organos:
            org = OrganoAdministracion(
                nombre_completo=org_raw.get("nombreCompleto", ""),
                tipo_documento=org_raw.get("tipoDocumento", ""),
                numero_documento=org_raw.get("numeroDocumento", ""),
                cargo=org_raw.get("cargo", ""),
                fecha_desde=org_raw.get("fechaDesde"),
            )
            organos.append(org)

        return organos

    def _normalize_experiencia(self, raw_data: Dict[str, Any]) -> List[ContratoExperiencia]:
        """
        Normalize contracts/experience data from API response.

        Args:
            raw_data: Raw API response

        Returns:
            List of ContratoExperiencia objects
        """
        lista_contratos = raw_data.get("listaContratos", [])
        contratos = []

        for contrato_raw in lista_contratos:
            contrato = ContratoExperiencia(
                numero_contrato=contrato_raw.get("numeroContrato", ""),
                entidad=contrato_raw.get("entidad", ""),
                objeto_contractual=contrato_raw.get("objetoContractual", ""),
                monto=contrato_raw.get("monto"),
                fecha_suscripcion=contrato_raw.get("fechaSuscripcion"),
                estado=contrato_raw.get("estado"),
            )
            contratos.append(contrato)

        return contratos
