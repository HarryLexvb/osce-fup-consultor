"""
Script to create test Excel files with RUCs for batch processing testing.
"""

import openpyxl
from pathlib import Path

# Test RUCs (válidos)
test_rucs = [
    "20508238143",  # GEROSANCA E.I.R.L.
    "20506534713",  # UNLIMITED DESIGNS SAC
    "20572291449",  # CONSTRUCTORA E INVERSIONES LA FORTALEZA
    "20600553691",  # OSIRIS EVENTOS Y PRODUCCIONES
    "20573004427",  # CONTRATISTAS & CONSULTORES CIENFUEGOS
    "20600539362",  # NAKAMA SOLUCIONES
    "20100008662",  # RANSA COMERCIAL S.A.
    "20100049776",  # ALICORP S.A.A.
    "20100070970",  # GLORIA S.A.
    "20100123009",  # TELEFONICA DEL PERU S.A.A.
]

def create_test_file(num_rucs: int, filename: str):
    """Create test Excel file with specified number of RUCs."""
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "RUCs"
    
    # Add header
    ws.append(["RUC"])
    
    # Add RUCs (repeat test RUCs if needed)
    for i in range(num_rucs):
        ruc = test_rucs[i % len(test_rucs)]
        ws.append([ruc])
    
    # Save file
    output_dir = Path(__file__).parent / "test_files"
    output_dir.mkdir(exist_ok=True)
    
    filepath = output_dir / filename
    wb.save(filepath)
    print(f"✓ Created: {filepath} ({num_rucs} RUCs)")
    return filepath

if __name__ == "__main__":
    # Create test files with different sizes
    print("Creating test files...")
    print()
    
    # Small dataset (Excel standard)
    create_test_file(10, "test_10_rucs.xlsx")
    
    # Medium dataset (Excel optimized)
    create_test_file(100, "test_100_rucs.xlsx")
    
    # Large dataset (CSV)
    # Note: 24k RUCs would take ~2-4 hours to process
    # For quick testing, use smaller sizes
    create_test_file(500, "test_500_rucs.xlsx")
    
    print()
    print("✓ All test files created in 'test_files' directory")
    print()
    print("Usage:")
    print("1. Navigate to http://localhost:8000")
    print("2. Click on 'Carga Masiva' tab")
    print("3. Upload one of the test files")
    print("4. Wait for processing to complete")
    print("5. Download the result file")
