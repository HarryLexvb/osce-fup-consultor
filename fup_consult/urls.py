"""
URL Configuration for FUP Consult app.
"""

from django.urls import path

from . import views

app_name = "fup_consult"

urlpatterns = [
    # Single RUC views
    path("", views.search_view, name="search"),
    path("resultados/<str:ruc>/", views.results_view, name="results"),
    path("descargar-excel/<str:ruc>/", views.download_excel_view, name="download_excel"),
    
    # Batch processing views
    path("batch/", views.batch_list_view, name="batch_list"),
    path("batch/upload/", views.batch_upload_view, name="batch_upload"),
    path("batch/<str:batch_id>/status/", views.batch_status_view, name="batch_status"),
    path("batch/<str:batch_id>/download/", views.batch_download_view, name="batch_download"),
    path("batch/<str:batch_id>/cancel/", views.batch_cancel_view, name="batch_cancel"),
]
