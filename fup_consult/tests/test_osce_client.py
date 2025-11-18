"""
Unit tests for OSCE API client.
"""

import pytest
from httpx import Response

from fup_consult.services.osce_client import OSCEAPIException, OSCEClient


@pytest.mark.unit
class TestOSCEClient:
    """Test suite for OSCE API client."""

    def test_client_initialization(self) -> None:
        """Test that client initializes with correct base URLs."""
        client = OSCEClient(
            perfilprov_base="https://test.com/perfilprov",
            fup_base="https://test.com/fup",
            expprov_base="https://test.com/expprov",
            timeout=10,
        )
        assert client.perfilprov_base == "https://test.com/perfilprov"
        assert client.fup_base == "https://test.com/fup"
        assert client.expprov_base == "https://test.com/expprov"

    @pytest.mark.asyncio
    async def test_get_provider_general_data_success(self, httpx_mock, sample_ruc: str) -> None:
        """Test successful retrieval of provider general data."""
        mock_response = {
            "resultadoT01": {"codigo": "00", "mensaje": "Exitoso"},
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
            },
        }

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            json=mock_response,
            status_code=200,
        )

        client = OSCEClient()
        data = await client.get_provider_general_data(sample_ruc)

        assert data is not None
        assert data["proveedorT01"]["ruc"] == sample_ruc
        assert data["resultadoT01"]["codigo"] == "00"

    @pytest.mark.asyncio
    async def test_get_provider_general_data_not_found(self, httpx_mock, sample_ruc: str) -> None:
        """Test handling of provider not found response."""
        mock_response = {
            "resultadoT01": {"codigo": "01", "mensaje": "RUC no encontrado"},
        }

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            json=mock_response,
            status_code=200,
        )

        client = OSCEClient()

        with pytest.raises(OSCEAPIException) as exc_info:
            await client.get_provider_general_data(sample_ruc)

        assert "RUC no encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_provider_general_data_http_error(self, httpx_mock, sample_ruc: str) -> None:
        """Test handling of HTTP errors."""
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            status_code=500,
        )

        client = OSCEClient()

        with pytest.raises(OSCEAPIException):
            await client.get_provider_general_data(sample_ruc)

    @pytest.mark.asyncio
    async def test_get_provider_general_data_timeout(self, httpx_mock, sample_ruc: str) -> None:
        """Test handling of timeout errors."""
        from httpx import TimeoutException

        httpx_mock.add_exception(
            TimeoutException("Request timed out"),
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
        )

        client = OSCEClient(timeout=1)

        with pytest.raises(OSCEAPIException) as exc_info:
            await client.get_provider_general_data(sample_ruc)

        assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_sociedades_success(self, httpx_mock, sample_ruc: str) -> None:
        """Test successful retrieval of shareholders data."""
        mock_response = {
            "resultadoT01": {"codigo": "00"},
            "listaSocios": [
                {
                    "nombreCompleto": "JUAN PEREZ GARCIA",
                    "tipoDocumento": "DNI",
                    "numeroDocumento": "12345678",
                }
            ],
        }

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/sociedades/{sample_ruc}",
            json=mock_response,
            status_code=200,
        )

        client = OSCEClient()
        data = await client.get_sociedades(sample_ruc)

        assert data is not None
        assert len(data.get("listaSocios", [])) == 1

    @pytest.mark.asyncio
    async def test_get_representantes_success(self, httpx_mock, sample_ruc: str) -> None:
        """Test successful retrieval of legal representatives data."""
        mock_response = {
            "resultadoT01": {"codigo": "00"},
            "listaRepresentantes": [
                {
                    "nombreCompleto": "MARIA LOPEZ TORRES",
                    "tipoDocumento": "DNI",
                    "numeroDocumento": "87654321",
                    "cargo": "GERENTE GENERAL",
                }
            ],
        }

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/representantes/{sample_ruc}",
            json=mock_response,
            status_code=200,
        )

        client = OSCEClient()
        data = await client.get_representantes(sample_ruc)

        assert data is not None
        assert len(data.get("listaRepresentantes", [])) == 1
