# Sherlock UI

This repo now includes a clean web UI around the official Sherlock Project.

## Run locally

PowerShell:

    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    py -m pip install -r requirements.txt
    py sherlock_server.py

Open:

    http://127.0.0.1:5000

The UI accepts one username and sends it to the local Sherlock process. It displays public username matches returned by Sherlock.

Sherlock is open source under the MIT license:
https://github.com/sherlock-project/sherlock

The web UI is intentionally separate from the existing index.html game so the current site is not broken.
