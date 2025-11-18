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
    domicilio: Optional[str] = None  # Complete address e.g., "LIMA / LIMA / SAN ISIDRO"
    departamento: Optional[str] = None
    provincia: Optional[str] = None
    distrito: Optional[str] = None
    personeria: Optional[str] = None  # Código de personería
    telefonos: List[str] = None
    emails: List[str] = None
    fecha_inscripcion: Optional[str] = None
    sistema_emision: Optional[str] = None
    actividad_economica: Optional[str] = None
    
    def __post_init__(self):
        if self.telefonos is None:
            self.telefonos = []
        if self.emails is None:
            self.emails = []


@dataclass
class Socio:
    """Shareholder or partner information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    porcentaje_participacion: Optional[str] = None
    numero_acciones: Optional[float] = None
    desc_tipo_documento: Optional[str] = None
    fecha_ingreso: Optional[str] = None


@dataclass
class Representante:
    """Legal representative information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    cargo: Optional[str] = None
    desc_tipo_documento: Optional[str] = None
    fecha_desde: Optional[str] = None


@dataclass
class OrganoAdministracion:
    """Administrative body member information."""

    nombre_completo: str
    tipo_documento: str
    numero_documento: str
    cargo: str
    desc_tipo_documento: Optional[str] = None
    tipo_organo: Optional[str] = None  # GERENCIA, DIRECTORIO, etc.
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
