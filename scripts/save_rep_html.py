"""
Save HTML from representantes page for inspection
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

def save_representantes_html():
    """Save HTML from representantes page"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        ruc = "20508238143"
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        
        print(f"Opening SUNAT...")
        driver.get(url)
        time.sleep(2)
        
        # Fill RUC
        print(f"Filling RUC: {ruc}")
        ruc_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        )
        ruc_input.clear()
        ruc_input.send_keys(ruc)
        
        # Click search
        print("Searching...")
        search_button = driver.find_element(By.ID, "btnAceptar")
        search_button.click()
        time.sleep(3)
        
        # Save main page HTML
        with open("sunat_main_page.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        print("Saved: sunat_main_page.html")
        
        # Try to click representantes link
        representantes_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "Representante")
        if representantes_links:
            print(f"Clicking representantes link...")
            representantes_links[0].click()
            time.sleep(3)
            
            # Check for iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes")
            
            if iframes:
                driver.switch_to.frame(iframes[0])
                time.sleep(2)
            
            # Save representantes page HTML
            with open("sunat_representantes_page.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
            print("Saved: sunat_representantes_page.html")
            
            # Get all text
            page_text = driver.find_element(By.TAG_NAME, "body").text
            with open("sunat_representantes_text.txt", "w", encoding="utf-8") as f:
                f.write(page_text)
            print("Saved: sunat_representantes_text.txt")
            
            # Check tables
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"Found {len(tables)} tables")
            for i, table in enumerate(tables):
                with open(f"sunat_table_{i}.txt", "w", encoding="utf-8") as f:
                    f.write(table.text)
                print(f"Saved: sunat_table_{i}.txt")
            
        else:
            print("No representantes link found!")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    save_representantes_html()
