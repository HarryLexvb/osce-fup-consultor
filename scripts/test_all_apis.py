import httpx
import asyncio
import json


async def test_apis():
    ruc = "20508238143"
    
    # Test different possible API endpoints
    urls = [
        # Datos generales (ya funciona)
        f"https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/{ruc}",
        
        # Intentar diferentes bases para socios
        f"https://eap.osce.gob.pe/ficha-proveedor-cns/1.0/sociedades/{ruc}",
        f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/sociedades/{ruc}",
        f"https://eap.osce.gob.pe/perfilprov-bus/1.0/sociedades/{ruc}",
        f"https://eap.oece.gob.pe/perfilprov-bus/1.0/sociedades/{ruc}",
        
        # Representantes
        f"https://eap.osce.gob.pe/ficha-proveedor-cns/1.0/representantes/{ruc}",
        f"https://eap.oece.gob.pe/ficha-proveedor-cns/1.0/representantes/{ruc}",
        f"https://eap.osce.gob.pe/perfilprov-bus/1.0/representantes/{ruc}",
        f"https://eap.oece.gob.pe/perfilprov-bus/1.0/representantes/{ruc}",
        
        # Domicilio
        f"https://eap.osce.gob.pe/perfilprov-bus/1.0/domicilio/{ruc}",
        f"https://eap.oece.gob.pe/perfilprov-bus/1.0/domicilio/{ruc}",
        f"https://eap.osce.gob.pe/perfilprov-bus/1.0/direccion/{ruc}",
        f"https://eap.oece.gob.pe/perfilprov-bus/1.0/direccion/{ruc}",
    ]
    
    async with httpx.AsyncClient(timeout=10) as client:
        for url in urls:
            try:
                print(f"\n{'='*80}")
                print(f"Testing: {url}")
                print(f"{'='*80}")
                response = await client.get(url)
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✓ SUCCESS!")
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                else:
                    print(f"✗ Status: {response.status_code}")
                    
            except Exception as e:
                print(f"✗ Error: {str(e)}")
            
            await asyncio.sleep(0.5)  # Be nice to the API


asyncio.run(test_apis())
