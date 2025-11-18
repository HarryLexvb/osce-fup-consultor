import httpx
import asyncio
import json


async def test():
    async with httpx.AsyncClient() as client:
        # Get full provider data
        resp = await client.get("https://eap.oece.gob.pe/perfilprov-bus/1.0/ficha/20508238143")
        data = resp.json()
        
        # Save to file for inspection
        with open("full_api_response.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print("Full API Response saved to full_api_response.json")
        print("\nKeys in response:")
        for key in data.keys():
            print(f"  - {key}")
        
        if "proveedorT01" in data:
            print("\nKeys in proveedorT01:")
            for key in data["proveedorT01"].keys():
                print(f"  - {key}: {type(data['proveedorT01'][key])}")


asyncio.run(test())
