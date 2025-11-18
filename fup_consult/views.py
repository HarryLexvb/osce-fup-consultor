"""
Views for FUP consultation.
"""

import asyncio
import logging

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from fup_consult.exporters.excel_exporter import ExcelExporter
from fup_consult.forms import RUCSearchForm
from fup_consult.services.fup_service import FUPService

logger = logging.getLogger(__name__)


def search_view(request: HttpRequest) -> HttpResponse:
    """
    Display RUC search form.

    Args:
        request: HTTP request

    Returns:
        Rendered search page
    """
    if request.method == "POST":
        form = RUCSearchForm(request.POST)
        if form.is_valid():
            ruc = form.cleaned_data["ruc"]
            # Redirect to results page
            from django.shortcuts import redirect

            return redirect("fup_consult:results", ruc=ruc)
    else:
        form = RUCSearchForm()

    return render(request, "fup_consult/search.html", {"form": form})


def results_view(request: HttpRequest, ruc: str) -> HttpResponse:
    """
    Display provider information for given RUC.

    Args:
        request: HTTP request
        ruc: Provider's RUC number

    Returns:
        Rendered results page
    """
    # Validate RUC format
    form = RUCSearchForm(data={"ruc": ruc})
    if not form.is_valid():
        return render(
            request,
            "fup_consult/error.html",
            {"error_message": "RUC inválido. Debe contener exactamente 11 dígitos numéricos."},
        )

    # Fetch provider data
    try:
        service = FUPService()
        provider_data = asyncio.run(service.get_provider_data(ruc))

        if provider_data.error_message:
            return render(
                request,
                "fup_consult/error.html",
                {
                    "error_message": "No se pudo obtener la información del proveedor. "
                    "Por favor, verifique el RUC e intente nuevamente."
                },
            )

        return render(
            request,
            "fup_consult/results.html",
            {"provider_data": provider_data, "ruc": ruc},
        )

    except Exception as e:
        logger.error(f"Error fetching provider data for RUC {ruc}: {e}", exc_info=True)
        return render(
            request,
            "fup_consult/error.html",
            {
                "error_message": "En este momento no se puede obtener la información desde OSCE. "
                "Por favor, intente nuevamente más tarde."
            },
        )


def download_excel_view(request: HttpRequest, ruc: str) -> HttpResponse:
    """
    Generate and download Excel file for given RUC.

    Args:
        request: HTTP request
        ruc: Provider's RUC number

    Returns:
        Excel file download response
    """
    try:
        # Fetch provider data
        service = FUPService()
        provider_data = asyncio.run(service.get_provider_data(ruc))

        if provider_data.error_message:
            return render(
                request,
                "fup_consult/error.html",
                {"error_message": "No se pudo generar el archivo Excel."},
            )

        # Generate Excel
        exporter = ExcelExporter()
        excel_bytes = exporter.generate_excel(provider_data)

        # Create response
        response = HttpResponse(
            excel_bytes,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="ficha_fup_{ruc}.xlsx"'

        return response

    except Exception as e:
        logger.error(f"Error generating Excel for RUC {ruc}: {e}", exc_info=True)
        return render(
            request,
            "fup_consult/error.html",
            {"error_message": "Error al generar el archivo Excel."},
        )
