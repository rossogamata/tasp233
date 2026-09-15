import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class ApiHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_json({"status": "ok"})
            return

        if self.path == "/api/message":
            self.send_json({"message": os.getenv("APP_MESSAGE", "Hello from API")})
            return

        self.send_error(404, "Not found")

    def send_json(self, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return


HTTPServer(("0.0.0.0", 8000), ApiHandler).serve_forever()
