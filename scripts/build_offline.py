#!/usr/bin/env python3
"""Build a standalone offline HTML snapshot with public data embedded."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
OUT=ROOT/'offline'/'Finance_Command_Center_Offline.html'
OUT.parent.mkdir(exist_ok=True)

def load(name,default):
    try:return json.loads((DATA/name).read_text(encoding='utf-8'))
    except Exception:return default

payload={
    'economy':load('economy.json',{'series':{}}),
    'futures':load('futures.json',{'contracts':{}}),
    'rates':load('rates.json',{'rates':{}}),
    'calendar':load('calendar.json',{'events':[]}),
    'status':load('status.json',{}),
}
source=(ROOT/'index.html').read_text(encoding='utf-8')
embedded='<script id="offline-public-data" type="application/json">'+json.dumps(payload).replace('</','<\\/')+'</script>\n'
source=source.replace('</head>',embedded+'</head>',1)
summary_css=ROOT/'summary-plus.css'
if summary_css.exists():
    source=source.replace('<link rel="stylesheet" href="summary-plus.css">','<style>\n'+summary_css.read_text(encoding='utf-8')+'\n</style>')
summary_js=ROOT/'summary-plus.js'
if summary_js.exists():
    source=source.replace('<script src="summary-plus.js"></script>','<script>\n'+summary_js.read_text(encoding='utf-8')+'\n</script>')
auto=ROOT/'auto-data.js'
if auto.exists():
    source=source.replace('<script src="auto-data.js"></script>','<script>\n'+auto.read_text(encoding='utf-8')+'\n</script>')
source=source.replace('<html lang="en"','<html lang="en" data-offline="true"',1)
OUT.write_text(source,encoding='utf-8')
print(f'Built {OUT.relative_to(ROOT)}')
