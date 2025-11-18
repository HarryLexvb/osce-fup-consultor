"""
Script to find correct OSCE/SUNAT APIs for provider detailed data.
Based on official OSCE portal at prodapp2.seace.gob.pe
"""
import httpx
import asyncio
import json


async def test_sunat_and_osce_apis():
    ruc = "20508238143"
    
    # Test various API patterns
    test_urls = [
        # SEACE/OSCE endpoints
        (f"https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/api/proveedor/{ruc}", "SEACE Proveedor API"),
        (f"https://prodapp2.seace.gob.pe/seacebus-uiwd-pub/api/ficha/{ruc}", "SEACE Ficha API"),
        (f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha-detalle/{ruc}", "Perfil Detalle"),
        
        # Try with authentication/session headers
        (f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{ruc}/detalle", "Ficha con detalle"),
        (f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{ruc}/completo", "Ficha completo"),
        
        # SUNAT endpoints (public)
        (f"https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias", f"SUNAT ConsultaRUC (POST required)"),
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://prodapp2.seace.gob.pe/"
    }
    
    successful = []
    
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for url, name in test_urls:
            try:
                print(f"\n{'='*80}")
                print(f"Testing: {name}")
                print(f"URL: {url}")
                print(f"{'='*80}")
                
                response = await client.get(url, headers=headers)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    try:
                        data = response.json()
                        print(f"✓ SUCCESS - JSON Response")
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
                        successful.append({
                            "name": name,
                            "url": url,
                            "data": data
                        })
                    except:
                        print(f"✓ SUCCESS - HTML/Text Response (length: {len(response.text)})")
                        if len(response.text) < 500:
                            print(response.text)
                else:
                    print(f"✗ Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"✗ Error: {type(e).__name__}: {str(e)[:200]}")
            
            await asyncio.sleep(0.5)
    
    if successful:
        print(f"\n\n✓✓✓ Found {len(successful)} successful endpoints!")
        with open("working_endpoints.json", "w", encoding="utf-8") as f:
            json.dump(successful, f, indent=2, ensure_ascii=False)
        print("Saved to working_endpoints.json")
    else:
        print("\n\n✗✗✗ No working endpoints found")
        print("\nNote: The official OSCE portal likely uses:")
        print("1. Session-based authentication")
        print("2. POST requests with specific parameters")
        print("3. CSRF tokens or API keys")
        print("4. Or web scraping of rendered HTML")


asyncio.run(test_sunat_and_osce_apis())
