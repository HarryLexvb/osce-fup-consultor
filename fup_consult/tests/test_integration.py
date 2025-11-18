"""
Integration tests for the complete consultation flow.
"""

import pytest
from django.test import Client
from django.urls import reverse


@pytest.mark.integration
@pytest.mark.django_db
class TestConsultationFlow:
    """Test suite for complete consultation flow."""

    def test_search_page_loads(self) -> None:
        """Test that search page loads successfully."""
        client = Client()
        response = client.get(reverse("fup_consult:search"))

        assert response.status_code == 200
        assert "Consultar Ficha del Proveedor" in response.content.decode()

    def test_search_form_submission_redirects(self, sample_ruc: str) -> None:
        """Test that form submission redirects to results page."""
        client = Client()
        response = client.post(
            reverse("fup_consult:search"), data={"ruc": sample_ruc}, follow=False
        )

        assert response.status_code == 302
        assert f"/resultados/{sample_ruc}/" in response.url

    def test_invalid_ruc_shows_error(self) -> None:
        """Test that invalid RUC shows validation error."""
        client = Client()
        response = client.post(reverse("fup_consult:search"), data={"ruc": "123"})

        assert response.status_code == 200
        assert "11 dígitos" in response.content.decode()

    def test_results_page_with_valid_data(self, httpx_mock, sample_ruc: str) -> None:
        """Test results page displays provider data correctly."""
        # Mock all required endpoints
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
        )

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/sociedades/{sample_ruc}",
            json={"resultadoT01": {"codigo": "00"}, "listaSocios": []},
        )

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/representantes/{sample_ruc}",
            json={"resultadoT01": {"codigo": "00"}, "listaRepresentantes": []},
        )

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/organos-administracion/{sample_ruc}",
            json={"resultadoT01": {"codigo": "00"}, "listaOrganos": []},
        )

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/expprov-bus/1.0/contratos/{sample_ruc}?limite=50",
            json={"resultadoT01": {"codigo": "00"}, "listaContratos": []},
        )

        client = Client()
        response = client.get(reverse("fup_consult:results", kwargs={"ruc": sample_ruc}))

        assert response.status_code == 200
        content = response.content.decode()
        assert "EMPRESA TEST SAC" in content
        assert sample_ruc in content
        assert "ACTIVO" in content

    def test_results_page_with_invalid_ruc(self) -> None:
        """Test results page with invalid RUC format."""
        client = Client()
        response = client.get(reverse("fup_consult:results", kwargs={"ruc": "123"}))

        assert response.status_code == 200
        assert "RUC inválido" in response.content.decode()

    def test_download_excel_success(self, httpx_mock, sample_ruc: str) -> None:
        """Test Excel download with valid data."""
        # Mock all endpoints
        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{sample_ruc}",
            json={
                "resultadoT01": {"codigo": "00"},
                "proveedorT01": {
                    "ruc": sample_ruc,
                    "razonSocial": "TEST",
                    "estado": "ACTIVO",
                    "condicion": "HABIDO",
                    "tipoContribuyente": "SAC",
                    "departamento": "LIMA",
                    "provincia": "LIMA",
                    "distrito": "LIMA",
                    "direccion": "DIR",
                    "telefonos": [],
                    "emails": [],
                },
            },
        )

        for endpoint in ["sociedades", "representantes", "organos-administracion"]:
            httpx_mock.add_response(
                url=f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/{endpoint}/{sample_ruc}",
                json={"resultadoT01": {"codigo": "00"}},
            )

        httpx_mock.add_response(
            url=f"https://eap.oece.gob.pe/expprov-bus/1.0/contratos/{sample_ruc}?limite=50",
            json={"resultadoT01": {"codigo": "00"}},
        )

        client = Client()
        response = client.get(reverse("fup_consult:download_excel", kwargs={"ruc": sample_ruc}))

        assert response.status_code == 200
        assert (
            response["Content-Type"]
            == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        assert f"ficha_fup_{sample_ruc}.xlsx" in response["Content-Disposition"]
