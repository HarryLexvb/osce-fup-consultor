"""
SUNAT Scraper Service
Obtiene datos fiscales de SUNAT mediante web scraping
"""

import logging
import re
from typing import Dict, Any, Optional

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

logger = logging.getLogger(__name__)


class SUNATScraperException(Exception):
    """Exception raised when SUNAT scraping fails."""

    pass


class SUNATScraper:
    """Scraper for SUNAT public consultation portal."""

    def __init__(self) -> None:
        """Initialize SUNAT scraper."""
        self.base_url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"

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
        Scrape provider data from SUNAT including representantes.

        Args:
            ruc: Provider's RUC number

        Returns:
            Dictionary with SUNAT data including representantes

        Raises:
            SUNATScraperException: If scraping fails
        """
        driver = None
        try:
            logger.info(f"Starting SUNAT scraping for RUC: {ruc}")
            driver = self._get_driver()
            
            driver.get(self.base_url)
            time.sleep(2)
            
            # Fill RUC input
            ruc_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtRuc"))
            )
            ruc_input.clear()
            ruc_input.send_keys(ruc)
            
            # Click search button
            search_button = driver.find_element(By.ID, "btnAceptar")
            search_button.click()
            
            # Wait for results
            time.sleep(3)
            
            # Get page text
            page_text = driver.find_element(By.TAG_NAME, "body").text
            
            # Parse main data (including inline representantes if present)
            data = self._parse_sunat_data(page_text, ruc)
            
            # If no representantes found in main page, try clicking the link
            if not data.get("representantes"):
                # Try to get representantes from separate page
                try:
                    # Look for "Representante(s) Legal(es)" link
                    representantes_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Representante")
                    
                    if representantes_links:
                        logger.info(f"Found Representantes link, clicking...")
                        representantes_links[0].click()
                        time.sleep(3)
                        
                        # Check if there's an iframe
                        iframes = driver.find_elements(By.TAG_NAME, "iframe")
                        if iframes:
                            logger.info(f"Found {len(iframes)} iframes, switching to first iframe")
                            driver.switch_to.frame(iframes[0])
                            time.sleep(2)
                        
                        # Try to get table directly
                        try:
                            tables = driver.find_elements(By.TAG_NAME, "table")
                            logger.info(f"Found {len(tables)} tables")
                            
                            # Parse tables for representantes
                            representantes = []
                            for table in tables:
                                table_text = table.text
                                logger.info(f"Table text: {table_text[:200]}")
                                if "Nombre" in table_text or "Doc." in table_text or "Cargo" in table_text:
                                    # This looks like a representantes table
                                    rows = table.find_elements(By.TAG_NAME, "tr")
                                    for row in rows[1:]:  # Skip header
                                        cells = row.find_elements(By.TAG_NAME, "td")
                                        if len(cells) >= 3:
                                            nombre = cells[0].text.strip()
                                            doc_info = cells[1].text.strip()
                                            cargo = cells[2].text.strip() if len(cells) > 2 else ""
                                            
                                            # Parse doc_info (format: "D.N.I. - 07329245")
                                            tipo_doc = ""
                                            num_doc = ""
                                            if " - " in doc_info:
                                                parts = doc_info.split(" - ")
                                                tipo_doc = parts[0].strip()
                                                num_doc = parts[1].strip() if len(parts) > 1 else ""
                                            
                                            if nombre and num_doc:
                                                representantes.append({
                                                    "nombre_completo": nombre,
                                                    "tipo_documento": tipo_doc,
                                                    "numero_documento": num_doc,
                                                    "cargo": cargo or "REPRESENTANTE LEGAL"
                                                })
                            
                            data["representantes"] = representantes
                            
                        except Exception as table_error:
                            logger.warning(f"Could not parse tables: {table_error}")
                            # Fall back to text parsing
                            rep_page_text = driver.find_element(By.TAG_NAME, "body").text
                            logger.info(f"Representantes page text length: {len(rep_page_text)}")
                            representantes = self._parse_representantes(rep_page_text)
                            data["representantes"] = representantes
                        
                        # Switch back if we switched to iframe
                        if iframes:
                            driver.switch_to.default_content()
                        
                        logger.info(f"Successfully scraped {len(data.get('representantes', []))} representantes")
                    else:
                        logger.info("No Representantes link found")
                        data["representantes"] = []
                        
                except Exception as e:
                    logger.warning(f"Could not scrape representantes from link: {e}")
                    if "representantes" not in data:
                        data["representantes"] = []
            
            logger.info(f"Successfully scraped SUNAT data for {ruc}")
            return data
            
        except Exception as e:
            error_msg = f"Failed to scrape SUNAT for {ruc}: {str(e)}"
            logger.error(error_msg)
            raise SUNATScraperException(error_msg) from e
            
        finally:
            if driver:
                driver.quit()

    def _parse_sunat_data(self, page_text: str, ruc: str) -> Dict[str, Any]:
        """
        Parse SUNAT page text to extract structured data.

        Args:
            page_text: Full page text from SUNAT
            ruc: RUC number

        Returns:
            Dictionary with parsed data
        """
        data = {
            "ruc": ruc,
            "razon_social": None,
            "estado": None,
            "condicion": None,
            "tipo_contribuyente": None,
            "domicilio": None,
            "departamento": None,
            "provincia": None,
            "distrito": None,
        }
        
        lines = page_text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            
            if "Número de RUC:" in line and i + 1 < len(lines):
                # Format: "20508238143 - QUANTUM ANDES S.A.C."
                next_line = lines[i + 1].strip()
                if " - " in next_line:
                    data["razon_social"] = next_line.split(" - ", 1)[1]
            
            elif "Tipo Contribuyente:" in line and i + 1 < len(lines):
                data["tipo_contribuyente"] = lines[i + 1].strip()
            
            elif "Estado del Contribuyente:" in line and i + 1 < len(lines):
                data["estado"] = lines[i + 1].strip()
            
            elif "Condición del Contribuyente:" in line and i + 1 < len(lines):
                data["condicion"] = lines[i + 1].strip()
            
            elif "Domicilio Fiscal:" in line and i + 1 < len(lines):
                domicilio_line = lines[i + 1].strip()
                data["domicilio"] = domicilio_line
                
                # Extract departamento/provincia/distrito
                # Format: "... LIMA - LIMA - SAN ISIDRO"
                match = re.search(r'([A-Z\s]+)\s+-\s+([A-Z\s]+)\s+-\s+([A-Z\s]+)$', domicilio_line)
                if match:
                    data["departamento"] = match.group(1).strip()
                    data["provincia"] = match.group(2).strip()
                    data["distrito"] = match.group(3).strip()
        
        return data
    
    def _parse_representantes(self, page_text: str) -> list:
        """
        Parse representantes from SUNAT representantes page.
        
        Args:
            page_text: Raw text from SUNAT representantes page
            
        Returns:
            List of representante dictionaries
        """
        from typing import List
        representantes = []
        
        try:
            # Common patterns in SUNAT representantes page:
            # MURAKAMI MOROYA BRUNO D.N.I. - 07329245 GERENTE GENERAL
            # DAMONTE FERNANDO JOSE P. - AAD47954 GERENTE
            
            # Split by lines
            lines = page_text.split("\n")
            
            # Look for patterns with documento followed by cargo
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Skip empty lines and headers
                if not line or "Nro. Doc." in line or "Nombre" in line:
                    continue
                
                # Pattern: NAME DOC_TYPE - DOC_NUMBER CARGO
                # Try to match lines with documento patterns
                if " - " in line and any(doc_type in line.upper() for doc_type in ["D.N.I", "DNI", "P.", "C.E.", "PASAPORTE"]):
                    
                    # Extract parts
                    parts = line.split()
                    
                    # Find documento separator
                    dash_idx = -1
                    for idx, part in enumerate(parts):
                        if part == "-":
                            dash_idx = idx
                            break
                    
                    if dash_idx > 0 and dash_idx < len(parts) - 1:
                        # Name is before documento type
                        name_parts = []
                        for idx in range(len(parts)):
                            part = parts[idx]
                            # Stop when we hit documento type
                            if any(doc in part.upper() for doc in ["D.N.I", "DNI", "P.", "C.E.", "PASAPORTE"]):
                                break
                            name_parts.append(part)
                        
                        nombre_completo = " ".join(name_parts)
                        
                        # Documento type is just before dash
                        tipo_documento = parts[dash_idx - 1] if dash_idx > 0 else ""
                        
                        # Documento number is after dash
                        numero_documento = parts[dash_idx + 1] if dash_idx + 1 < len(parts) else ""
                        
                        # Cargo is the rest after documento number
                        cargo_parts = parts[dash_idx + 2:]
                        cargo = " ".join(cargo_parts) if cargo_parts else ""
                        
                        # Clean up
                        nombre_completo = nombre_completo.strip()
                        tipo_documento = tipo_documento.strip()
                        numero_documento = numero_documento.strip()
                        cargo = cargo.strip()
                        
                        if nombre_completo and numero_documento:
                            representantes.append({
                                "nombre_completo": nombre_completo,
                                "tipo_documento": tipo_documento,
                                "numero_documento": numero_documento,
                                "cargo": cargo or "REPRESENTANTE LEGAL"
                            })
            
            logger.info(f"Parsed {len(representantes)} representantes")
            
        except Exception as e:
            logger.warning(f"Error parsing representantes: {e}")
        
        return representantes
