"""
Test different RUCs to find one with complete data
"""

import logging
from camoufox.sync_api import Camoufox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try different RUCs - big companies that should have complete data
test_rucs = [
    "20100070970",  # Telefónica del Perú
    "20100047218",  # Banco de Crédito del Perú
    "20331066703",  # Odebrecht (now Novonor)
    "20505670443",  # Graña y Montero
    "20508238143",  # Original RUC
]

def test_ruc(ruc):
    """Test a RUC to see if it has socios/representantes/organos data."""
    
    url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
    
    logger.info(f"\n{'='*60}")
    logger.info(f"Testing RUC: {ruc}")
    logger.info(f"{'='*60}")
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(10000)
        
        text = page.inner_text("body")
        
        has_socios = "Conformación Societaria" in text or "Socios/Accionistas" in text
        has_reps = "Representantes Legales" in text or "Representantes" in text
        has_organos = "Órganos de Administración" in text
        
        logger.info(f"Has Socios: {has_socios}")
        logger.info(f"Has Representantes: {has_reps}")
        logger.info(f"Has Órganos: {has_organos}")
        
        if has_socios or has_reps or has_organos:
            logger.info(f"✅ RUC {ruc} HAS DATA!")
            
            # Save the page
            with open(f"osce_ruc_{ruc}_text.txt", "w", encoding="utf-8") as f:
                f.write(text)
            
            html = page.content()
            with open(f"osce_ruc_{ruc}_html.html", "w", encoding="utf-8") as f:
                f.write(html)
            
            return True
        else:
            logger.info(f"❌ RUC {ruc} has no detailed data")
            return False

def main():
    found_rucs = []
    
    for ruc in test_rucs:
        if test_ruc(ruc):
            found_rucs.append(ruc)
    
    logger.info(f"\n\n{'='*60}")
    logger.info(f"SUMMARY")
    logger.info(f"{'='*60}")
    logger.info(f"Total RUCs tested: {len(test_rucs)}")
    logger.info(f"RUCs with data: {len(found_rucs)}")
    
    if found_rucs:
        logger.info(f"\nRUCs with socios/representantes/organos:")
        for ruc in found_rucs:
            logger.info(f"  - {ruc}")
    else:
        logger.info("\n❌ NO RUCs found with detailed data!")
        logger.info("This suggests the OSCE Angular page does NOT show this data,")
        logger.info("or it requires special authentication/conditions.")

if __name__ == "__main__":
    main()
