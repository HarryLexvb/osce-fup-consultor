"""
Batch processing service for handling multiple RUCs in parallel.

This module provides functionality to process large batches of RUCs
with controlled concurrency, automatic retries, and progress tracking.
"""

import asyncio
import logging
from typing import List, Optional
from pathlib import Path

import openpyxl
from django.core.files.base import ContentFile
from django.db import transaction
from django.utils import timezone

from fup_consult.models import BatchJob, BatchItem, BatchJobStatus, BatchItemStatus
from fup_consult.services.fup_service import FUPService
from fup_consult.exporters.excel_batch_exporter import ExcelBatchExporter

logger = logging.getLogger(__name__)


class BatchProcessingService:
    """Service for processing multiple RUCs in parallel with retry logic."""
    
    def __init__(
        self,
        max_concurrent: int = 20,  # Increased from 10 to 20 for better parallelism
        max_retries: int = 3,
        retry_delay: float = 1.0  # Reduced from 2.0 to 1.0 for faster retries
    ):
        """
        Initialize batch processing service.
        
        Args:
            max_concurrent: Maximum number of concurrent requests (default: 20)
            max_retries: Maximum number of retries per item (default: 3)
            retry_delay: Delay between retries in seconds (default: 1.0)
        """
        self.max_concurrent = max_concurrent
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.fup_service = FUPService()
        self.excel_exporter = ExcelBatchExporter()
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def create_batch_from_excel(self, file_path: str, filename: str) -> BatchJob:
        """
        Create a batch job from an Excel file.
        
        Args:
            file_path: Path to the Excel file
            filename: Original filename
        
        Returns:
            Created BatchJob instance
        
        Raises:
            ValueError: If Excel file is invalid or empty
        """
        try:
            # Load Excel file
            wb = openpyxl.load_workbook(file_path)
            ws = wb.active
            
            # Extract RUCs (assuming first column, skip header)
            rucs = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                if row[0]:  # Check if first column has value
                    ruc = str(row[0]).strip()
                    if ruc and len(ruc) == 11 and ruc.isdigit():
                        rucs.append(ruc)
            
            if not rucs:
                raise ValueError("No valid RUCs found in Excel file")
            
            # Remove duplicates while preserving order
            rucs = list(dict.fromkeys(rucs))
            
            # Create batch job and items using asyncio.to_thread
            def create_batch_in_db():
                with transaction.atomic():
                    batch_job = BatchJob.objects.create(
                        filename=filename,
                        total_items=len(rucs),
                        status=BatchJobStatus.PENDING
                    )
                    
                    # Create batch items
                    batch_items = [
                        BatchItem(
                            batch_job=batch_job,
                            ruc=ruc,
                            max_retries=self.max_retries
                        )
                        for ruc in rucs
                    ]
                    BatchItem.objects.bulk_create(batch_items)
                    return batch_job
            
            batch_job = await asyncio.to_thread(create_batch_in_db)
            
            logger.info(f"Created batch job {batch_job.id} with {len(rucs)} RUCs")
            return batch_job
            
        except Exception as e:
            logger.error(f"Error creating batch from Excel: {e}")
            raise ValueError(f"Invalid Excel file: {str(e)}")
    
    async def process_batch(self, batch_job_id: str) -> BatchJob:
        """
        Process all items in a batch job with parallelism and retries.
        
        Args:
            batch_job_id: UUID of the batch job
        
        Returns:
            Updated BatchJob instance
        """
        try:
            batch_job = await asyncio.to_thread(
                BatchJob.objects.get, id=batch_job_id
            )
            
            # Mark job as started
            await asyncio.to_thread(batch_job.mark_started)
            logger.info(f"Started processing batch job {batch_job.id}")
            
            # Process all items
            await self._process_all_items(batch_job)
            
            # Generate consolidated Excel
            await self._generate_result_file(batch_job)
            
            # Mark job as completed
            await asyncio.to_thread(batch_job.mark_completed)
            logger.info(f"Completed batch job {batch_job.id}")
            
            return batch_job
            
        except Exception as e:
            logger.error(f"Error processing batch {batch_job_id}: {e}")
            await asyncio.to_thread(
                batch_job.mark_failed,
                f"Processing error: {str(e)}"
            )
            raise
    
    async def _process_all_items(self, batch_job: BatchJob):
        """Process all pending and failed items with retries using optimized batching."""
        max_retry_rounds = self.max_retries + 1  # Initial attempt + retries
        batch_size = 100  # Process in batches of 100 for better progress tracking
        
        for round_num in range(max_retry_rounds):
            # Get items to process
            items = await asyncio.to_thread(
                lambda: list(
                    batch_job.items.filter(
                        status__in=[BatchItemStatus.PENDING, BatchItemStatus.RETRYING]
                    )
                )
            )
            
            if not items:
                break
            
            logger.info(
                f"Batch {batch_job.id} - Round {round_num + 1}: "
                f"Processing {len(items)} items with {self.max_concurrent} concurrent workers"
            )
            
            # Process items in chunks for better progress visibility
            for i in range(0, len(items), batch_size):
                chunk = items[i:i + batch_size]
                logger.info(
                    f"Processing chunk {i // batch_size + 1}: "
                    f"items {i + 1} to {min(i + batch_size, len(items))}"
                )
                
                # Process chunk in parallel
                tasks = [self._process_item(item) for item in chunk]
                await asyncio.gather(*tasks, return_exceptions=True)
            
            # Small delay between retry rounds
            if round_num < max_retry_rounds - 1:
                await asyncio.sleep(self.retry_delay)
    
    async def _process_item(self, item: BatchItem):
        """
        Process a single batch item with rate limiting.
        
        Args:
            item: BatchItem to process
        """
        async with self._semaphore:
            try:
                # Mark as processing
                await asyncio.to_thread(item.mark_processing)
                
                # Fetch provider data
                provider_data = await self.fup_service.get_provider_data(item.ruc)
                
                if provider_data.error_message:
                    raise Exception(provider_data.error_message)
                
                # Convert to dict for storage with complete data
                result_data = {
                    'ruc': item.ruc,
                    'razon_social': provider_data.general.razon_social,
                    'estado': provider_data.general.estado,
                    'condicion': provider_data.general.condicion,
                    'tipo_contribuyente': provider_data.general.tipo_contribuyente,
                    'domicilio': provider_data.general.domicilio,
                    'departamento': provider_data.general.departamento,
                    'provincia': provider_data.general.provincia,
                    'distrito': provider_data.general.distrito,
                    'personeria': provider_data.general.personeria,
                    'telefonos': provider_data.general.telefonos,
                    'emails': provider_data.general.emails,
                    'num_socios': len(provider_data.socios),
                    'num_representantes': len(provider_data.representantes),
                    'num_organos': len(provider_data.organos_administracion),
                    # Store complete details
                    'socios': [
                        {
                            'nombre_completo': s.nombre_completo,
                            'tipo_documento': s.tipo_documento,
                            'numero_documento': s.numero_documento,
                            'porcentaje_participacion': s.porcentaje_participacion,
                            'numero_acciones': s.numero_acciones,
                            'desc_tipo_documento': s.desc_tipo_documento,
                            'fecha_ingreso': s.fecha_ingreso,
                        }
                        for s in provider_data.socios
                    ],
                    'representantes': [
                        {
                            'nombre_completo': r.nombre_completo,
                            'tipo_documento': r.tipo_documento,
                            'numero_documento': r.numero_documento,
                            'cargo': r.cargo,
                            'desc_tipo_documento': r.desc_tipo_documento,
                            'fecha_desde': r.fecha_desde,
                        }
                        for r in provider_data.representantes
                    ],
                    'organos_administracion': [
                        {
                            'nombre_completo': o.nombre_completo,
                            'tipo_documento': o.tipo_documento,
                            'numero_documento': o.numero_documento,
                            'cargo': o.cargo,
                            'desc_tipo_documento': o.desc_tipo_documento,
                            'tipo_organo': o.tipo_organo,
                            'fecha_desde': o.fecha_desde,
                        }
                        for o in provider_data.organos_administracion
                    ],
                }
                
                # Mark as completed
                await asyncio.to_thread(item.mark_completed, result_data)
                logger.info(f"Successfully processed RUC {item.ruc}")
                
            except Exception as e:
                error_msg = str(e)
                logger.warning(f"Failed to process RUC {item.ruc}: {error_msg}")
                await asyncio.to_thread(item.mark_failed, error_msg)
    
    async def _generate_result_file(self, batch_job: BatchJob):
        """
        Generate consolidated Excel file with all results.
        
        Args:
            batch_job: BatchJob instance
        """
        try:
            # Get all completed items
            items = await asyncio.to_thread(
                lambda: list(
                    batch_job.items.filter(
                        status=BatchItemStatus.COMPLETED
                    ).order_by('created_at')
                )
            )
            
            if not items:
                logger.warning(f"No completed items for batch {batch_job.id}")
                return
            
            # Extract result data
            results = [item.result_data for item in items if item.result_data]
            
            # Generate Excel
            excel_bytes = await asyncio.to_thread(
                self.excel_exporter.generate_batch_excel,
                results,
                batch_job.filename
            )
            
            # Save to batch job
            filename = f"batch_result_{batch_job.id}.xlsx"
            await asyncio.to_thread(
                batch_job.result_file.save,
                filename,
                ContentFile(excel_bytes),
                save=True
            )
            
            logger.info(f"Generated result file for batch {batch_job.id}")
            
        except Exception as e:
            logger.error(f"Error generating result file: {e}")
            raise
    
    async def get_batch_status(self, batch_job_id: str) -> dict:
        """
        Get current status and statistics for a batch job.
        
        Args:
            batch_job_id: UUID of the batch job
        
        Returns:
            Dictionary with status information
        """
        batch_job = await asyncio.to_thread(
            BatchJob.objects.get, id=batch_job_id
        )
        
        # Get item counts by status
        items_by_status = await asyncio.to_thread(
            lambda: {
                status: batch_job.items.filter(status=status).count()
                for status in BatchItemStatus.values
            }
        )
        
        return {
            'id': str(batch_job.id),
            'filename': batch_job.filename,
            'status': batch_job.status,
            'total_items': batch_job.total_items,
            'completed_items': batch_job.completed_items,
            'failed_items': batch_job.failed_items,
            'pending_items': batch_job.pending_items_count,
            'progress_percentage': batch_job.progress_percentage,
            'items_by_status': items_by_status,
            'created_at': batch_job.created_at.isoformat(),
            'started_at': batch_job.started_at.isoformat() if batch_job.started_at else None,
            'completed_at': batch_job.completed_at.isoformat() if batch_job.completed_at else None,
            'has_result_file': bool(batch_job.result_file),
            'error_message': batch_job.error_message,
        }
    
    async def cancel_batch(self, batch_job_id: str):
        """
        Cancel a running batch job.
        
        Args:
            batch_job_id: UUID of the batch job
        """
        batch_job = await asyncio.to_thread(
            BatchJob.objects.get, id=batch_job_id
        )
        
        if batch_job.status == BatchJobStatus.PROCESSING:
            batch_job.status = BatchJobStatus.CANCELLED
            batch_job.completed_at = timezone.now()
            await asyncio.to_thread(
                batch_job.save,
                update_fields=['status', 'completed_at']
            )
            logger.info(f"Cancelled batch job {batch_job.id}")
