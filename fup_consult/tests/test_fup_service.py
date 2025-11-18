"""
Unit tests for FUP service layer.
"""

import pytest

from fup_consult.models import ProviderData
from fup_consult.services.fup_service import FUPService


@pytest.mark.unit
class TestFUPService:
    """Test suite for FUP service."""

    @pytest.mark.asyncio
    async def test_get_provider_data_success(self, httpx_mock, sample_ruc: str) -> None:
        """Test successful retrieval and aggregation of provider data."""
        # Mock general data
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            json={
                "resultadoT01": {"codigo": "00"},
                "proveedorT01": {
                    "ruc": sample_ruc,
                    "razonSocial": "EMPRESA TEST SAC",
                    "estado": "ACTIVO",
                    "condicion": "HABIDO",
                    "tipoContribuyente": "SOCIEDAD ANONIMA CERRADA",
                    "departamento": "LIMA",
                    "provincia": "LIMA",
                    "distrito": "MIRAFLORES",
                    "direccion": "AV. TEST 123",
                    "telefonos": ["999888777"],
                    "emails": ["test@empresa.com"],
                },
            },
            status_code=200,
        )

        # Mock sociedades
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/sociedades/{sample_ruc}",
            json={
                "resultadoT01": {"codigo": "00"},
                "listaSocios": [
                    {
                        "nombreCompleto": "JUAN PEREZ",
                        "tipoDocumento": "DNI",
                        "numeroDocumento": "12345678",
                    }
                ],
            },
            status_code=200,
        )

        # Mock representantes
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/representantes/{sample_ruc}",
            json={"resultadoT01": {"codigo": "00"}, "listaRepresentantes": []},
            status_code=200,
        )

        # Mock organos
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/organos-administracion/{sample_ruc}",
            json={"resultadoT01": {"codigo": "00"}, "listaOrganos": []},
            status_code=200,
        )

        # Mock experiencia
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/expprov-bus/1.0/contratos/{sample_ruc}?limite=50",
            json={"resultadoT01": {"codigo": "00"}, "listaContratos": []},
            status_code=200,
        )

        service = FUPService()
        provider_data = await service.get_provider_data(sample_ruc)

        assert isinstance(provider_data, ProviderData)
        assert provider_data.general.ruc == sample_ruc
        assert provider_data.general.razon_social == "EMPRESA TEST SAC"
        assert len(provider_data.socios) == 1
        assert provider_data.socios[0].nombre_completo == "JUAN PEREZ"

    @pytest.mark.asyncio
    async def test_get_provider_data_not_found(self, httpx_mock, sample_ruc: str) -> None:
        """Test handling of provider not found."""
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            json={"resultadoT01": {"codigo": "01", "mensaje": "RUC no encontrado"}},
            status_code=200,
        )

        service = FUPService()
        provider_data = await service.get_provider_data(sample_ruc)

        assert provider_data.error_message is not None
        assert "RUC no encontrado" in provider_data.error_message

    @pytest.mark.asyncio
    async def test_normalize_general_data(self) -> None:
        """Test normalization of general data from API response."""
        raw_data = {
            "proveedorT01": {
                "ruc": "20508238143",
                "razonSocial": "TEST SAC",
                "estado": "ACTIVO",
                "condicion": "HABIDO",
                "tipoContribuyente": "SAC",
                "departamento": "LIMA",
                "provincia": "LIMA",
                "distrito": "SURCO",
                "direccion": "AV TEST 123",
                "telefonos": ["999888777"],
                "emails": ["test@test.com"],
            }
        }

        service = FUPService()
        general_data = service._normalize_general_data(raw_data)

        assert general_data.ruc == "20508238143"
        assert general_data.razon_social == "TEST SAC"
        assert general_data.estado == "ACTIVO"
        assert len(general_data.telefonos) == 1
        assert len(general_data.emails) == 1
