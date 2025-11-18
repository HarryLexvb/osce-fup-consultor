"""
Test script for OSCE Camoufox Scraper
"""

import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from fup_consult.services.osce_camoufox_scraper import OSCECamoufoxScraper

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Test OSCE Camoufox scraper with RUC 20508238143."""
    
    ruc = "20508238143"
    print(f"\n{'='*60}")
    print(f"Testing OSCE Camoufox Scraper with RUC: {ruc}")
    print(f"{'='*60}\n")
    
    scraper = OSCECamoufoxScraper()
    
    try:
        data = scraper.scrape_provider_data(ruc)
        
        print(f"\n✅ Scraping completed successfully!")
        print(f"\n{'='*60}")
        print("Results:")
        print(f"{'='*60}")
        
        print(f"\nSocios/Accionistas: {len(data['socios'])}")
        for socio in data['socios']:
            print(f"  - {socio['nombre_completo']} ({socio['tipo_documento']} {socio['numero_documento']})")
        
        print(f"\nRepresentantes Legales: {len(data['representantes'])}")
        for rep in data['representantes']:
            print(f"  - {rep['nombre_completo']} ({rep['tipo_documento']} {rep['numero_documento']})")
        
        print(f"\nÓrganos de Administración: {len(data['organos'])}")
        for org in data['organos']:
            print(f"  - {org['nombre_completo']} - {org['cargo']} ({org['tipo_documento']} {org['numero_documento']})")
        
        print(f"\n{'='*60}")
        print("\nDebug files saved:")
        print("  - osce_camoufox_debug.txt (initial page load)")
        print("  - osce_camoufox_after_clicks.txt (after clicking sections)")
        print(f"{'='*60}\n")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
