"""
CSV exporter for batch processing results.

This module provides functionality to export multiple provider data
into CSV format, optimized for large datasets (10k+ records).
CSV files are lightweight, Excel-compatible, and handle large volumes efficiently.
"""

import csv
import io
import logging
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class CSVBatchExporter:
    """Exports batch processing results to CSV format."""
    
    def __init__(self) -> None:
        """Initialize CSV batch exporter."""
        pass
    
    def generate_batch_csv(
        self,
        results: List[Dict[str, Any]],
        original_filename: str
    ) -> bytes:
        """
        Generate consolidated CSV file from batch results.
        
        Args:
            results: List of provider data dictionaries
            original_filename: Original input filename for reference
        
        Returns:
            CSV file as bytes (UTF-8 with BOM for Excel compatibility)
        """
        output = io.StringIO()
        
        # Write metadata header
        output.write(f"# REPORTE DE PROCESAMIENTO BATCH\n")
        output.write(f"# Archivo Original: {original_filename}\n")
        output.write(f"# Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        output.write(f"# Total RUCs: {len(results)}\n")
        output.write(f"#\n")
        
        # Main consolidated data
        output.write("=== DATOS CONSOLIDADOS ===\n")
        self._write_consolidated_data(output, results)
        
        # Socios detailed data
        output.write("\n\n=== SOCIOS DETALLADOS ===\n")
        self._write_socios_detail(output, results)
        
        # Representantes detailed data
        output.write("\n\n=== REPRESENTANTES DETALLADOS ===\n")
        self._write_representantes_detail(output, results)
        
        # Organos detailed data
        output.write("\n\n=== ORGANOS DE ADMINISTRACION ===\n")
        self._write_organos_detail(output, results)
        
        # Convert to bytes with UTF-8 BOM for Excel compatibility
        csv_bytes = '\ufeff' + output.getvalue()
        return csv_bytes.encode('utf-8')
    
    def _write_consolidated_data(
        self,
        output: io.StringIO,
        results: List[Dict[str, Any]]
    ) -> None:
        """Write consolidated data section."""
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = [
            "RUC",
            "Razón Social",
            "Estado",
            "Condición",
            "Tipo de Contribuyente",
            "Domicilio",
            "Departamento",
            "Provincia",
            "Distrito",
            "Teléfonos",
            "Emails",
            "N° Socios",
            "N° Representantes",
            "N° Órganos Administración"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for result in results:
            # Safely get values with defaults
            telefonos = result.get('telefonos', [])
            emails = result.get('emails', [])
            
            row = [
                result.get('ruc', ''),
                result.get('razon_social', ''),
                result.get('estado', ''),
                result.get('condicion', ''),
                result.get('tipo_contribuyente', ''),
                result.get('domicilio', ''),
                result.get('departamento', ''),
                result.get('provincia', ''),
                result.get('distrito', ''),
                ', '.join(telefonos) if telefonos else '',
                ', '.join(emails) if emails else '',
                result.get('num_socios', 0),
                result.get('num_representantes', 0),
                result.get('num_organos', 0)
            ]
            writer.writerow(row)
    
    def _write_socios_detail(
        self,
        output: io.StringIO,
        results: List[Dict[str, Any]]
    ) -> None:
        """Write socios detailed section."""
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = [
            "RUC Empresa",
            "Razón Social Empresa",
            "Nombre Completo Socio",
            "Tipo Doc",
            "Descripción Documento",
            "Número Documento",
            "Participación %",
            "Número de Acciones",
            "Fecha Ingreso"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for result in results:
            ruc = result.get('ruc', '')
            razon_social = result.get('razon_social', '')
            socios = result.get('socios', [])
            
            if not socios:
                # Add a row indicating no socios
                row = [ruc, razon_social, 'Sin socios registrados', '', '', '', '', '', '']
                writer.writerow(row)
            else:
                for socio in socios:
                    row = [
                        ruc,
                        razon_social,
                        socio.get('nombre_completo', ''),
                        socio.get('tipo_documento', ''),
                        socio.get('desc_tipo_documento', ''),
                        socio.get('numero_documento', ''),
                        socio.get('porcentaje_participacion', ''),
                        socio.get('numero_acciones', ''),
                        socio.get('fecha_ingreso', '')
                    ]
                    writer.writerow(row)
    
    def _write_representantes_detail(
        self,
        output: io.StringIO,
        results: List[Dict[str, Any]]
    ) -> None:
        """Write representantes detailed section."""
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = [
            "RUC Empresa",
            "Razón Social Empresa",
            "Nombre Completo",
            "Tipo Doc",
            "Descripción Documento",
            "Número Documento",
            "Cargo",
            "Fecha Desde"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for result in results:
            ruc = result.get('ruc', '')
            razon_social = result.get('razon_social', '')
            representantes = result.get('representantes', [])
            
            if not representantes:
                # Add a row indicating no representantes
                row = [ruc, razon_social, 'Sin representantes registrados', '', '', '', '', '']
                writer.writerow(row)
            else:
                for rep in representantes:
                    row = [
                        ruc,
                        razon_social,
                        rep.get('nombre_completo', ''),
                        rep.get('tipo_documento', ''),
                        rep.get('desc_tipo_documento', ''),
                        rep.get('numero_documento', ''),
                        rep.get('cargo', ''),
                        rep.get('fecha_desde', '')
                    ]
                    writer.writerow(row)
    
    def _write_organos_detail(
        self,
        output: io.StringIO,
        results: List[Dict[str, Any]]
    ) -> None:
        """Write organos de administracion detailed section."""
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write headers
        headers = [
            "RUC Empresa",
            "Razón Social Empresa",
            "Nombre Completo",
            "Tipo Doc",
            "Descripción Documento",
            "Número Documento",
            "Tipo de Órgano",
            "Cargo",
            "Fecha Desde"
        ]
        writer.writerow(headers)
        
        # Write data rows
        for result in results:
            ruc = result.get('ruc', '')
            razon_social = result.get('razon_social', '')
            organos = result.get('organos_administracion', [])
            
            if not organos:
                # Add a row indicating no organos
                row = [ruc, razon_social, 'Sin órganos de administración registrados', '', '', '', '', '', '']
                writer.writerow(row)
            else:
                for org in organos:
                    row = [
                        ruc,
                        razon_social,
                        org.get('nombre_completo', ''),
                        org.get('tipo_documento', ''),
                        org.get('desc_tipo_documento', ''),
                        org.get('numero_documento', ''),
                        org.get('tipo_organo', ''),
                        org.get('cargo', ''),
                        org.get('fecha_desde', '')
                    ]
                    writer.writerow(row)
