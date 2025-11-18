"""
URL Configuration for FUP Consult app.
"""

from django.urls import path

from . import views

app_name = "fup_consult"

urlpatterns = [
    path("", views.search_view, name="search"),
    path("resultados/<str:ruc>/", views.results_view, name="results"),
    path("descargar-excel/<str:ruc>/", views.download_excel_view, name="download_excel"),
]
