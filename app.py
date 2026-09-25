from flask import Flask, jsonify, request, send_from_directory
import subprocess, sys, re

app = Flask(__name__, static_folder=".")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FOUND_RE = re.compile(r"^\[\+\]\s*(.*?):\s*(https?://\S+)\s*$")

@app.get("/")
def home():
    return send_from_directory(".", "index.html")

@app.post("/api/sherlock")
def search():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    variants = bool(data.get("variants", False))
    if not USERNAME_RE.fullmatch(username):
        return jsonify(error="Invalid username."), 400
    target = username + "{?}" if variants else username
    cmd = [sys.executable, "-m", "sherlock_project", target, "--print-found", "--no-color", "--timeout", "12"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except subprocess.TimeoutExpired:
        return jsonify(error="Search timed out. Try again later."), 504
    except Exception as exc:
        return jsonify(error=f"Could not start Sherlock: {exc}"), 500
    results, seen = [], set()
    for line in p.stdout.splitlines():
        m = FOUND_RE.match(line.strip())
        if m:
            url = m.group(2).strip()
            if url not in seen:
                seen.add(url)
                results.append({"site": m.group(1).strip(), "url": url})
    if p.returncode != 0 and not results:
        detail = (p.stderr or p.stdout).strip().splitlines()
        return jsonify(error=detail[-1] if detail else "Sherlock returned no results."), 502
    return jsonify(username=username, variants_checked=variants, results=results)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
