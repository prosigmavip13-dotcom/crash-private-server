
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
import json
import os

HOST = "0.0.0.0"
PORT = int(os.environ.get("PORT", "8080"))
DATA_FILE = "players.json"

def load_player():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return {
            "player_id": "test-player",
            "level": 1,
            "wumpa_fruit": 0
        }

player = load_player()

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        path = urlparse(self.path).path.rstrip("/") or "/"
        print(f"GET {path}", flush=True)

        if path == "/":
            self.send_json({
                "status": "ok",
                "server": "CrashPrivateServer",
                "message": "Server is running",
                "endpoints": ["/health", "/api/v1/player"]
            })
        elif path == "/health":
            self.send_json({
                "status": "ok",
                "server": "CrashPrivateServer",
                "version": 3
            })
        elif path == "/api/v1/player":
            self.send_json(player)
        else:
            self.send_json({"error": "not_found", "path": path}, 404)

    def do_POST(self):
        global player
        path = urlparse(self.path).path.rstrip("/") or "/"
        print(f"POST {path}", flush=True)

        if path != "/api/v1/player":
            self.send_json({"error": "not_found", "path": path}, 404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length))

            if not isinstance(data, dict):
                raise ValueError("Expected a JSON object")

            if "level" in data:
                player["level"] = max(1, min(int(data["level"]), 10000))

            if "wumpa_fruit" in data:
                player["wumpa_fruit"] = max(
                    0, min(int(data["wumpa_fruit"]), 100000000)
                )

            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(player, f, ensure_ascii=False)

            self.send_json(player)

        except (ValueError, TypeError, json.JSONDecodeError):
            self.send_json({"error": "invalid_data"}, 400)

    def log_message(self, format, *args):
        print(format % args, flush=True)

print(f"CrashPrivateServer v3 listening on port {PORT}", flush=True)
ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()
