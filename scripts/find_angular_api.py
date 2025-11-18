import httpx
import asyncio
import json
import re


async def find_api_endpoints():
    """
    Since the page is an Angular SPA, we need to find the API endpoints
    that the JavaScript app uses to fetch data.
    """
    ruc = "20508238143"
    
    # Try common API patterns for OSCE Angular app
    base_urls = [
        "https://apps.osce.gob.pe/perfilprov-ui-api",
        "https://apps.osce.gob.pe/perfilprov-api",
        "https://apps.osce.gob.pe/api/perfilprov",
        "https://eap.oece.gob.pe/perfilprov-api",
        "https://eap.osce.gob.pe/perfilprov-ui-api",
    ]
    
    endpoints = [
        "/proveedor/{ruc}",
        "/ficha/{ruc}",
        "/detalle/{ruc}",
        "/consulta/{ruc}",
        "/v1/proveedor/{ruc}",
        "/v1/ficha/{ruc}",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://apps.osce.gob.pe",
        "Referer": f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}",
    }
    
    print("Searching for Angular API endpoints...\n")
    
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        # First, try to download the main.js file to find API base URL
        main_js_url = "https://apps.osce.gob.pe/perfilprov-ui/main.f0be3c0d0b123adadb50.js"
        
        try:
            print(f"Downloading main.js to find API endpoints...")
            response = await client.get(main_js_url)
            
            if response.status_code == 200:
                js_content = response.text
                
                # Save for inspection
                with open("main_js.txt", "w", encoding="utf-8") as f:
                    f.write(js_content)
                print(f"✓ Saved main.js ({len(js_content)} bytes)")
                
                # Search for API URLs in the JavaScript
                api_patterns = [
                    r'https?://[^"\s]+/api/[^"\s]+',
                    r'https?://apps\.osce\.gob\.pe/[^"\s]+',
                    r'https?://eap\.[^"\s]+/[^"\s]+',
                    r'baseUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                    r'apiUrl["\']?\s*[:=]\s*["\']([^"\']+)["\']',
                ]
                
                found_urls = set()
                for pattern in api_patterns:
                    matches = re.findall(pattern, js_content)
                    found_urls.update(matches)
                
                if found_urls:
                    print(f"\n✓ Found {len(found_urls)} potential API URLs:")
                    for url in sorted(found_urls)[:20]:
                        print(f"  - {url}")
                
                # Look for specific endpoints
                if "/sociedades" in js_content:
                    print("\n✓ Found '/sociedades' endpoint reference")
                if "/representantes" in js_content:
                    print("✓ Found '/representantes' endpoint reference")
                if "/organos" in js_content:
                    print("✓ Found '/organos' endpoint reference")
                
        except Exception as e:
            print(f"Could not download main.js: {e}")
        
        # Now test potential API endpoints
        print("\n\nTesting API endpoints...\n")
        
        for base_url in base_urls:
            for endpoint in endpoints:
                url = base_url + endpoint.format(ruc=ruc)
                
                try:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        print(f"\n{'='*80}")
                        print(f"✓✓✓ SUCCESS! {url}")
                        print(f"{'='*80}")
                        
                        try:
                            data = response.json()
                            print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
                            
                            # Save successful response
                            with open(f"api_response_{base_url.split('/')[-1]}.json", "w", encoding="utf-8") as f:
                                json.dump(data, f, indent=2, ensure_ascii=False)
                                
                        except:
                            print(response.text[:1000])
                    
                    elif response.status_code != 404:
                        print(f"  {url} -> Status {response.status_code}")
                        
                except Exception as e:
                    pass
                
                await asyncio.sleep(0.2)


asyncio.run(find_api_endpoints())
