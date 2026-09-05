#!/usr/bin/env python3
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')

# Keep this project focused on economy, markets, rates and catalysts.
# Remove the retirement page, navigation entries and its active runtime hooks.
s=re.sub(r'\n\s*<button class="nav-btn" data-page="retirement">.*?</button>','',s,count=1,flags=re.S)
s=re.sub(r'\n\s*<button data-page="retirement">.*?</button>','',s,count=1,flags=re.S)
s=re.sub(
    r'\n\s*<section class="page" id="page-retirement">.*?</section>\s*(?=<section class="page" id="page-rates">)',
    '\n\n    ',s,count=1,flags=re.S
)
s=s.replace(",retirement:['LONG-TERM PLAN','Retirement & Financial Freedom']",'')
s=s.replace(
    "function setPage(page){state.page=page;",
    "function setPage(page){if(page==='retirement')page='summary';state.page=page;"
)
s=s.replace(
    'function recalcAll(){recalcEconomy();recalcRetirement();recalcRates();',
    'function recalcAll(){recalcEconomy();recalcRates();'
)
s=s.replace("if(state.page==='retirement')recalcRetirement();",'')
s=re.sub(r'function calcRetirement\(ageTarget\)\{.*?(?=function renderRates\(\))','',s,count=1,flags=re.S)
s=re.sub(
    r";\$\('#retireReset'\)\.addEventListener\('click',\(\)=>\{.*?toast\('Retirement model reset\.'\)\}\)",
    '',s,count=1,flags=re.S
)
s=s.replace("Object.entries(state.retire).forEach(([field,value])=>rows.push({section:'retirement',field,value}));",'')
s=s.replace("const retirement=Object.entries(state.retire).map(([Field,Value])=>({Field,Value}));",'')
s=s.replace("XLSX.utils.book_append_sheet(wb,XLSX.utils.json_to_sheet(retirement),'Retirement');",'')

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
print('Dashboard wiring is ready; retirement page removed.')
