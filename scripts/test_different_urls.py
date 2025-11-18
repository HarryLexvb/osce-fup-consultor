"""
Test different OSCE URLs to find where the complete data is displayed
"""
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def test_urls(ruc: str):
    """Test different URLs"""
    
    urls_to_test = [
        f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}",
        f"https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/fichaProveedor/verProveedorCabecera.xhtml?ruc={ruc}",
        f"https://apps.osce.gob.pe/perfilprov-ui/proveedor/{ruc}",
        f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}/detalle",
    ]
    
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        for url in urls_to_test:
            print(f"\n{'='*80}")
            print(f"Testing: {url}")
            print(f"{'='*80}")
            
            try:
                driver.get(url)
                time.sleep(5)
                
                page_text = driver.find_element(By.TAG_NAME, "body").text
                
                # Check for keywords
                found = []
                if "Conformación" in page_text or "Socios" in page_text:
                    found.append("Socios/Conformación")
                if "Representantes" in page_text:
                    found.append("Representantes")
                if "Órganos" in page_text or "Organos" in page_text:
                    found.append("Órganos")
                if "Domicilio" in page_text and ("LIMA" in page_text or "SAN ISIDRO" in page_text):
                    found.append("Domicilio completo")
                if "DAMONTE" in page_text or "MURAKAMI" in page_text:
                    found.append("Nombres de personas (representantes/socios)")
                
                if found:
                    print(f"✓✓✓ FOUND DATA: {', '.join(found)}")
                    print("\nFirst 3000 chars of text:")
                    print(page_text[:3000])
                    
                    # Save this HTML
                    filename = f"found_data_{url.split('/')[-2]}_{ruc}.html"
                    with open(filename, "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                    print(f"\n✓ Saved to {filename}")
                else:
                    print("✗ No complete data found")
                    
            except Exception as e:
                print(f"Error: {type(e).__name__}: {str(e)}")
            
    finally:
        driver.quit()


if __name__ == "__main__":
    ruc = "20508238143"
    test_urls(ruc)
