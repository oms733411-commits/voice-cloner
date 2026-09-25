import json
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FOUND_RE = re.compile(r"^\[\+\]\s*(.*?):\s*(https?://\S+)\s*$")


def run_sherlock(username, variants=False):
    target = username + "{?}" if variants else username
    cmd = [
        sys.executable, "-m", "sherlock_project", target,
        "--print-found", "--no-color", "--timeout", "12",
    ]
    p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    results, seen = [], set()
    for line in p.stdout.splitlines():
        match = FOUND_RE.match(line.strip())
        if match:
            url = match.group(2).strip()
            if url not in seen:
                seen.add(url)
                results.append({"site": match.group(1).strip(), "url": url})
    return p, results


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
            data = json.loads(self.rfile.read(length) or b"{}")
            username = str(data.get("username", "")).strip()
            variants = bool(data.get("variants", False))

            if not USERNAME_RE.fullmatch(username):
                return self._send(400, {"error": "Invalid username."})

            try:
                p, results = run_sherlock(username, variants)
            except subprocess.TimeoutExpired:
                return self._send(504, {"error": "Search timed out. Try again later."})

            if p.returncode != 0 and not results:
                detail = (p.stderr or p.stdout).strip().splitlines()
                return self._send(502, {
                    "error": detail[-1] if detail else "Sherlock returned no results."
                })

            return self._send(200, {
                "username": username,
                "variants_checked": variants,
                "results": results
            })

        except json.JSONDecodeError:
            return self._send(400, {"error": "Invalid JSON request."})
        except Exception as exc:
            return self._send(500, {"error": f"Server error: {exc}"})
