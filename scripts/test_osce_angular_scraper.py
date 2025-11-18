"""
Test OSCE Angular scraper
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "osce_fup_portal.settings")

from fup_consult.services.osce_angular_scraper import OSCEAngularScraper

def test_osce_angular():
    """Test OSCE Angular scraper"""
    scraper = OSCEAngularScraper()
    
    ruc = "20508238143"
    print(f"Testing OSCE Angular scraper with RUC: {ruc}")
    print("-" * 60)
    
    try:
        data = scraper.scrape_provider_data(ruc)
        
        print(f"[OK] Scraped successfully\n")
        
        print(f"=== SOCIOS ({len(data['socios'])}) ===")
        for socio in data['socios']:
            print(f"  - {socio['nombre_completo']}")
            print(f"    Doc: {socio['tipo_documento']} - {socio['numero_documento']}")
        
        print(f"\n=== REPRESENTANTES ({len(data['representantes'])}) ===")
        for rep in data['representantes']:
            print(f"  - {rep['nombre_completo']}")
            print(f"    Doc: {rep['tipo_documento']} - {rep['numero_documento']}")
            print(f"    Cargo: {rep['cargo']}")
        
        print(f"\n=== ORGANOS ({len(data['organos'])}) ===")
        for org in data['organos']:
            print(f"  - {org['nombre_completo']}")
            print(f"    Doc: {org['tipo_documento']} - {org['numero_documento']}")
            print(f"    Cargo: {org['cargo']}")
        
        if len(data['socios']) == 0 and len(data['representantes']) == 0 and len(data['organos']) == 0:
            print("\n[WARNING] No data extracted. Check osce_angular_debug.txt for page content")
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_osce_angular()
