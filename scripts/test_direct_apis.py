import httpx
import asyncio
import json


async def test_direct_api():
    ruc = "20508238143"
    
    # Based on Angular app pattern, the API is likely at a predictable location
    test_urls = [
        # Most likely candidates
        f"https://apps.osce.gob.pe/perfilprov-ui-api/proveedor/{ruc}",
        f"https://apps.osce.gob.pe/perfilprov-ui-api/ficha/{ruc}",
        f"https://apps.osce.gob.pe/perfilprov-api/proveedor/{ruc}",
        f"https://apps.osce.gob.pe/perfilprov-api/ficha/{ruc}",
        
        # Alternative paths
        f"https://apps.osce.gob.pe/api/proveedor/{ruc}",
        f"https://apps.osce.gob.pe/api/ficha/{ruc}",
        
        # Backend service paths
        f"https://eap.osce.gob.pe/perfilprov-ui-api/proveedor/{ruc}",
        f"https://eap.osce.gob.pe/perfilprov-api/proveedor/{ruc}",
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Origin": "https://apps.osce.gob.pe",
        "Referer": f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}",
    }
    
    async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
        for url in test_urls:
            try:
                print(f"\nTesting: {url}")
                response = await client.get(url, headers=headers)
                print(f"Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("SUCCESS!")
                    try:
                        data = response.json()
                        print(json.dumps(data, indent=2, ensure_ascii=False)[:3000])
                        
                        # Save successful response
                        filename = f"success_api_{url.split('/')[-2]}_{ruc}.json"
                        with open(filename, "w", encoding="utf-8") as f:
                            json.dump(data, f, indent=2, ensure_ascii=False)
                        print(f"\nSaved to {filename}")
                        
                        return data
                        
                    except:
                        print("Response is not JSON:")
                        print(response.text[:500])
                        
            except Exception as e:
                print(f"Error: {type(e).__name__}")
            
            await asyncio.sleep(0.3)
    
    print("\n\nNo working API found. The Angular app might be using:")
    print("1. GraphQL endpoint")
    print("2. WebSocket connection")
    print("3. Server-side rendering")
    print("4. Protected API with auth tokens")


asyncio.run(test_direct_api())
