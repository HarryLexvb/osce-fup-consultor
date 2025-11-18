import httpx
import asyncio
from bs4 import BeautifulSoup
import json


async def scrape_osce_webpage():
    ruc = "20508238143"
    
    # The official OSCE provider portal URL
    url = f"https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/fichaProveedor/verProveedorCabecera.xhtml?ruc={ruc}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            print(f"Fetching: {url}")
            response = await client.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                # Save HTML for inspection
                with open("osce_page.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("✓ HTML saved to osce_page.html")
                
                # Try to parse and find API calls in the HTML/JavaScript
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for script tags that might contain API endpoints
                scripts = soup.find_all('script')
                print(f"\nFound {len(scripts)} script tags")
                
                # Save scripts for analysis
                with open("osce_scripts.txt", "w", encoding="utf-8") as f:
                    for i, script in enumerate(scripts):
                        if script.string:
                            f.write(f"\n\n{'='*80}\nScript {i+1}:\n{'='*80}\n")
                            f.write(script.string)
                
                print("✓ Scripts saved to osce_scripts.txt")
                
                # Look for data in the HTML
                print("\nSearching for 'api', 'endpoint', 'http' in scripts...")
                for script in scripts:
                    if script.string and ('api' in script.string.lower() or 'endpoint' in script.string.lower() or 'http' in script.string.lower()):
                        print(f"\n--- Found potential API reference ---")
                        print(script.string[:500])
            
        except Exception as e:
            print(f"Error: {type(e).__name__}: {str(e)}")


asyncio.run(scrape_osce_webpage())
