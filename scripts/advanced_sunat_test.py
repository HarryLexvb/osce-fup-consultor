"""
Advanced SUNAT scraper - try multiple strategies to find representantes data
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

def advanced_sunat_scrape():
    """Try multiple strategies to get representantes from SUNAT"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        ruc = "20508238143"
        url = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/FrameCriterioBusquedaWeb.jsp"
        
        print(f"Testing advanced SUNAT scraping for RUC: {ruc}")
        print("-" * 60)
        
        driver.get(url)
        time.sleep(2)
        
        # Fill and search
        print("Filling RUC and searching...")
        ruc_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "txtRuc"))
        )
        ruc_input.send_keys(ruc)
        
        search_button = driver.find_element(By.ID, "btnAceptar")
        search_button.click()
        time.sleep(3)
        
        # Check main page for any representantes info
        print("\n=== MAIN PAGE ANALYSIS ===")
        main_text = driver.find_element(By.TAG_NAME, "body").text
        
        # Look for representantes in main text
        if "Representante" in main_text:
            print("[OK] Found 'Representante' in main page")
            idx = main_text.find("Representante")
            context = main_text[max(0, idx-100):min(len(main_text), idx+500)]
            print(f"Context:\n{context}")
        
        # Try to find and click representantes link
        print("\n=== LOOKING FOR LINKS ===")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        rep_link = None
        
        for link in all_links:
            link_text = link.text.strip()
            if link_text and ("Representante" in link_text or "representante" in link_text):
                print(f"[OK] Found link: '{link_text}'")
                print(f"    href: {link.get_attribute('href')}")
                print(f"    onclick: {link.get_attribute('onclick')}")
                rep_link = link
                break
        
        if rep_link:
            print("\n=== CLICKING REPRESENTANTES LINK ===")
            
            # Get initial window handles
            initial_windows = driver.window_handles
            print(f"Initial windows: {len(initial_windows)}")
            
            # Click link
            rep_link.click()
            time.sleep(4)
            
            # Check if new window opened
            new_windows = driver.window_handles
            print(f"After click windows: {len(new_windows)}")
            
            if len(new_windows) > len(initial_windows):
                print("[OK] New window/tab opened, switching...")
                driver.switch_to.window(new_windows[-1])
                time.sleep(2)
            
            # Check for iframes
            iframes = driver.find_elements(By.TAG_NAME, "iframe")
            print(f"Found {len(iframes)} iframes")
            
            if iframes:
                print("[OK] Switching to iframe...")
                driver.switch_to.frame(iframes[0])
                time.sleep(2)
            
            # Get content after click
            rep_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"\n=== REPRESENTANTES PAGE TEXT (length: {len(rep_text)}) ===")
            print(rep_text)
            
            # Save to file
            with open("sunat_representantes_full.txt", "w", encoding="utf-8") as f:
                f.write(rep_text)
            print("\n[OK] Saved: sunat_representantes_full.txt")
            
            # Look for specific patterns
            print("\n=== LOOKING FOR NAMES ===")
            names_to_find = ["MURAKAMI", "DAMONTE", "MARIO", "FERNANDO"]
            for name in names_to_find:
                if name in rep_text.upper():
                    print(f"[OK] Found: {name}")
                    idx = rep_text.upper().find(name)
                    context = rep_text[max(0, idx-50):min(len(rep_text), idx+150)]
                    print(f"    Context: {context}")
            
            # Check for tables
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"\n[INFO] Found {len(tables)} tables")
            
            for i, table in enumerate(tables):
                print(f"\n--- Table {i+1} ---")
                print(table.text[:500])
                
        else:
            print("[--] No representantes link found")
            
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    advanced_sunat_scrape()
