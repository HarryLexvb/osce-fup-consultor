"""
Network request interceptor for OSCE Angular SPA
"""

import logging
from camoufox.sync_api import Camoufox

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def intercept_requests():
    """Intercept all network requests to find API endpoints."""
    
    ruc = "20508238143"
    url = f"https://apps.osce.gob.pe/perfilprov-ui/ficha/{ruc}"
    
    requests_log = []
    
    with Camoufox(headless=True, humanize=True) as browser:
        page = browser.new_page()
        
        # Listen to all network requests
        def log_request(request):
            request_info = {
                "url": request.url,
                "method": request.method,
                "resource_type": request.resource_type
            }
            requests_log.append(request_info)
            logger.info(f"{request.method} {request.url}")
        
        def log_response(response):
            if "api" in response.url.lower() or "bus" in response.url.lower() or "ficha" in response.url.lower():
                logger.info(f"RESPONSE {response.status} {response.url}")
        
        page.on("request", log_request)
        page.on("response", log_response)
        
        logger.info(f"Navigating to: {url}")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        # Wait for Angular
        page.wait_for_timeout(15000)
        
        # Save all requests
        with open("osce_network_requests.txt", "w", encoding="utf-8") as f:
            f.write("=== All Network Requests ===\n\n")
            for req in requests_log:
                f.write(f"{req['method']} [{req['resource_type']}] {req['url']}\n")
        
        logger.info(f"\n\n{'='*60}")
        logger.info(f"Total requests: {len(requests_log)}")
        logger.info(f"Network log saved to: osce_network_requests.txt")
        logger.info(f"{'='*60}\n")
        
        # Filter API calls
        api_requests = [r for r in requests_log if any(keyword in r['url'].lower() for keyword in ['api', 'bus', 'perfilprov-bus', 'ficha', 'proveedor'])]
        
        logger.info(f"\n=== Potential API Endpoints ===")
        for req in api_requests:
            logger.info(f"{req['method']} {req['url']}")

if __name__ == "__main__":
    intercept_requests()
