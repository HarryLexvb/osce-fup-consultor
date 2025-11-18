"""
HTML structure investigation for OSCE Angular SPA
"""

import logging
from camoufox.sync_api import Camoufox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def investigate_html():
    """Investigate the HTML structure of OSCE Angular page."""
    
    ruc = "20508238143"
    url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
    
    with Camoufox(headless=False, humanize=True) as browser:  # headless=False to see what's happening
        page = browser.new_page()
        
        logger.info(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Wait for content
        page.wait_for_timeout(10000)
        
        # Get full HTML
        html = page.content()
        
        # Save HTML
        with open("osce_full_html.html", "w", encoding="utf-8") as f:
            f.write(html)
        
        logger.info(f"HTML saved to osce_full_html.html ({len(html)} bytes)")
        
        # Look for specific elements
        logger.info("\n=== Looking for key elements ===")
        
        # Try to find tabs or accordions
        tabs = page.locator("mat-tab, .mat-tab, [role='tab']").all()
        logger.info(f"Found {len(tabs)} tabs")
        
        accordions = page.locator("mat-expansion-panel, .mat-expansion-panel, .accordion").all()
        logger.info(f"Found {len(accordions)} accordions")
        
        # Try to find buttons
        buttons = page.locator("button").all()
        logger.info(f"Found {len(buttons)} buttons")
        
        # Try to find any element with "Conformación" text
        conformacion = page.locator("text=/Conformación/i").all()
        logger.info(f"Found {len(conformacion)} elements with 'Conformación'")
        
        # Try to find any element with "Representantes" text
        representantes = page.locator("text=/Representantes/i").all()
        logger.info(f"Found {len(representantes)} elements with 'Representantes'")
        
        # Try to find any element with "Órganos" text
        organos = page.locator("text=/Órganos/i").all()
        logger.info(f"Found {len(organos)} elements with 'Órganos'")
        
        # Wait for user to inspect
        logger.info("\nBrowser will stay open for 30 seconds for manual inspection...")
        page.wait_for_timeout(30000)

if __name__ == "__main__":
    investigate_html()
