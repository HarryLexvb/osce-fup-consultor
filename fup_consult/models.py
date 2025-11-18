"""
Data models for OSCE API responses.

This module defines the data structures used to represent provider information
from the OSCE public APIs.
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class GeneralData:
    """General provider information."""

    ruc: str
    razon_social: str
    estado: str
    condicion: str
    tipo_contribuyente: str
    departamento: str
    provincia: str
    distrito: str
    direccion: str
    telefonos: List[str]
    emails: List[str]
    fecha_inscripcion: Optional[str] = None
    sistema_emision: Optional[str] = None
    actividad_economica: Optional[str] = None


@dataclass
class Socio:
    """Shareholder or partner information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    porcentaje_participacion: Optional[str] = None


@dataclass
class Representante:
    """Legal representative information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    cargo: Optional[str] = None
    fecha_desde: Optional[str] = None


@dataclass
class OrganoAdministracion:
    """Administrative body member information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    cargo: str
    fecha_desde: Optional[str] = None


@dataclass
class ContratoExperiencia:
    """Contract experience information."""

    numero_contrato: str
    entidad: str
    objeto_contractual: str
    monto: Optional[float] = None
    fecha_suscripcion: Optional[str] = None
    estado: Optional[str] = None


@dataclass
class ProviderData:
    """Complete provider information aggregated from multiple APIs."""

    general: GeneralData
    socios: List[Socio]
    representantes: List[Representante]
    organos_administracion: List[OrganoAdministracion]
    experiencia: List[ContratoExperiencia]
    error_message: Optional[str] = None
