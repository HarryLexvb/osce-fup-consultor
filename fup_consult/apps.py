"""
FUP Consult App Configuration.
"""

from django.apps import AppConfig


class FupConsultConfig(AppConfig):
    """Configuration for the FUP Consult application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "fup_consult"
    verbose_name = "Consulta de Ficha Única del Proveedor"
