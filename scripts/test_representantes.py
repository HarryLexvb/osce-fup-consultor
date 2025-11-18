"""
Test script for SUNAT representantes scraping
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fup_consult.services.sunat_scraper import SUNATScraper

def test_scrape_representantes():
    """Test scraping representantes from SUNAT"""
    scraper = SUNATScraper()
    
    # Test with RUC 20508238143
    ruc = "20508238143"
    print(f"Testing SUNAT scraper with RUC: {ruc}")
    print("-" * 60)
    
    try:
        data = scraper.scrape_provider_data(ruc)
        
        print(f"[OK] Scraped successfully")
        print(f"\nRUC: {data.get('ruc')}")
        print(f"Razon Social: {data.get('razon_social')}")
        print(f"Tipo Contribuyente: {data.get('tipo_contribuyente')}")
        print(f"Estado: {data.get('estado')}")
        print(f"Condicion: {data.get('condicion')}")
        print(f"Domicilio: {data.get('domicilio')}")
        
        representantes = data.get('representantes', [])
        print(f"\n[OK] Found {len(representantes)} representantes:")
        for rep in representantes:
            print(f"  - {rep.get('nombre_completo')}")
            print(f"    Documento: {rep.get('tipo_documento')} - {rep.get('numero_documento')}")
            print(f"    Cargo: {rep.get('cargo')}")
            print()
        
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scrape_representantes()
