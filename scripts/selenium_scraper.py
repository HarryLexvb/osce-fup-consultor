"""
OSCE Web Scraper using Selenium
Extracts provider data from Angular SPA
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


def scrape_osce_provider(ruc: str):
    """Scrape provider data using Selenium"""
    
    url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
    
    # Setup Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    # Initialize driver
    print(f"Initializing Chrome driver...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        print(f"Loading: {url}")
        driver.get(url)
        
        # Wait for page to load (wait for body content)
        print("Waiting for page to load...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Give Angular time to render
        time.sleep(5)
        
        # Save full page HTML after JavaScript rendering
        page_html = driver.page_source
        with open(f"osce_rendered_{ruc}.html", "w", encoding="utf-8") as f:
            f.write(page_html)
        print(f"Saved rendered HTML ({len(page_html)} bytes)")
        
        # Extract data
        data = {
            "ruc": ruc,
            "razon_social": None,
            "estado": None,
            "condicion": None,
            "tipo_contribuyente": None,
            "domicilio": None,
            "telefonos": [],
            "emails": [],
            "socios": [],
            "representantes": [],
            "organos": [],
        }
        
        # Try to find data in the rendered page
        try:
            # Look for common patterns
            page_text = driver.find_element(By.TAG_NAME, "body").text
            print("\n--- Full Page Text ---")
            print(page_text)
            print("\n--- End of Page Text ---\n")
            
            # Check if data is present
            if "QUANTUM ANDES" in page_text:
                print("\n✓ Found company name")
            if "Socios" in page_text or "Accionistas" in page_text or "Conformación" in page_text:
                print("✓ Found Socios/Accionistas section")
            if "Representantes" in page_text:
                print("✓ Found Representantes section")
            if "Órganos" in page_text or "Organos" in page_text:
                print("✓ Found Órganos section")
            if "Domicilio" in page_text:
                print("✓ Found Domicilio")
                
        except Exception as e:
            print(f"Error extracting text: {e}")
        
        # Save screenshot for debugging
        driver.save_screenshot(f"osce_screenshot_{ruc}.png")
        print(f"\n✓ Screenshot saved")
        
        return data
        
    finally:
        driver.quit()
        print("Browser closed")


if __name__ == "__main__":
    ruc = "20508238143"
    print(f"\nScraping OSCE data for RUC: {ruc}\n")
    print("="*80)
    
    data = scrape_osce_provider(ruc)
    
    # Save results
    with open(f"scraped_data_{ruc}.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✓ Data saved to scraped_data_{ruc}.json")
