from flask import Flask, jsonify, request, send_from_directory
import subprocess, sys, re

app = Flask(__name__, static_folder=".")
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FOUND_RE = re.compile(r"^\[\+\]\s*(.*?):\s*(https?://\S+)\s*$")

@app.get("/")
def home():
    return send_from_directory(".", "sherlock.html")

@app.post("/api/sherlock")
def search():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    if not USERNAME_RE.fullmatch(username):
        return jsonify(error="Invalid username."), 400
    cmd = [sys.executable, "-m", "sherlock_project", username, "--print-found", "--no-color", "--timeout", "15"]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except subprocess.TimeoutExpired:
        return jsonify(error="Search timed out. Try again later."), 504
    except Exception as exc:
        return jsonify(error=f"Could not start Sherlock: {exc}"), 500
    results=[]
    for line in p.stdout.splitlines():
        m=FOUND_RE.match(line.strip())
        if m: results.append({"site":m.group(1).strip(),"url":m.group(2).strip()})
    unique=[]; seen=set()
    for item in results:
        if item["url"] not in seen:
            seen.add(item["url"]); unique.append(item)
    if p.returncode != 0 and not unique:
        detail=(p.stderr or p.stdout).strip().splitlines()
        return jsonify(error=detail[-1] if detail else "Sherlock returned no results."),502
    return jsonify(username=username,results=unique)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
