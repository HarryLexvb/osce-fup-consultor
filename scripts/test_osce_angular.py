"""
Test scraping OSCE Angular SPA at https://apps.osce.gob.pe/perfilprov-ui/ficha/{RUC}
Check if it has representantes, socios, organos data
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def test_osce_angular_spa():
    """Test OSCE Angular SPA for complete data"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        ruc = "20508238143"
        url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
        
        print(f"Testing OSCE Angular SPA with RUC: {ruc}")
        print(f"URL: {url}")
        print("-" * 60)
        
        print("Opening page...")
        driver.get(url)
        
        # Wait for Angular to load (longer timeout for SPA)
        print("Waiting for Angular app to render...")
        time.sleep(8)
        
        # Get page text
        page_text = driver.find_element(By.TAG_NAME, "body").text
        
        print("\n=== PAGE CONTENT (first 2000 chars) ===")
        print(page_text[:2000])
        
        # Save full HTML for inspection
        with open("osce_angular_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("\n[OK] Saved: osce_angular_page.html")
        
        # Save full text
        with open("osce_angular_text.txt", "w", encoding="utf-8") as f:
            f.write(page_text)
        print("[OK] Saved: osce_angular_text.txt")
        
        # Check for specific sections
        print("\n=== CHECKING FOR DATA SECTIONS ===")
        
        sections_to_check = [
            ("Domicilio", ["domicilio", "direccion", "fiscal"]),
            ("Socios", ["socio", "accionista", "conformacion societaria"]),
            ("Representantes", ["representante", "legal"]),
            ("Organos", ["organo", "administracion", "gerente", "directorio"])
        ]
        
        for section_name, keywords in sections_to_check:
            found = any(keyword.lower() in page_text.lower() for keyword in keywords)
            status = "[OK]" if found else "[--]"
            print(f"{status} {section_name}: {'Found' if found else 'Not found'}")
            
            if found:
                # Try to find the section and print some context
                for keyword in keywords:
                    if keyword.lower() in page_text.lower():
                        idx = page_text.lower().find(keyword.lower())
                        context = page_text[max(0, idx-50):min(len(page_text), idx+200)]
                        print(f"    Context: ...{context}...")
                        break
        
        # Look for specific names from requirements
        print("\n=== CHECKING FOR SPECIFIC NAMES ===")
        expected_names = [
            "MARIO CARLOS ALBERTO DAMONTE VILLALONGA",
            "MARIA DEL CARMEN LINZOAIN",
            "MURAKAMI MOROYA BRUNO",
            "DAMONTE FERNANDO JOSE"
        ]
        
        for name in expected_names:
            found = name in page_text.upper()
            status = "[OK]" if found else "[--]"
            print(f"{status} {name}")
        
        # Check for tables
        tables = driver.find_elements(By.TAG_NAME, "table")
        print(f"\n[INFO] Found {len(tables)} tables on page")
        
        for i, table in enumerate(tables[:5]):  # First 5 tables
            table_text = table.text
            if table_text:
                print(f"\n--- Table {i+1} (first 300 chars) ---")
                print(table_text[:300])
        
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    test_osce_angular_spa()
