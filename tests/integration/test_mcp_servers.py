import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from mcp_servers.supplier.client import SupplierMCPClient
from mcp_servers.supplier.providers import AcmeVendorResponseMapper
from models.supplier import Supplier


def test_supplier_client_returns_list():
    client = SupplierMCPClient(provider_mode="mock")
    results = client.search_suppliers('laptop', 2)
    assert isinstance(results, list)
    assert all(isinstance(item, Supplier) for item in results)


def test_supplier_client_auto_falls_back_to_demo_catalog():
    client = SupplierMCPClient(
        provider_mode="auto",
        api_base_url="http://127.0.0.1:9",
        timeout_s=0.2,
    )
    results = client.search_suppliers("laptop", 1)
    assert len(results) >= 1


def test_acme_vendor_response_mapper_maps_payload():
    payload = {
        "results": [
            {
                "vendorCode": "acme-01",
                "displayName": "Acme Devices",
                "catalogTags": ["laptop", "it-hardware"],
                "minimumOrder": 2,
                "pricing": {"unitEur": 899.5},
                "fulfillment": {"leadTimeDays": 4},
                "quality": {"reliabilityScore": 0.93},
            }
        ]
    }
    mapped = AcmeVendorResponseMapper().map_payload(payload)
    assert len(mapped) == 1
    supplier = mapped[0]
    assert supplier.id == "acme-01"
    assert supplier.name == "Acme Devices"
    assert "laptop" in supplier.categories
    assert supplier.unit_price_eur == 899.5


def test_supplier_client_api_mode_with_acme_mapper():
    payload = {
        "results": [
            {
                "vendorCode": "acme-http-01",
                "displayName": "Acme HTTP Devices",
                "catalogTags": ["laptop"],
                "minimumOrder": 1,
                "pricing": {"unitEur": 799.0},
                "fulfillment": {"leadTimeDays": 5},
                "quality": {"reliabilityScore": 0.9},
            }
        ]
    }

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt, *args):  # noqa: A003
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base_url = f"http://127.0.0.1:{server.server_port}"

    try:
        client = SupplierMCPClient(
            provider_mode="api",
            api_base_url=base_url,
            api_response_format="acme_v1",
            timeout_s=1.0,
        )
        results = client.search_suppliers("laptop", 1)
        assert len(results) == 1
        assert results[0].id == "acme-http-01"
        assert results[0].name == "Acme HTTP Devices"
    finally:
        server.shutdown()
        server.server_close()
