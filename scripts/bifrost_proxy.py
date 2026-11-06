"""Expose only authenticated Bifrost chat completions to the VeriFact app.

Bind to loopback and put Cloudflare Tunnel in front of this proxy, never Bifrost's
admin/dashboard port. The bearer token is read from a local 0600 file.
"""
from __future__ import annotations

import hmac
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

TOKEN_FILE = Path.home() / ".config/verifact/bifrost_proxy_token"
VK_FILE = Path.home() / ".config/verifact/bifrost_virtual_key"
TOKEN = os.environ.get("BIFROST_PROXY_TOKEN") or TOKEN_FILE.read_text().strip()
VIRTUAL_KEY = os.environ.get("BIFROST_VIRTUAL_KEY") or VK_FILE.read_text().strip()
UPSTREAM = "http://127.0.0.1:8080/v1/chat/completions"
MAX_BODY = 1_000_000


class Handler(BaseHTTPRequestHandler):
    server_version = "VeriFactInferenceProxy"

    def _send(self, status: int, body: bytes, content_type: str = "application/json") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path == "/healthz":
            self._send(200, b'{"status":"ok"}')
        else:
            self._send(404, b'{"error":"not_found"}')

    def do_POST(self) -> None:
        if self.path != "/v1/chat/completions":
            self._send(404, b'{"error":"not_found"}')
            return
        supplied = self.headers.get("Authorization", "")
        if not hmac.compare_digest(supplied, f"Bearer {TOKEN}"):
            self._send(401, b'{"error":"unauthorized"}')
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send(400, b'{"error":"invalid_content_length"}')
            return
        if length <= 0 or length > MAX_BODY:
            self._send(413, b'{"error":"request_body_too_large_or_empty"}')
            return
        body = self.rfile.read(length)
        try:
            payload = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send(400, b'{"error":"invalid_json"}')
            return
        if not isinstance(payload, dict) or not str(payload.get("model", "")).startswith("gemini/"):
            self._send(400, b'{"error":"model_not_allowed"}')
            return
        if not isinstance(payload.get("messages"), list):
            self._send(400, b'{"error":"messages_required"}')
            return
        request = Request(UPSTREAM, data=body, headers={"Content-Type": "application/json", "x-bf-vk": VIRTUAL_KEY}, method="POST")
        try:
            with urlopen(request, timeout=90) as response:
                self._send(response.status, response.read(), response.headers.get("Content-Type", "application/json"))
        except HTTPError as exc:
            self._send(exc.code, exc.read(), exc.headers.get("Content-Type", "application/json"))
        except (URLError, TimeoutError, OSError):
            self._send(502, b'{"error":"upstream_unavailable"}')

    def log_message(self, fmt: str, *args: object) -> None:
        # Do not log request bodies, authorization headers, or claim text.
        print(f"{self.address_string()} {self.command} {self.path} {args[1] if len(args) > 1 else ''}")


if __name__ == "__main__":
    if not TOKEN:
        raise SystemExit("BIFROST_PROXY_TOKEN is empty")
    if not VIRTUAL_KEY:
        raise SystemExit("BIFROST_VIRTUAL_KEY is empty")
    ThreadingHTTPServer(("127.0.0.1", 8081), Handler).serve_forever()
