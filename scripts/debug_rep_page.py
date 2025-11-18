"""
Debug script to see what's on the representantes page
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

def debug_representantes_page():
    """Debug what's on the representantes page"""
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # Disable headless for debugging
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        ruc = "20508238143"
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        
        print(f"Opening SUNAT page...")
        driver.get(url)
        time.sleep(3)
        
        # Fill RUC
        print(f"Filling RUC: {ruc}")
        ruc_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        )
        ruc_input.clear()
        ruc_input.send_keys(ruc)
        
        # Click search
        print("Clicking search button...")
        search_button = driver.find_element(By.ID, "btnAceptar")
        search_button.click()
        time.sleep(4)
        
        print("\n=== MAIN PAGE TEXT (first 1000 chars) ===")
        main_text = driver.find_element(By.TAG_NAME, "body").text
        print(main_text[:1000])
        print("\n...")
        
        # Try to find representantes link
        print("\n=== LOOKING FOR REPRESENTANTES LINK ===")
        links = driver.find_elements(By.TAG_NAME, "a")
        rep_link = None
        for link in links:
            link_text = link.text.strip()
            if "Representante" in link_text or "representante" in link_text:
                print(f"Found link: '{link_text}'")
                print(f"Link href: {link.get_attribute('href')}")
                rep_link = link
        
        # Try to click
        if rep_link:
            print(f"\n=== CLICKING REPRESENTANTES LINK ===")
            rep_link.click()
            time.sleep(4)
            
            print("=== REPRESENTANTES PAGE TEXT ===")
            rep_text = driver.find_element(By.TAG_NAME, "body").text
            print(rep_text)
            
        else:
            print("No representantes link found!")
        
        input("Press Enter to close browser...")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        input("Press Enter to close browser...")
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_representantes_page()
