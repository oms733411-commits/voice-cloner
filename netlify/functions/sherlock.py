import json
import os
import re
import subprocess
import sys

USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{1,80}$")
FOUND_RE = re.compile(r"^\[\+\]\s*(.*?):\s*(https?://\S+)\s*$")

def handler(event, context):
    try:
        body = json.loads(event.get("body") or "{}")
        username = str(body.get("username", "")).strip()
        if not USERNAME_RE.fullmatch(username):
            return {"statusCode":400,"headers":{"Content-Type":"application/json"},"body":json.dumps({"error":"Invalid username."})}
        cmd=[sys.executable,"-m","sherlock_project",username,"--print-found","--no-color","--timeout","15"]
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=180)
        results=[]; seen=set()
        for line in p.stdout.splitlines():
            m=FOUND_RE.match(line.strip())
            if m and m.group(2) not in seen:
                seen.add(m.group(2)); results.append({"site":m.group(1).strip(),"url":m.group(2).strip()})
        if p.returncode != 0 and not results:
            detail=(p.stderr or p.stdout).strip().splitlines()
            return {"statusCode":502,"headers":{"Content-Type":"application/json"},"body":json.dumps({"error":detail[-1] if detail else "Sherlock returned no results."})}
        return {"statusCode":200,"headers":{"Content-Type":"application/json"},"body":json.dumps({"username":username,"results":results})}
    except subprocess.TimeoutExpired:
        return {"statusCode":504,"headers":{"Content-Type":"application/json"},"body":json.dumps({"error":"Search timed out. Try again later."})}
    except Exception as exc:
        return {"statusCode":500,"headers":{"Content-Type":"application/json"},"body":json.dumps({"error":str(exc)})}
