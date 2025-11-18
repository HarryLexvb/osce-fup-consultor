"""
OSCE Angular SPA Scraper using Camoufox (anti-detection)
Extrae datos completos de https://apps.osce.gob.pe/perfilprov-ui/ficha/{RUC}
"""

import logging
import asyncio
from typing import Dict, Any, List

from camoufox.sync_api import Camoufox

logger = logging.getLogger(__name__)


class OSCECamoufoxScraperException(Exception):
    """Exception raised when OSCE Camoufox scraping fails."""
    pass


class OSCECamoufoxScraper:
    """Scraper for OSCE Angular SPA using Camoufox for anti-detection."""

    def __init__(self) -> None:
        """Initialize OSCE Camoufox scraper."""
        self.base_url = "https://apps.osce.gob.pe/perfilprov-ui/ficha"

    def scrape_provider_data(self, ruc: str) -> Dict[str, Any]:
        """
        Scrape complete provider data from OSCE Angular SPA using Camoufox.

        Args:
            ruc: Provider's RUC number

        Returns:
            Dictionary with complete provider data including socios, representantes, organos

        Raises:
            OSCECamoufoxScraperException: If scraping fails
        """
        try:
            logger.info(f"Starting OSCE Camoufox scraping for RUC: {ruc}")
            
            with Camoufox(headless=True, humanize=True) as browser:
                page = browser.new_page()
                
                url = f"{self.base_url}/{ruc}"
                logger.info(f"Navigating to: {url}")
                page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Wait for Angular to load content
                logger.info("Waiting for Angular content to load...")
                page.wait_for_timeout(8000)  # 8 seconds for Angular
                
                # Try to wait for specific content
                try:
                    page.wait_for_selector("text=QUANTUM", timeout=10000)
                    logger.info("Content loaded successfully")
                except Exception as e:
                    logger.warning(f"Timeout waiting for content: {e}")
                
                # Additional wait for dynamic content
                page.wait_for_timeout(3000)
                
                # Get page text
                page_text = page.inner_text("body")
                logger.info(f"Page text length: {len(page_text)} characters")
                
                # Save for debugging
                with open("osce_camoufox_debug.txt", "w", encoding="utf-8") as f:
                    f.write(page_text)
                
                # Try to find and click on collapsible sections
                try:
                    # Look for elements that might be collapsed
                    # Common patterns: buttons, spans, divs with click handlers
                    logger.info("Looking for collapsible sections...")
                    
                    # Try to find "Conformación Societaria" section
                    conformacion_elements = page.locator("text=/Conformación Societaria/i").all()
                    if conformacion_elements:
                        logger.info(f"Found {len(conformacion_elements)} conformación elements")
                        for elem in conformacion_elements:
                            try:
                                elem.click(timeout=2000)
                                page.wait_for_timeout(1000)
                            except:
                                pass
                    
                    # Try to find "Representantes" section
                    rep_elements = page.locator("text=/Representantes/i").all()
                    if rep_elements:
                        logger.info(f"Found {len(rep_elements)} representantes elements")
                        for elem in rep_elements:
                            try:
                                elem.click(timeout=2000)
                                page.wait_for_timeout(1000)
                            except:
                                pass
                    
                    # Try to find "Órganos" section
                    organos_elements = page.locator("text=/Órganos de Administración/i").all()
                    if organos_elements:
                        logger.info(f"Found {len(organos_elements)} órganos elements")
                        for elem in organos_elements:
                            try:
                                elem.click(timeout=2000)
                                page.wait_for_timeout(1000)
                            except:
                                pass
                    
                    # Get updated page text after clicks
                    page_text = page.inner_text("body")
                    logger.info(f"Updated page text length: {len(page_text)} characters")
                    
                    # Save updated text
                    with open("osce_camoufox_after_clicks.txt", "w", encoding="utf-8") as f:
                        f.write(page_text)
                    
                except Exception as e:
                    logger.warning(f"Error clicking sections: {e}")
                
                # Extract data
                data = {
                    "socios": self._extract_socios(page_text),
                    "representantes": self._extract_representantes(page_text),
                    "organos": self._extract_organos(page_text)
                }
                
                logger.info(f"Successfully scraped OSCE Camoufox data: "
                           f"{len(data['socios'])} socios, "
                           f"{len(data['representantes'])} representantes, "
                           f"{len(data['organos'])} órganos")
                
                return data
                
        except Exception as e:
            error_msg = f"Failed to scrape OSCE Camoufox for {ruc}: {str(e)}"
            logger.error(error_msg)
            raise OSCECamoufoxScraperException(error_msg) from e

    def _extract_socios(self, page_text: str) -> List[Dict[str, str]]:
        """Extract socios/accionistas from the page text."""
        socios = []
        
        try:
            if "Conformación Societaria" not in page_text and "Socios/Accionistas" not in page_text:
                logger.info("No socios section found on page")
                return socios
            
            lines = page_text.split('\n')
            
            i = 0
            in_socios_section = False
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Detect when we enter socios section
                if "Socios/Accionistas" in line or "Conformación Societaria" in line:
                    in_socios_section = True
                    i += 1
                    continue
                
                # Exit socios section when we hit another section
                if in_socios_section and ("Representantes" in line or "Órganos" in line or "Experiencia" in line):
                    break
                
                # If we're in socios section and line looks like a name
                if in_socios_section and line and not line.startswith("Tipo de"):
                    # Check if next line has document info
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if "Tipo de Documento:" in next_line:
                            # Extract document type and number
                            doc_parts = next_line.replace("Tipo de Documento:", "").strip()
                            
                            tipo_doc = ""
                            num_doc = ""
                            
                            if " - " in doc_parts:
                                parts = doc_parts.split(" - ")
                                tipo_doc = parts[0].strip()
                                num_doc = parts[1].strip() if len(parts) > 1 else ""
                            
                            socios.append({
                                "nombre_completo": line,
                                "tipo_documento": tipo_doc,
                                "numero_documento": num_doc,
                                "porcentaje_participacion": None
                            })
                            
                            i += 2
                            continue
                
                i += 1
            
            logger.info(f"Extracted {len(socios)} socios")
            
        except Exception as e:
            logger.warning(f"Error extracting socios: {e}")
        
        return socios

    def _extract_representantes(self, page_text: str) -> List[Dict[str, str]]:
        """Extract representantes legales from the page text."""
        representantes = []
        
        try:
            if "Representantes" not in page_text:
                logger.info("No representantes section found on page")
                return representantes
            
            lines = page_text.split('\n')
            
            i = 0
            in_rep_section = False
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Detect when we enter representantes section
                if "Representantes" in line and "Socios" not in line:
                    in_rep_section = True
                    i += 1
                    continue
                
                # Exit section
                if in_rep_section and ("Órganos" in line or "Experiencia" in line or "Proveedores sancionados" in line):
                    break
                
                # If we're in representantes section and line looks like a name
                if in_rep_section and line and not line.startswith("Tipo de"):
                    # Check if next line has document info
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if "Tipo de Documento:" in next_line:
                            doc_parts = next_line.replace("Tipo de Documento:", "").strip()
                            
                            tipo_doc = ""
                            num_doc = ""
                            
                            if " - " in doc_parts:
                                parts = doc_parts.split(" - ")
                                tipo_doc = parts[0].strip()
                                num_doc = parts[1].strip() if len(parts) > 1 else ""
                            
                            representantes.append({
                                "nombre_completo": line,
                                "tipo_documento": tipo_doc,
                                "numero_documento": num_doc,
                                "cargo": "REPRESENTANTE LEGAL"
                            })
                            
                            i += 2
                            continue
                
                i += 1
            
            logger.info(f"Extracted {len(representantes)} representantes")
            
        except Exception as e:
            logger.warning(f"Error extracting representantes: {e}")
        
        return representantes

    def _extract_organos(self, page_text: str) -> List[Dict[str, str]]:
        """Extract órganos de administración from the page text."""
        organos = []
        
        try:
            if "Órganos de Administración" not in page_text:
                logger.info("No órganos section found on page")
                return organos
            
            lines = page_text.split('\n')
            
            i = 0
            in_organos_section = False
            current_nombre = None
            
            while i < len(lines):
                line = lines[i].strip()
                
                # Detect section start
                if "Órganos de Administración" in line:
                    in_organos_section = True
                    i += 1
                    continue
                
                # Exit section
                if in_organos_section and ("Experiencia" in line or "Proveedores sancionados" in line):
                    break
                
                # Extract data
                if in_organos_section and line:
                    if not line.startswith("Tipo de") and not line.startswith("CARGO:"):
                        # This is likely a name
                        current_nombre = line
                    elif line.startswith("Tipo de Documento:") and current_nombre:
                        # Get document info
                        doc_parts = line.replace("Tipo de Documento:", "").strip()
                        
                        tipo_doc = ""
                        num_doc = ""
                        
                        if " - " in doc_parts:
                            parts = doc_parts.split(" - ")
                            tipo_doc = parts[0].strip()
                            num_doc = parts[1].strip() if len(parts) > 1 else ""
                        
                        # Look for cargo in next line
                        cargo = "MIEMBRO"
                        if i + 1 < len(lines):
                            next_line = lines[i + 1].strip()
                            if "CARGO:" in next_line:
                                cargo = next_line.replace("CARGO:", "").strip()
                        
                        organos.append({
                            "nombre_completo": current_nombre,
                            "tipo_documento": tipo_doc,
                            "numero_documento": num_doc,
                            "cargo": cargo
                        })
                        
                        current_nombre = None
                
                i += 1
            
            logger.info(f"Extracted {len(organos)} órganos")
            
        except Exception as e:
            logger.warning(f"Error extracting órganos: {e}")
        
        return organos
