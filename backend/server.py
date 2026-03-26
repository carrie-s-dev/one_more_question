#!/usr/bin/env python3
"""Tiny Ollama proxy for One More Question (no Node required)."""

import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

PORT = int(os.environ.get("PORT", "3000"))
OLLAMA_BASE = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434").rstrip("/")
DEFAULT_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
# Comma-separated origins, or * (default)
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "*")


def _cors_headers(handler: BaseHTTPRequestHandler) -> None:
    if FRONTEND_ORIGIN.strip() == "*":
        handler.send_header("Access-Control-Allow-Origin", "*")
    else:
        origin = handler.headers.get("Origin") or ""
        allowed = [o.strip() for o in FRONTEND_ORIGIN.split(",") if o.strip()]
        if origin in allowed:
            handler.send_header("Access-Control-Allow-Origin", origin)
        elif allowed:
            handler.send_header("Access-Control-Allow-Origin", allowed[0])
        else:
            handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:
        # Quieter logs
        print(f"{self.address_string()} - {fmt % args}")

    def do_OPTIONS(self) -> None:
        self.send_response(204)
        _cors_headers(self)
        self.end_headers()

    def do_GET(self) -> None:
        if self.path in ("/health", "/api/health"):
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            _cors_headers(self)
            self.end_headers()
            self.wfile.write(b'{"ok":true,"service":"one-more-question-backend-py"}')
            return
        self.send_response(404)
        self.end_headers()

    def do_POST(self) -> None:
        if self.path != "/api/ask":
            self.send_response(404)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            self._json(400, {"error": "Invalid JSON"})
            return

        prompt = (data.get("prompt") or "").strip()
        model = (data.get("model") or DEFAULT_MODEL).strip()
        if not prompt:
            self._json(400, {"error": "Missing prompt"})
            return

        body = json.dumps(
            {"model": model, "prompt": prompt, "stream": False}
        ).encode("utf-8")
        req = urllib.request.Request(
            f"{OLLAMA_BASE}/api/generate",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                ollama_raw = resp.read()
            ollama_data = json.loads(ollama_raw.decode("utf-8"))
            text = ollama_data.get("response") or ""
            self._json(200, {"response": text})
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8", errors="replace")
            self._json(502, {"error": f"Ollama HTTP {e.code}: {err_body}"})
        except urllib.error.URLError as e:
            self._json(502, {"error": f"Cannot reach Ollama at {OLLAMA_BASE}: {e.reason}"})
        except Exception as e:
            self._json(500, {"error": str(e)})

    def _json(self, code: int, payload: dict) -> None:
        b = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        _cors_headers(self)
        self.end_headers()
        self.wfile.write(b)


if __name__ == "__main__":
    print(f"Kid Explainer backend → Ollama at {OLLAMA_BASE}")
    print(f"Listening on http://127.0.0.1:{PORT}  (POST /api/ask, GET /health)")
    HTTPServer(("", PORT), Handler).serve_forever()
