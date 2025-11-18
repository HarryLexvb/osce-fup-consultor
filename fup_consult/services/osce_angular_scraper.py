"""
OSCE Angular SPA Scraper
Extrae datos completos de https://apps.osce.gob.pe/perfilprov-ui/ficha/{RUC}
"""

import logging
import time
from typing import Dict, Any, List

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class OSCEAngularScraperException(Exception):
    """Exception raised when OSCE Angular scraping fails."""
    pass


class OSCEAngularScraper:
    """Scraper for OSCE Angular SPA with complete provider data."""

    def __init__(self) -> None:
        """Initialize OSCE Angular scraper."""
        self.base_url = "https://apps.osce.gob.pe/perfilprov-ui/ficha"

    def _get_driver(self) -> webdriver.Chrome:
        """Get configured Chrome driver."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
        
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape_provider_data(self, ruc: str) -> Dict[str, Any]:
        """
        Scrape complete provider data from OSCE Angular SPA.

        Args:
            ruc: Provider's RUC number

        Returns:
            Dictionary with complete provider data including socios, representantes, organos

        Raises:
            OSCEAngularScraperException: If scraping fails
        """
        driver = None
        try:
            logger.info(f"Starting OSCE Angular scraping for RUC: {ruc}")
            driver = self._get_driver()
            
            url = f"{self.base_url}/{ruc}"
            driver.get(url)
            
            # Wait for Angular to render (increased timeout for SPA)
            logger.info("Waiting for Angular app to load...")
            time.sleep(10)  # Increased from 8 to 10 seconds
            
            # Wait for specific content to appear
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: "QUANTUM" in d.find_element(By.TAG_NAME, "body").text or
                              "Conformación" in d.find_element(By.TAG_NAME, "body").text
                )
                logger.info("Angular content loaded")
            except Exception as e:
                logger.warning(f"Timeout waiting for Angular content: {e}")
            
            # Additional wait for dynamic content
            time.sleep(3)
            
            # Get page text for debugging
            page_text = driver.find_element(By.TAG_NAME, "body").text
            logger.info(f"Page text length: {len(page_text)} characters")
            
            # Save to file for debugging
            with open("osce_angular_debug.txt", "w", encoding="utf-8") as f:
                f.write(page_text)
            
            # Extract data
            data = {
                "socios": self._extract_socios(driver),
                "representantes": self._extract_representantes(driver),
                "organos": self._extract_organos(driver)
            }
            
            logger.info(f"Successfully scraped OSCE Angular data: "
                       f"{len(data['socios'])} socios, "
                       f"{len(data['representantes'])} representantes, "
                       f"{len(data['organos'])} órganos")
            
            return data
            
        except Exception as e:
            error_msg = f"Failed to scrape OSCE Angular for {ruc}: {str(e)}"
            logger.error(error_msg)
            raise OSCEAngularScraperException(error_msg) from e
            
        finally:
            if driver:
                driver.quit()

    def _extract_socios(self, driver: webdriver.Chrome) -> List[Dict[str, str]]:
        """Extract socios/accionistas from the page."""
        socios = []
        
        try:
            # Look for "Conformación Societaria" or "Socios/Accionistas" section
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            if "Conformación Societaria" not in page_text and "Socios/Accionistas" not in page_text:
                logger.info("No socios section found on page")
                return socios
            
            # Try to find all text elements that look like names with documents
            # Pattern: NAME\nTipo de Documento: P. - AAD877402
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
                            # Format: "Tipo de Documento: P. - AAD877402"
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
                            
                            i += 2  # Skip the document line
                            continue
                
                i += 1
            
            logger.info(f"Extracted {len(socios)} socios")
            
        except Exception as e:
            logger.warning(f"Error extracting socios: {e}")
        
        return socios

    def _extract_representantes(self, driver: webdriver.Chrome) -> List[Dict[str, str]]:
        """Extract representantes legales from the page."""
        representantes = []
        
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
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

    def _extract_organos(self, driver: webdriver.Chrome) -> List[Dict[str, str]]:
        """Extract órganos de administración from the page."""
        organos = []
        
        try:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
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
