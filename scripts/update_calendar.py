#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'; DATA.mkdir(exist_ok=True)
EVENTS=[
('2026-09-10','08:30','High','PPI — August 2026','BLS Producer Price Index'),
('2026-09-11','08:30','High','CPI — August 2026','BLS Consumer Price Index'),
('2026-09-16','','High','FOMC policy decision','FOMC meeting Sep 15–16'),
('2026-09-16','08:30','High','Retail Sales — August 2026','Census advance retail sales'),
('2026-09-17','08:30','Medium','Housing Starts — August 2026','Census/HUD new residential construction'),
('2026-09-29','10:00','Medium','JOLTS — August 2026','BLS Job Openings and Labor Turnover'),
('2026-09-30','08:30','High','GDP Q2 — Third Estimate','BEA GDP'),
('2026-09-30','08:30','High','PCE / Personal Income & Outlays — August 2026','BEA PCE inflation'),
('2026-10-02','08:30','High','Employment Situation — September 2026','BLS payrolls and unemployment'),
('2026-10-14','08:30','High','CPI — September 2026','BLS Consumer Price Index'),
('2026-10-15','08:30','High','PPI — September 2026','BLS Producer Price Index'),
('2026-10-15','08:30','High','Retail Sales — September 2026','Census advance retail sales'),
('2026-10-20','08:30','Medium','Housing Starts — September 2026','Census/HUD new residential construction'),
('2026-10-28','','High','FOMC policy decision','FOMC meeting Oct 27–28'),
('2026-10-29','08:30','High','GDP Q3 — Advance Estimate','BEA GDP'),
('2026-10-29','08:30','High','PCE / Personal Income & Outlays — September 2026','BEA PCE inflation'),
('2026-11-03','10:00','Medium','JOLTS — September 2026','BLS Job Openings and Labor Turnover'),
('2026-11-06','08:30','High','Employment Situation — October 2026','BLS payrolls and unemployment'),
('2026-11-10','08:30','High','CPI — October 2026','BLS Consumer Price Index'),
('2026-11-13','08:30','High','PPI — October 2026','BLS Producer Price Index'),
('2026-11-17','08:30','High','Retail Sales — October 2026','Census advance retail sales'),
('2026-11-18','08:30','Medium','Housing Starts — October 2026','Census/HUD new residential construction'),
('2026-11-25','08:30','High','GDP Q3 — Second Estimate','BEA GDP'),
('2026-11-25','08:30','High','PCE / Personal Income & Outlays — October 2026','BEA PCE inflation'),
('2026-12-01','10:00','Medium','JOLTS — October 2026','BLS Job Openings and Labor Turnover'),
('2026-12-04','08:30','High','Employment Situation — November 2026','BLS payrolls and unemployment'),
('2026-12-09','','High','FOMC policy decision','FOMC meeting Dec 8–9'),
('2026-12-10','08:30','High','CPI — November 2026','BLS Consumer Price Index'),
('2026-12-15','08:30','High','PPI — November 2026','BLS Producer Price Index'),
('2026-12-16','08:30','High','Retail Sales — November 2026','Census advance retail sales'),
('2026-12-17','08:30','Medium','Housing Starts — November 2026','Census/HUD new residential construction'),
('2026-12-23','08:30','High','GDP Q3 — Third Estimate','BEA GDP'),
('2026-12-23','08:30','High','PCE / Personal Income & Outlays — November 2026','BEA PCE inflation'),
]
stamp=datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00','Z')
events=[{'id':f'econ-{d}-{i}','uid':f'econ-{d}-{i}@economy-command-center','date':d,'start':t,'end':'','type':'economic','importance':imp,'ticker':'','title':title,'location':'','notes':notes} for i,(d,t,imp,title,notes) in enumerate(EVENTS,1)]
(DATA/'calendar.json').write_text(json.dumps({'updated':stamp,'coverageThrough':max(e['date'] for e in events),'events':events},indent=2)+'\n',encoding='utf-8')
print(f'Wrote {len(events)} economic calendar events.')