"""
Data models for OSCE API responses.

This module defines the data structures used to represent provider information
from the OSCE public APIs, as well as Django models for batch processing.
"""

from dataclasses import dataclass
from typing import List, Optional
import uuid

from django.db import models
from django.utils import timezone


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


# ============================================================================
# Django Models for Batch Processing
# ============================================================================

class BatchJobStatus(models.TextChoices):
    """Status choices for batch jobs."""
    PENDING = 'pending', 'Pendiente'
    PROCESSING = 'processing', 'Procesando'
    COMPLETED = 'completed', 'Completado'
    FAILED = 'failed', 'Fallido'
    CANCELLED = 'cancelled', 'Cancelado'


class BatchItemStatus(models.TextChoices):
    """Status choices for individual batch items."""
    PENDING = 'pending', 'Pendiente'
    PROCESSING = 'processing', 'Procesando'
    COMPLETED = 'completed', 'Completado'
    FAILED = 'failed', 'Fallido'
    RETRYING = 'retrying', 'Reintentando'


class BatchJob(models.Model):
    """
    Represents a batch processing job for multiple RUCs.
    
    Tracks the overall progress, status, and metadata for a batch upload.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    filename = models.CharField(max_length=255, help_text="Original filename")
    status = models.CharField(
        max_length=20,
        choices=BatchJobStatus.choices,
        default=BatchJobStatus.PENDING,
        db_index=True
    )
    
    # Statistics
    total_items = models.IntegerField(default=0)
    completed_items = models.IntegerField(default=0)
    failed_items = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Results
    result_file = models.FileField(upload_to='batch_results/', null=True, blank=True)
    error_message = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at', 'status']),
        ]
    
    def __str__(self):
        return f"BatchJob {self.id} - {self.filename} ({self.status})"
    
    @property
    def progress_percentage(self):
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0
        return int((self.completed_items / self.total_items) * 100)
    
    @property
    def pending_items_count(self):
        """Calculate number of pending items."""
        return self.total_items - self.completed_items - self.failed_items
    
    def mark_started(self):
        """Mark job as started."""
        self.status = BatchJobStatus.PROCESSING
        self.started_at = timezone.now()
        self.save(update_fields=['status', 'started_at'])
    
    def mark_completed(self):
        """Mark job as completed."""
        self.status = BatchJobStatus.COMPLETED
        self.completed_at = timezone.now()
        self.save(update_fields=['status', 'completed_at'])
    
    def mark_failed(self, error_message: str = ""):
        """Mark job as failed."""
        self.status = BatchJobStatus.FAILED
        self.completed_at = timezone.now()
        self.error_message = error_message
        self.save(update_fields=['status', 'completed_at', 'error_message'])
    
    def increment_completed(self):
        """Increment completed items counter."""
        self.completed_items += 1
        self.save(update_fields=['completed_items'])
    
    def increment_failed(self):
        """Increment failed items counter."""
        self.failed_items += 1
        self.save(update_fields=['failed_items'])


class BatchItem(models.Model):
    """
    Represents a single RUC within a batch job.
    
    Tracks the processing status, retries, and results for each RUC.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_job = models.ForeignKey(
        BatchJob,
        on_delete=models.CASCADE,
        related_name='items'
    )
    ruc = models.CharField(max_length=11, db_index=True)
    status = models.CharField(
        max_length=20,
        choices=BatchItemStatus.choices,
        default=BatchItemStatus.PENDING,
        db_index=True
    )
    
    # Processing details
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True)
    
    # Results (stored as JSON)
    result_data = models.JSONField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['created_at']
        unique_together = [['batch_job', 'ruc']]
        indexes = [
            models.Index(fields=['batch_job', 'status']),
            models.Index(fields=['ruc']),
        ]
    
    def __str__(self):
        return f"BatchItem {self.ruc} - {self.status}"
    
    def mark_processing(self):
        """Mark item as processing."""
        self.status = BatchItemStatus.PROCESSING
        self.save(update_fields=['status'])
    
    def mark_completed(self, result_data: dict):
        """Mark item as completed with result data."""
        self.status = BatchItemStatus.COMPLETED
        self.processed_at = timezone.now()
        self.result_data = result_data
        self.save(update_fields=['status', 'processed_at', 'result_data'])
        
        # Update batch job counters
        self.batch_job.increment_completed()
    
    def mark_failed(self, error_message: str):
        """Mark item as failed."""
        self.retry_count += 1
        
        if self.retry_count < self.max_retries:
            self.status = BatchItemStatus.RETRYING
        else:
            self.status = BatchItemStatus.FAILED
            self.batch_job.increment_failed()
        
        self.error_message = error_message
        self.processed_at = timezone.now()
        self.save(update_fields=['status', 'retry_count', 'error_message', 'processed_at'])
    
    def can_retry(self):
        """Check if item can be retried."""
        return self.retry_count < self.max_retries and self.status in [
            BatchItemStatus.FAILED,
            BatchItemStatus.RETRYING
        ]
