#!/usr/bin/env python3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')
if 'id="publicDataStatus"' not in s:
    old='''    <div class="side-foot">
      <div class="mini">Autosaves locally in your browser. No account required.</div>
      <div class="mini" id="lastSaved">Last saved: —</div>
    </div>'''
    new='''    <div class="side-foot">
      <div class="mini" id="publicDataStatus">Public data: loading…</div>
      <div class="mini" id="publicDataTime">Last public refresh: —</div>
      <div class="mini" id="lastSaved">Last saved: —</div>
    </div>'''
    if old not in s: raise SystemExit('sidebar anchor not found')
    s=s.replace(old,new,1)
if '.mini.public-ok{' not in s:
    anchor='.data-status i{width:7px;height:7px;border-radius:50%;background:var(--good);box-shadow:0 0 0 4px rgba(82,225,164,.08)}'
    add=anchor+'.mini.public-ok{border-color:rgba(82,225,164,.28);color:var(--good)}.mini.public-warn{border-color:rgba(255,208,111,.30);color:var(--warn)}.mini.public-offline{border-color:rgba(111,179,255,.28);color:var(--info)}'
    if anchor not in s: raise SystemExit('css anchor not found')
    s=s.replace(anchor,add,1)
if 'window.__FCC_STATE=state;' not in s:
    if 'let state=load();' not in s: raise SystemExit('state anchor not found')
    s=s.replace('let state=load();','let state=load();window.__FCC_STATE=state;',1)
if '<script src="auto-data.js"></script>' not in s:
    if '</body>' not in s: raise SystemExit('body anchor not found')
    s=s.replace('</body>','<script src="auto-data.js"></script>\n</body>',1)
if '<link rel="stylesheet" href="summary-plus.css">' not in s:
    if '</head>' not in s: raise SystemExit('head anchor not found')
    s=s.replace('</head>','<link rel="stylesheet" href="summary-plus.css">\n</head>',1)
if '<script src="summary-plus.js"></script>' not in s:
    if '<script src="auto-data.js"></script>' in s:
        s=s.replace('<script src="auto-data.js"></script>','<script src="summary-plus.js"></script>\n<script src="auto-data.js"></script>',1)
    elif '</body>' in s:
        s=s.replace('</body>','<script src="summary-plus.js"></script>\n</body>',1)
    else:
        raise SystemExit('summary script anchor not found')
p.write_text(s,encoding='utf-8')
print('Dashboard public-data and Summary Plus wiring is ready.')
