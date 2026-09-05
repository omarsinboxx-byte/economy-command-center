#!/usr/bin/env python3
"""Build a standalone offline HTML snapshot.

When the modular dashboard is present, this script embeds the latest public JSON
inside the HTML so the offline copy can still display the most recent snapshot.
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "offline" / "Finance_Command_Center_Offline.html"
OUT.parent.mkdir(exist_ok=True)


def load(name, default):
    path = DATA / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def main():
    payload = {
        "economy": load("economy.json", {"series": {}}),
        "futures": load("futures.json", {"contracts": {}}),
        "rates": load("rates.json", {"rates": {}}),
        "calendar": load("calendar.json", {"events": []}),
        "status": load("status.json", {}),
    }
    index = ROOT / "index.html"
    if index.exists():
        source = index.read_text(encoding="utf-8")
        marker = "</head>"
        embedded = (
            '<script id="offline-public-data" type="application/json">'
            + json.dumps(payload).replace("</", "<\\/")
            + "</script>\n"
        )
        if marker in source:
            source = source.replace(marker, embedded + marker, 1)
        else:
            source = embedded + source
        source = source.replace(
            "<html lang=\"en\"",
            "<html lang=\"en\" data-offline=\"true\"",
            1,
        )
        OUT.write_text(source, encoding="utf-8")
    else:
        # Temporary fallback until index.html is added.
        stamp = payload.get("status", {}).get("completedAt") or "No refresh yet"
        page = f'''<!doctype html>
<html lang="en" data-offline="true"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Economy Command Center — Offline</title>
<style>body{{font-family:system-ui;background:#0b1220;color:#edf4ff;padding:40px;max-width:900px;margin:auto}}.card{{padding:24px;border:1px solid #28405e;border-radius:18px;background:#101b2d}}small{{color:#9fb0c8}}</style></head>
<body><div class="card"><h1>Economy Command Center</h1><p>Offline snapshot foundation is ready.</p><small>Last build: {html.escape(str(stamp))}</small><p>The full dashboard shell will appear here after index.html is committed.</p></div></body></html>'''
        OUT.write_text(page, encoding="utf-8")
    print(f"Built {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
