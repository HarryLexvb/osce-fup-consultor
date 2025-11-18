"""
Django admin configuration for fup_consult app.
"""

from django.contrib import admin
from fup_consult.models import BatchJob, BatchItem


@admin.register(BatchJob)
class BatchJobAdmin(admin.ModelAdmin):
    """Admin interface for BatchJob model."""
    
    list_display = [
        'id', 'filename', 'status', 'total_items', 'completed_items',
        'failed_items', 'progress_percentage', 'created_at'
    ]
    list_filter = ['status', 'created_at']
    search_fields = ['id', 'filename']
    readonly_fields = [
        'id', 'created_at', 'started_at', 'completed_at',
        'progress_percentage', 'pending_items_count'
    ]
    
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'filename', 'status')
        }),
        ('Estadísticas', {
            'fields': (
                'total_items', 'completed_items', 'failed_items',
                'pending_items_count', 'progress_percentage'
            )
        }),
        ('Fechas', {
            'fields': ('created_at', 'started_at', 'completed_at')
        }),
        ('Resultados', {
            'fields': ('result_file', 'error_message')
        }),
    )


@admin.register(BatchItem)
class BatchItemAdmin(admin.ModelAdmin):
    """Admin interface for BatchItem model."""
    
    list_display = [
        'id', 'batch_job', 'ruc', 'status', 'retry_count',
        'max_retries', 'processed_at'
    ]
    list_filter = ['status', 'batch_job', 'processed_at']
    search_fields = ['id', 'ruc', 'batch_job__filename']
    readonly_fields = ['id', 'created_at', 'processed_at']
    
    fieldsets = (
        ('Información General', {
            'fields': ('id', 'batch_job', 'ruc', 'status')
        }),
        ('Reintentos', {
            'fields': ('retry_count', 'max_retries', 'error_message')
        }),
        ('Fechas', {
            'fields': ('created_at', 'processed_at')
        }),
        ('Resultados', {
            'fields': ('result_data',)
        }),
    )
