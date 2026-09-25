import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FOUND_RE = re.compile(r"^\[\+\]\s*(.*?):\s*(https?://\S+)\s*$")


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self._send(204, {})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw or b"{}")
            username = str(data.get("username", "")).strip()

            if not USERNAME_RE.fullmatch(username):
                return self._send(400, {"error": "Invalid username."})

            cmd = [
                sys.executable,
                "-m",
                "sherlock_project",
                username,
                "--print-found",
                "--no-color",
                "--timeout",
                "8",
            ]

            try:
                p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            except subprocess.TimeoutExpired:
                return self._send(504, {"error": "Search timed out. Try again later."})

            results = []
            seen = set()

            for line in p.stdout.splitlines():
                match = FOUND_RE.match(line.strip())
                if match:
                    url = match.group(2).strip()
                    if url not in seen:
                        seen.add(url)
                        results.append({
                            "site": match.group(1).strip(),
                            "url": url,
                        })

            if p.returncode != 0 and not results:
                detail = (p.stderr or p.stdout).strip().splitlines()
                return self._send(
                    502,
                    {"error": detail[-1] if detail else "Sherlock returned no results."},
                )

            return self._send(200, {"username": username, "results": results})

        except json.JSONDecodeError:
            return self._send(400, {"error": "Invalid JSON request."})
        except Exception as exc:
            return self._send(500, {"error": f"Server error: {exc}"})
