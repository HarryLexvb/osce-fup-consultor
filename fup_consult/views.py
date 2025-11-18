"""
Views for FUP consultation.
"""

import asyncio
import logging
import tempfile
import threading
from pathlib import Path

from django.http import HttpRequest, HttpResponse, JsonResponse, FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage

from fup_consult.exporters.excel_exporter import ExcelExporter
from fup_consult.forms import RUCSearchForm
from fup_consult.services.fup_service import FUPService
from fup_consult.services.batch_service import BatchProcessingService
from fup_consult.models import BatchJob, BatchItem, BatchItemStatus

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
        # Read USE_SUNAT_SCRAPING from environment
        import os
        use_sunat = os.getenv("USE_SUNAT_SCRAPING", "False").lower() == "true"
        use_osce_angular = os.getenv("USE_OSCE_ANGULAR_SCRAPING", "True").lower() == "true"
        
        service = FUPService(use_sunat=use_sunat, use_osce_angular=use_osce_angular)
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
        import os
        use_sunat = os.getenv("USE_SUNAT_SCRAPING", "False").lower() == "true"
        use_osce_angular = os.getenv("USE_OSCE_ANGULAR_SCRAPING", "True").lower() == "true"
        
        service = FUPService(use_sunat=use_sunat, use_osce_angular=use_osce_angular)
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


# ============================================================================
# Batch Processing Views
# ============================================================================

@csrf_exempt
@require_http_methods(["POST"])
def batch_upload_view(request: HttpRequest) -> JsonResponse:
    """
    Handle batch Excel file upload.
    
    Expects multipart/form-data with 'file' field containing Excel file.
    
    Returns:
        JSON response with batch_id and initial status
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No se proporcionó ningún archivo'
            }, status=400)
        
        uploaded_file = request.FILES['file']
        
        # Validate file extension
        if not uploaded_file.name.endswith(('.xlsx', '.xls')):
            return JsonResponse({
                'success': False,
                'error': 'El archivo debe ser un Excel (.xlsx o .xls)'
            }, status=400)
        
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp_file:
            for chunk in uploaded_file.chunks():
                tmp_file.write(chunk)
            tmp_file_path = tmp_file.name
        
        # Create batch job
        service = BatchProcessingService()
        batch_job = asyncio.run(
            service.create_batch_from_excel(
                tmp_file_path,
                uploaded_file.name
            )
        )
        
        # Clean up temp file
        Path(tmp_file_path).unlink()
        
        # Start processing in background thread
        def process_in_background():
            asyncio.run(service.process_batch(str(batch_job.id)))
        
        thread = threading.Thread(target=process_in_background, daemon=True)
        thread.start()
        
        return JsonResponse({
            'success': True,
            'batch_id': str(batch_job.id),
            'filename': batch_job.filename,
            'total_items': batch_job.total_items,
            'message': f'Procesamiento iniciado para {batch_job.total_items} RUCs'
        })
        
    except ValueError as e:
        logger.error(f"Validation error in batch upload: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error in batch upload: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Error al procesar el archivo. Por favor, intente nuevamente.'
        }, status=500)


@require_http_methods(["GET"])
def batch_status_view(request: HttpRequest, batch_id: str) -> JsonResponse:
    """
    Get current status of a batch job.
    
    Args:
        request: HTTP request
        batch_id: UUID of the batch job
    
    Returns:
        JSON response with batch status and statistics
    """
    try:
        service = BatchProcessingService()
        status = asyncio.run(service.get_batch_status(batch_id))
        
        # Add sample results for preview (last 10 completed items)
        batch_job = BatchJob.objects.get(id=batch_id)
        completed_items = batch_job.items.filter(
            status=BatchItemStatus.COMPLETED
        ).order_by('-processed_at')[:10]
        
        sample_results = []
        for item in completed_items:
            if item.result_data:
                sample_results.append({
                    'ruc': item.result_data.get('ruc', ''),
                    'razon_social': item.result_data.get('razon_social', ''),
                    'estado': item.result_data.get('estado', ''),
                    'num_socios': item.result_data.get('num_socios', 0),
                    'num_representantes': item.result_data.get('num_representantes', 0),
                    'num_organos': item.result_data.get('num_organos', 0),
                })
        
        status['sample_results'] = sample_results
        
        return JsonResponse({
            'success': True,
            'status': status
        })
        
    except BatchJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Batch no encontrado'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error getting batch status: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Error al obtener el estado del procesamiento'
        }, status=500)


@require_http_methods(["GET"])
def batch_download_view(request: HttpRequest, batch_id: str) -> HttpResponse:
    """
    Download result Excel file for completed batch.
    
    Args:
        request: HTTP request
        batch_id: UUID of the batch job
    
    Returns:
        Excel file download response or error
    """
    try:
        batch_job = BatchJob.objects.get(id=batch_id)
        
        if not batch_job.result_file:
            return JsonResponse({
                'success': False,
                'error': 'El resultado aún no está disponible'
            }, status=404)
        
        # Return file
        response = FileResponse(
            batch_job.result_file.open('rb'),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = (
            f'attachment; filename="batch_result_{batch_job.filename}"'
        )
        
        return response
        
    except BatchJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Batch no encontrado'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error downloading batch result: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Error al descargar el archivo'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def batch_cancel_view(request: HttpRequest, batch_id: str) -> JsonResponse:
    """
    Cancel a running batch job.
    
    Args:
        request: HTTP request
        batch_id: UUID of the batch job
    
    Returns:
        JSON response confirming cancellation
    """
    try:
        service = BatchProcessingService()
        asyncio.run(service.cancel_batch(batch_id))
        
        return JsonResponse({
            'success': True,
            'message': 'Procesamiento cancelado'
        })
        
    except BatchJob.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Batch no encontrado'
        }, status=404)
    
    except Exception as e:
        logger.error(f"Error canceling batch: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Error al cancelar el procesamiento'
        }, status=500)


def batch_list_view(request: HttpRequest) -> HttpResponse:
    """
    Display list of batch jobs.
    
    Args:
        request: HTTP request
    
    Returns:
        Rendered batch list page
    """
    batches = BatchJob.objects.all().order_by('-created_at')[:50]
    return render(request, "fup_consult/batch_list.html", {"batches": batches})

