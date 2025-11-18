import httpx
import asyncio
import json


async def test_detailed_endpoints():
    ruc = "20508238143"
    
    # Based on OSCE API patterns, try these endpoints
    endpoints = {
        "Ficha completa con detalles": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha-completa/{ruc}",
        "Detalle del proveedor": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/detalle/{ruc}",
        "Info completa": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/info/{ruc}",
        "Proveedor completo": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/proveedor/{ruc}",
        
        # Try domicilio/address endpoints
        "Domicilio fiscal": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/domicilio-fiscal/{ruc}",
        "Ubicacion": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ubicacion/{ruc}",
        
        # Try SUNAT-related endpoints (since address comes from SUNAT)
        "SUNAT data": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/sunat/{ruc}",
        "Datos SUNAT": f"https://eap.oece.gob.pe/perfilprov-bus/1.0/datos-sunat/{ruc}",
    }
    
    results = {}
    
    async with httpx.AsyncClient(timeout=10) as client:
        for name, url in endpoints.items():
            try:
                print(f"\nTesting: {name}")
                print(f"URL: {url}")
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ SUCCESS! Status: {response.status_code}")
                    results[name] = data
                    print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
                else:
                    print(f"✗ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ Error: {type(e).__name__}: {str(e)[:100]}")
            
            await asyncio.sleep(0.3)
    
    # Save successful results
    if results:
        with open("successful_endpoints.json", "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n\n✓ Saved {len(results)} successful endpoints to successful_endpoints.json")


asyncio.run(test_detailed_endpoints())
