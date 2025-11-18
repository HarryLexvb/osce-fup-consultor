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
from fup_consult.services.sunat_scraper import SUNATScraper, SUNATScraperException
from fup_consult.services.osce_angular_scraper import OSCEAngularScraper, OSCEAngularScraperException

logger = logging.getLogger(__name__)


class FUPService:
    """Service for retrieving and normalizing FUP data."""

    def __init__(self, client: OSCEClient = None, use_sunat: bool = True, use_osce_angular: bool = True) -> None:
        """
        Initialize FUP service.

        Args:
            client: OSCE API client (creates new one if not provided)
            use_sunat: Whether to use SUNAT scraping for additional data
            use_osce_angular: Whether to use OSCE Angular scraping for socios/representantes/organos
        """
        self.client = client or OSCEClient()
        self.use_sunat = use_sunat
        self.use_osce_angular = use_osce_angular
        
        if use_sunat:
            self.sunat_scraper = SUNATScraper()
        else:
            self.sunat_scraper = None
        
        if use_osce_angular:
            self.osce_angular_scraper = OSCEAngularScraper()
        else:
            self.osce_angular_scraper = None

    async def get_provider_data(self, ruc: str) -> ProviderData:
        """
        Get complete provider data for given RUC.
        Uses the /ficha/{ruc}/resumen endpoint which includes all data.

        Args:
            ruc: Provider's RUC number

        Returns:
            Complete provider data
        """
        try:
            # Fetch complete data from OSCE /resumen endpoint
            # This endpoint includes datosSunat + conformacion (socios, representantes, organos)
            data_raw = await self.client.get_provider_general_data(ruc)
            
            # The new endpoint returns already normalized data
            general_data = GeneralData(
                ruc=data_raw["ruc"],
                razon_social=data_raw["razon_social"],
                estado=data_raw["estado"],
                condicion=data_raw["condicion"],
                tipo_contribuyente=data_raw["tipo_contribuyente"],
                domicilio=data_raw["domicilio"],
                telefonos=data_raw.get("telefonos", []),
                emails=data_raw.get("emails", [])
            )
            
            # Convert to model objects
            socios = [
                Socio(
                    nombre_completo=s["nombre_completo"],
                    tipo_documento=s["tipo_documento"],
                    numero_documento=s["numero_documento"],
                    porcentaje_participacion=str(s["porcentaje_participacion"]) if s["porcentaje_participacion"] else None
                )
                for s in data_raw.get("socios", [])
            ]
            
            representantes = [
                Representante(
                    nombre_completo=r["nombre_completo"],
                    tipo_documento=r["tipo_documento"],
                    numero_documento=r["numero_documento"],
                    cargo=r.get("cargo", "REPRESENTANTE LEGAL")
                )
                for r in data_raw.get("representantes", [])
            ]
            
            organos = [
                OrganoAdministracion(
                    nombre_completo=o["nombre_completo"],
                    tipo_documento=o["tipo_documento"],
                    numero_documento=o["numero_documento"],
                    cargo=o["cargo"]
                )
                for o in data_raw.get("organos", [])
            ]
            
            logger.info(f"Successfully fetched data for {ruc}: "
                       f"{len(socios)} socios, "
                       f"{len(representantes)} representantes, "
                       f"{len(organos)} órganos")

            return ProviderData(
                general=general_data,
                socios=socios,
                representantes=representantes,
                organos_administracion=organos,
                experiencia=[],  # Not requested by user
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
                    domicilio=None,
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

        # Map tipo_personeria to readable format
        tipo_persona_map = {
            1: "PERSONA NATURAL",
            2: "SOCIEDAD ANONIMA CERRADA",
            3: "SOCIEDAD ANONIMA",
            4: "EMPRESA INDIVIDUAL DE RESPONSABILIDAD LIMITADA",
            5: "SOCIEDAD COMERCIAL DE RESPONSABILIDAD LIMITADA"
        }
        tipo_persona = tipo_persona_map.get(proveedor.get("tipoPersoneria", 0), "OTRO")

        # Map OSCE API fields to our data model
        return GeneralData(
            ruc=proveedor.get("numRuc", ""),
            razon_social=proveedor.get("nomRzsProv", ""),
            estado="ACTIVO" if proveedor.get("esHabilitado") else "INACTIVO",
            condicion="HABIDO" if proveedor.get("esAptoContratar") else "NO HABIDO",
            tipo_contribuyente=tipo_persona,
            domicilio=None,  # Will be set from SUNAT scraping
            telefonos=proveedor.get("telefonos", []),
            emails=proveedor.get("emails", []),
            fecha_inscripcion=None,
            sistema_emision=None,
            actividad_economica=None,
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
