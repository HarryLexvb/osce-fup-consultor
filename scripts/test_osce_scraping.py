import httpx
import asyncio
import json
from bs4 import BeautifulSoup


async def test_osce_page():
    ruc = "20508238143"
    url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
    }
    
    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        try:
            print(f"Fetching: {url}")
            response = await client.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            print(f"Content-Type: {response.headers.get('content-type')}")
            print(f"Content-Length: {len(response.text)}")
            
            if response.status_code == 200:
                # Save full HTML
                with open("osce_ficha_page.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("\n✓ HTML saved to osce_ficha_page.html")
                
                # Try to parse structure
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for common patterns in OSCE pages
                print("\n--- Searching for data patterns ---")
                
                # Search for text patterns
                if "QUANTUM ANDES" in response.text:
                    print("✓ Found company name in HTML")
                
                if "Socios" in response.text or "Accionistas" in response.text:
                    print("✓ Found 'Socios/Accionistas' text")
                
                if "Representantes" in response.text:
                    print("✓ Found 'Representantes' text")
                
                # Look for tables
                tables = soup.find_all('table')
                print(f"\n✓ Found {len(tables)} tables")
                
                # Look for script tags with data
                scripts = soup.find_all('script')
                print(f"✓ Found {len(scripts)} script tags")
                
                # Search for JSON data in scripts
                for i, script in enumerate(scripts):
                    if script.string and ('window.' in script.string or 'var ' in script.string or 'const ' in script.string):
                        script_text = script.string[:500]
                        if 'socios' in script_text.lower() or 'representantes' in script_text.lower() or 'ruc' in script_text.lower():
                            print(f"\n--- Potential data in script {i+1} ---")
                            print(script_text)
                
                # Look for specific divs/sections
                sections = soup.find_all(['section', 'div'], class_=True)
                print(f"\n✓ Found {len(sections)} sections/divs with classes")
                
                # Save first 5000 chars for inspection
                print("\n--- First 2000 characters of HTML ---")
                print(response.text[:2000])
                
        except Exception as e:
            print(f"Error: {type(e).__name__}: {str(e)}")


asyncio.run(test_osce_page())
