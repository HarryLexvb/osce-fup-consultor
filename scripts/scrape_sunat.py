"""
SUNAT Web Scraper
Obtiene datos del portal público de SUNAT donde SÍ aparece toda la información
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import re


def scrape_sunat_data(ruc: str):
    """
    Scrape data from SUNAT's public consultation page
    URL: https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp
    """
    
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Comment this to see browser
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        print(f"Loading SUNAT consultation page...")
        driver.get(url)
        
        # Wait for page load
        time.sleep(2)
        
        #Fill RUC input
        try:
            ruc_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "txtRuc"))
            )
            ruc_input.clear()
            ruc_input.send_keys(ruc)
            print(f"✓ Entered RUC: {ruc}")
            
            # Click search button
            search_button = driver.find_element(By.ID, "btnAceptar")
            search_button.click()
            print("✓ Clicked search")
            
            # Wait for results
            time.sleep(3)
            
            # Get page content
            page_text = driver.find_element(By.TAG_NAME, "body").text
            page_html = driver.page_source
            
            print("\n--- SUNAT Page Text ---")
            print(page_text)
            
            # Save HTML
            with open(f"sunat_result_{ruc}.html", "w", encoding="utf-8") as f:
                f.write(page_html)
            print(f"\n✓ Saved HTML to sunat_result_{ruc}.html")
            
            # Save screenshot
            driver.save_screenshot(f"sunat_screenshot_{ruc}.png")
            print(f"✓ Saved screenshot")
            
            # Extract data patterns
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
                "representantes": [],
            }
            
            # Parse the text to extract structured data
            lines = page_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                
                if "Número de RUC:" in line and i+1 < len(lines):
                    # Format: "20508238143 - QUANTUM ANDES S.A.C."
                    next_line = lines[i+1].strip()
                    if " - " in next_line:
                        data["razon_social"] = next_line.split(" - ", 1)[1]
                
                elif "Tipo Contribuyente:" in line and i+1 < len(lines):
                    data["tipo_contribuyente"] = lines[i+1].strip()
                
                elif "Estado del Contribuyente:" in line and i+1 < len(lines):
                    data["estado"] = lines[i+1].strip()
                
                elif "Condición del Contribuyente:" in line and i+1 < len(lines):
                    data["condicion"] = lines[i+1].strip()
                
                elif "Domicilio Fiscal:" in line and i+1 < len(lines):
                    domicilio_line = lines[i+1].strip()
                    data["domicilio"] = domicilio_line
                    
                    # Extract departamento/provincia/distrito from end
                    # Format: "... LIMA - LIMA - SAN ISIDRO"
                    if " - " in domicilio_line:
                        parts = domicilio_line.split(" - ")
                        if len(parts) >= 3:
                            # Get last 3 parts (could be in the middle of address)
                            # Look for pattern at the end
                            domicilio_upper = domicilio_line.upper()
                            # Extract LIMA - LIMA - SAN ISIDRO pattern
                            match = re.search(r'([A-Z\s]+)\s+-\s+([A-Z\s]+)\s+-\s+([A-Z\s]+)$', domicilio_upper)
                            if match:
                                data["departamento"] = match.group(1).strip()
                                data["provincia"] = match.group(2).strip()
                                data["distrito"] = match.group(3).strip()
            
            print("\n--- Extracted Data ---")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Try to click on Representantes link
            try:
                print("\n--- Looking for Representantes link ---")
                # Find link by text
                representantes_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Representante")
                if representantes_links:
                    print(f"✓ Found {len(representantes_links)} Representantes link(s)")
                    representantes_links[0].click()
                    print("✓ Clicked Representantes link")
                    time.sleep(3)
                    
                    # Get representantes data
                    rep_text = driver.find_element(By.TAG_NAME, "body").text
                    print("\n--- Representantes Page ---")
                    print(rep_text)
                    
                    # Save representantes HTML
                    with open(f"sunat_representantes_{ruc}.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    driver.save_screenshot(f"sunat_representantes_{ruc}.png")
                    print("✓ Saved representantes data")
                    
            except Exception as e:
                print(f"Could not get representantes: {type(e).__name__}")
            
            return data
            
        except Exception as e:
            print(f"Error during scraping: {type(e).__name__}: {str(e)}")
            driver.save_screenshot(f"sunat_error_{ruc}.png")
            return None
            
    finally:
        time.sleep(2)  # Keep browser open briefly
        driver.quit()


if __name__ == "__main__":
    ruc = "20508238143"
    print(f"Scraping SUNAT data for RUC: {ruc}\n")
    print("="*80)
    
    data = scrape_sunat_data(ruc)
    
    if data:
        with open(f"sunat_scraped_{ruc}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"\n✓ Data saved to sunat_scraped_{ruc}.json")
