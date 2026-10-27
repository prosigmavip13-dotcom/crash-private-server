from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))

player = {
    "player_id": "test-player",
    "level": 1,
    "wumpa_fruit": 0
}

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({})

    def do_GET(self):
        if self.path == "/health":
            self.send_json({
                "status": "ok",
                "server": "CrashPrivateServer",
                "version": 2
            })
        elif self.path == "/api/v1/player":
            self.send_json(player)
        else:
            self.send_json({"error": "not_found"}, 404)

    def do_POST(self):
        global player

        if self.path != "/api/v1/player":
            self.send_json({"error": "not_found"}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))

            if "level" in data:
                player["level"] = max(1, min(int(data["level"]), 10000))

            if "wumpa_fruit" in data:
                player["wumpa_fruit"] = max(
                    0, min(int(data["wumpa_fruit"]), 100000000)
                )

            self.send_json(player)

        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_json({"error": "invalid_data"}, 400)

    def log_message(self, format, *args):
        print(format % args)

print(f"CrashPrivateServer listening on port {PORT}")
HTTPServer((HOST, PORT), Handler).serve_forever()
