"""Local mock vendor API server that emits Acme v1 payloads."""

from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

FIXTURE_PAYLOAD = {
    "results": [
        {
            "vendorCode": "acme-01",
            "displayName": "Acme Devices",
            "catalogTags": ["laptop", "it-hardware"],
            "minimumOrder": 1,
            "pricing": {"unitEur": 899.5},
            "fulfillment": {"leadTimeDays": 4},
            "quality": {"reliabilityScore": 0.93},
        },
        {
            "vendorCode": "acme-02",
            "displayName": "Acme Office",
            "catalogTags": ["desk", "office-furniture"],
            "minimumOrder": 2,
            "pricing": {"unitEur": 320.0},
            "fulfillment": {"leadTimeDays": 8},
            "quality": {"reliabilityScore": 0.9},
        },
    ]
}


class AcmeVendorApiHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/suppliers/search":
            self._send_json({"error": "not_found"}, status=404)
            return

        query = parse_qs(parsed.query)
        category = (query.get("category", [""])[0] or "").lower()
        quantity = int((query.get("quantity", ["1"])[0] or "1"))

        payload = self._load_fixture()
        rows = payload.get("results", [])
        if category:
            rows = [
                row
                for row in rows
                if category in [str(tag).lower() for tag in row.get("catalogTags", [])]
                and int(row.get("minimumOrder", 1)) <= quantity
            ]
        self._send_json({"results": rows})

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        # Keep console output quiet for demo runs.
        return

    @staticmethod
    def _load_fixture() -> dict:
        return FIXTURE_PAYLOAD

    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run(host: str = "127.0.0.1", port: int = 8090) -> None:
    server = ThreadingHTTPServer((host, port), AcmeVendorApiHandler)
    print(f"Mock Acme Vendor API running at http://{host}:{port}")
    server.serve_forever()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run local mock Acme vendor API.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8090)
    args = parser.parse_args()
    run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
