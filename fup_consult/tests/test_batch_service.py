"""
Tests for batch processing service.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from django.core.files.uploadedfile import SimpleUploadedFile

from fup_consult.services.batch_service import BatchProcessingService
from fup_consult.models import BatchJob, BatchItem, BatchJobStatus, BatchItemStatus


@pytest.mark.django_db
class TestBatchProcessingService:
    """Tests for BatchProcessingService."""
    
    @pytest.fixture
    def service(self):
        """Create batch processing service instance."""
        return BatchProcessingService(max_concurrent=2, max_retries=2)
    
    @pytest.fixture
    def test_excel_path(self):
        """Path to test Excel file."""
        return str(Path(__file__).parent.parent.parent / "test_batch_small.xlsx")
    
    @pytest.mark.asyncio
    async def test_create_batch_from_excel(self, service, test_excel_path):
        """Test creating batch job from Excel file."""
        batch_job = await service.create_batch_from_excel(
            test_excel_path,
            "test_batch_small.xlsx"
        )
        
        assert batch_job is not None
        assert batch_job.filename == "test_batch_small.xlsx"
        assert batch_job.status == BatchJobStatus.PENDING
        assert batch_job.total_items == 3  # We created 3 RUCs
        assert batch_job.completed_items == 0
        assert batch_job.failed_items == 0
        
        # Check items were created
        items = await asyncio.to_thread(
            lambda: list(batch_job.items.all())
        )
        assert len(items) == 3
        assert all(item.status == BatchItemStatus.PENDING for item in items)
    
    @pytest.mark.asyncio
    async def test_create_batch_invalid_file(self, service, tmp_path):
        """Test error handling for invalid Excel file."""
        # Create empty file
        invalid_file = tmp_path / "invalid.xlsx"
        invalid_file.touch()
        
        with pytest.raises(ValueError):
            await service.create_batch_from_excel(str(invalid_file), "invalid.xlsx")
    
    @pytest.mark.asyncio
    async def test_create_batch_no_rucs(self, service, tmp_path):
        """Test error handling for Excel with no valid RUCs."""
        import openpyxl
        
        # Create Excel with no RUCs
        wb = openpyxl.Workbook()
        ws = wb.active
        ws['A1'] = "RUC"
        # No data rows
        
        test_file = tmp_path / "empty.xlsx"
        wb.save(str(test_file))
        
        with pytest.raises(ValueError, match="No valid RUCs found"):
            await service.create_batch_from_excel(str(test_file), "empty.xlsx")
    
    @pytest.mark.asyncio
    async def test_get_batch_status(self, service):
        """Test getting batch status."""
        # Create a batch job manually
        batch_job = await asyncio.to_thread(
            BatchJob.objects.create,
            filename="test.xlsx",
            total_items=5,
            completed_items=2,
            failed_items=1,
            status=BatchJobStatus.PROCESSING
        )
        
        status = await service.get_batch_status(str(batch_job.id))
        
        assert status['id'] == str(batch_job.id)
        assert status['filename'] == "test.xlsx"
        assert status['status'] == BatchJobStatus.PROCESSING
        assert status['total_items'] == 5
        assert status['completed_items'] == 2
        assert status['failed_items'] == 1
        assert status['pending_items'] == 2
        assert status['progress_percentage'] == 40  # 2/5 * 100
    
    @pytest.mark.asyncio
    async def test_mark_started(self):
        """Test marking batch as started."""
        batch_job = await asyncio.to_thread(
            BatchJob.objects.create,
            filename="test.xlsx",
            total_items=1
        )
        
        await asyncio.to_thread(batch_job.mark_started)
        await asyncio.to_thread(batch_job.refresh_from_db)
        
        assert batch_job.status == BatchJobStatus.PROCESSING
        assert batch_job.started_at is not None
    
    @pytest.mark.asyncio
    async def test_mark_completed(self):
        """Test marking batch as completed."""
        batch_job = await asyncio.to_thread(
            BatchJob.objects.create,
            filename="test.xlsx",
            total_items=1,
            status=BatchJobStatus.PROCESSING
        )
        
        await asyncio.to_thread(batch_job.mark_completed)
        await asyncio.to_thread(batch_job.refresh_from_db)
        
        assert batch_job.status == BatchJobStatus.COMPLETED
        assert batch_job.completed_at is not None
    
    @pytest.mark.asyncio
    async def test_batch_item_retry_logic(self):
        """Test batch item retry logic."""
        batch_job = await asyncio.to_thread(
            BatchJob.objects.create,
            filename="test.xlsx",
            total_items=1
        )
        
        item = await asyncio.to_thread(
            BatchItem.objects.create,
            batch_job=batch_job,
            ruc="12345678901",
            max_retries=3
        )
        
        # First failure - should retry
        await asyncio.to_thread(item.mark_failed, "Error 1")
        await asyncio.to_thread(item.refresh_from_db)
        
        assert item.status == BatchItemStatus.RETRYING
        assert item.retry_count == 1
        assert item.can_retry()
        
        # Second failure - should retry
        await asyncio.to_thread(item.mark_failed, "Error 2")
        await asyncio.to_thread(item.refresh_from_db)
        
        assert item.status == BatchItemStatus.RETRYING
        assert item.retry_count == 2
        assert item.can_retry()
        
        # Third failure - should fail permanently
        await asyncio.to_thread(item.mark_failed, "Error 3")
        await asyncio.to_thread(item.refresh_from_db)
        
        assert item.status == BatchItemStatus.FAILED
        assert item.retry_count == 3
        assert not item.can_retry()
    
    @pytest.mark.asyncio
    async def test_batch_item_mark_completed(self):
        """Test marking batch item as completed."""
        batch_job = await asyncio.to_thread(
            BatchJob.objects.create,
            filename="test.xlsx",
            total_items=1
        )
        
        item = await asyncio.to_thread(
            BatchItem.objects.create,
            batch_job=batch_job,
            ruc="12345678901"
        )
        
        result_data = {
            'ruc': '12345678901',
            'razon_social': 'TEST COMPANY',
            'estado': 'ACTIVO'
        }
        
        await asyncio.to_thread(item.mark_completed, result_data)
        await asyncio.to_thread(item.refresh_from_db)
        await asyncio.to_thread(batch_job.refresh_from_db)
        
        assert item.status == BatchItemStatus.COMPLETED
        assert item.result_data == result_data
        assert item.processed_at is not None
        assert batch_job.completed_items == 1


@pytest.mark.django_db
class TestBatchModels:
    """Tests for batch models."""
    
    def test_batch_job_progress_percentage(self):
        """Test progress percentage calculation."""
        batch = BatchJob.objects.create(
            filename="test.xlsx",
            total_items=10,
            completed_items=3
        )
        
        assert batch.progress_percentage == 30
    
    def test_batch_job_progress_percentage_zero_items(self):
        """Test progress percentage with zero items."""
        batch = BatchJob.objects.create(
            filename="test.xlsx",
            total_items=0
        )
        
        assert batch.progress_percentage == 0
    
    def test_batch_job_pending_items_count(self):
        """Test pending items count calculation."""
        batch = BatchJob.objects.create(
            filename="test.xlsx",
            total_items=10,
            completed_items=3,
            failed_items=2
        )
        
        assert batch.pending_items_count == 5
    
    def test_batch_item_can_retry(self):
        """Test can_retry logic."""
        batch = BatchJob.objects.create(
            filename="test.xlsx",
            total_items=1
        )
        
        item = BatchItem.objects.create(
            batch_job=batch,
            ruc="12345678901",
            max_retries=3,
            retry_count=1,
            status=BatchItemStatus.RETRYING
        )
        
        assert item.can_retry()
        
        item.retry_count = 3
        item.status = BatchItemStatus.FAILED
        item.save()
        
        assert not item.can_retry()
