"""
Quick test of new OSCE endpoint /resumen
"""

import asyncio
import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'osce_fup_portal.settings')
import django
django.setup()

from fup_consult.services.osce_client import OSCEClient

async def test_resumen_endpoint():
    """Test the /resumen endpoint with RUC 20508238143."""
    
    ruc = "20508238143"
    print(f"\n{'='*60}")
    print(f"Testing OSCE /resumen endpoint with RUC: {ruc}")
    print(f"{'='*60}\n")
    
    client = OSCEClient()
    
    try:
        data = await client.get_provider_general_data(ruc)
        
        print("✅ Successfully fetched data!\n")
        print(f"{'='*60}")
        print("GENERAL DATA:")
        print(f"{'='*60}")
        print(f"RUC: {data['ruc']}")
        print(f"Razón Social: {data['razon_social']}")
        print(f"Estado: {data['estado']}")
        print(f"Condición: {data['condicion']}")
        print(f"Tipo: {data['tipo_contribuyente']}")
        print(f"Domicilio: {data['domicilio']}")
        
        print(f"\n{'='*60}")
        print(f"SOCIOS/ACCIONISTAS: {len(data['socios'])}")
        print(f"{'='*60}")
        for socio in data['socios']:
            print(f"- {socio['nombre_completo']}")
            print(f"  {socio['tipo_documento']} {socio['numero_documento']}")
            print(f"  Participación: {socio['porcentaje_participacion']}%")
        
        print(f"\n{'='*60}")
        print(f"REPRESENTANTES LEGALES: {len(data['representantes'])}")
        print(f"{'='*60}")
        for rep in data['representantes']:
            print(f"- {rep['nombre_completo']}")
            print(f"  {rep['tipo_documento']} {rep['numero_documento']}")
        
        print(f"\n{'='*60}")
        print(f"ÓRGANOS DE ADMINISTRACIÓN: {len(data['organos'])}")
        print(f"{'='*60}")
        for org in data['organos']:
            print(f"- {org['nombre_completo']}")
            print(f"  {org['tipo_documento']} {org['numero_documento']}")
            print(f"  Cargo: {org['cargo']}")
        
        print(f"\n{'='*60}\n")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_resumen_endpoint())
