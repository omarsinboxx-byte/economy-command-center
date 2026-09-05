#!/usr/bin/env python3
"""Refresh public economy and market data for Economy Command Center.

Public-only data. Personal finance values never belong in this script or repo.
If one provider fails, the last good value remains and status.json records it.
"""
from __future__ import annotations

import csv
import io
import json
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

FRED_SERIES = {
    "CPIAUCSL": "Consumer Price Index",
    "UNRATE": "Unemployment Rate",
    "PAYEMS": "Total Nonfarm Payrolls",
    "ICSA": "Initial Jobless Claims",
    "DFF": "Effective Fed Funds Rate",
    "DGS3MO": "3-Month Treasury Yield",
    "DGS1": "1-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "DGS10": "10-Year Treasury Yield",
    "MORTGAGE30US": "30-Year Mortgage Rate",
    "HOUST": "Housing Starts",
    "DCOILWTICO": "WTI Crude Oil",
    "DTWEXBGS": "Broad U.S. Dollar Index",
    "VIXCLS": "VIX",
}

YAHOO_FUTURES = {
    "CL": ("CL=F", "WTI Crude Oil", "Energy"),
    "BZ": ("BZ=F", "Brent Crude Oil", "Energy"),
    "NG": ("NG=F", "Natural Gas", "Energy"),
    "RB": ("RB=F", "RBOB Gasoline", "Energy"),
    "HO": ("HO=F", "Heating Oil / ULSD", "Energy"),
    "GC": ("GC=F", "Gold", "Metals"),
    "SI": ("SI=F", "Silver", "Metals"),
    "HG": ("HG=F", "Copper", "Metals"),
    "PL": ("PL=F", "Platinum", "Metals"),
    "ES": ("ES=F", "S&P 500 E-mini", "Equity Index"),
    "NQ": ("NQ=F", "Nasdaq-100 E-mini", "Equity Index"),
    "YM": ("YM=F", "Dow E-mini", "Equity Index"),
    "RTY": ("RTY=F", "Russell 2000 E-mini", "Equity Index"),
    "ZT": ("ZT=F", "2-Year Treasury Note", "Rates & FX"),
    "ZN": ("ZN=F", "10-Year Treasury Note", "Rates & FX"),
    "ZB": ("ZB=F", "30-Year Treasury Bond", "Rates & FX"),
    "DX": ("DX-Y.NYB", "U.S. Dollar Index", "Rates & FX"),
    "ZC": ("ZC=F", "Corn", "Agriculture"),
    "ZW": ("ZW=F", "Wheat", "Agriculture"),
    "ZS": ("ZS=F", "Soybeans", "Agriculture"),
}

UA = {"User-Agent": "EconomyCommandCenter/1.1 (+https://github.com/omarsinboxx-byte/economy-command-center)"}

def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

def load_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def save_json(path: Path, obj) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=False) + "\n", encoding="utf-8")

def get_text(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="replace")

def get_json(url: str, timeout: int = 25):
    return json.loads(get_text(url, timeout=timeout))

def fred_latest(series_id: str):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={urllib.parse.quote(series_id)}"
    rows = list(csv.DictReader(io.StringIO(get_text(url))))
    good = []
    for row in rows:
        raw = (row.get(series_id) or "").strip()
        if raw in {"", "."}:
            continue
        try:
            good.append((row.get("DATE") or row.get("observation_date"), float(raw)))
        except ValueError:
            pass
    if not good:
        raise RuntimeError(f"No observations for {series_id}")
    latest = good[-1]
    previous = good[-2] if len(good) > 1 else latest
    history = [{"date": d, "value": v} for d, v in good[-120:]]
    return latest, previous, history, url

def yahoo_latest(yahoo_symbol: str):
    q = urllib.parse.quote(yahoo_symbol, safe="")
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{q}?range=10d&interval=1d&includePrePost=false&events=div%2Csplits"
    result = get_json(url)["chart"]["result"][0]
    ts = result.get("timestamp") or []
    quote = (result.get("indicators", {}).get("quote") or [{}])[0]
    points = []
    for i, epoch in enumerate(ts):
        closes = quote.get("close") or []
        close = closes[i] if i < len(closes) else None
        if close is None:
            continue
        def item(name):
            arr = quote.get(name) or []
            return float(arr[i]) if i < len(arr) and arr[i] is not None else None
        points.append({
            "date": datetime.fromtimestamp(epoch, timezone.utc).date().isoformat(),
            "latest": float(close),
            "open": item("open"), "high": item("high"), "low": item("low"), "volume": item("volume"),
        })
    if not points:
        raise RuntimeError(f"No observations for {yahoo_symbol}")
    latest = points[-1].copy()
    latest["previous"] = points[-2]["latest"] if len(points) > 1 else latest["latest"]
    return latest, points, url

def refresh_economy(status):
    path = DATA / "economy.json"
    store = load_json(path, {"updated": None, "series": {}})
    errors, updated = [], 0
    for sid, name in FRED_SERIES.items():
        try:
            latest, previous, history, source = fred_latest(sid)
            store["series"][sid] = {
                "id": sid, "name": name, "date": latest[0], "latest": latest[1], "previous": previous[1],
                "history": history, "source": source, "lastChecked": now_iso(), "status": "current",
            }
            updated += 1
        except Exception as exc:
            errors.append(f"{sid}: {exc}")
            old = store["series"].get(sid, {})
            old.update({"lastChecked": now_iso(), "status": "warning", "error": str(exc)})
            store["series"][sid] = old
        time.sleep(0.10)
    store["updated"] = now_iso()
    save_json(path, store)
    status["datasets"]["economy"] = {"status": "ok" if not errors else "partial", "lastChecked": now_iso(), "updatedItems": updated, "errors": errors}

def refresh_futures(status):
    path = DATA / "futures.json"
    store = load_json(path, {"updated": None, "contracts": {}})
    errors, updated = [], 0
    for symbol, (ysym, name, category) in YAHOO_FUTURES.items():
        try:
            latest, history, source = yahoo_latest(ysym)
            store["contracts"][symbol] = {
                "symbol": symbol, "providerSymbol": ysym, "name": name, "category": category, **latest,
                "history": history[-60:], "source": source, "lastChecked": now_iso(), "status": "current",
            }
            updated += 1
        except Exception as exc:
            errors.append(f"{symbol}: {exc}")
            old = store["contracts"].get(symbol, {})
            old.update({"lastChecked": now_iso(), "status": "warning", "error": str(exc)})
            store["contracts"][symbol] = old
        time.sleep(0.18)
    store["updated"] = now_iso()
    save_json(path, store)
    status["datasets"]["futures"] = {"status": "ok" if not errors else "partial", "lastChecked": now_iso(), "updatedItems": updated, "errors": errors}

def refresh_rates(status):
    path = DATA / "rates.json"
    store = load_json(path, {"updated": None, "rates": {}})
    economy = load_json(DATA / "economy.json", {"series": {}}).get("series", {})
    mapping = {"3-Month Treasury": "DGS3MO", "1-Year Treasury": "DGS1", "2-Year Treasury": "DGS2", "30-Year Mortgage": "MORTGAGE30US"}
    updated = 0
    for name, sid in mapping.items():
        src = economy.get(sid) or {}
        if src.get("latest") is not None:
            store["rates"][name] = {"name": name, "rate": src["latest"], "date": src.get("date"), "source": src.get("source"), "lastChecked": now_iso(), "status": "current"}
            updated += 1
    store["updated"] = now_iso()
    save_json(path, store)
    status["datasets"]["rates"] = {"status": "ok", "lastChecked": now_iso(), "updatedItems": updated, "errors": [], "note": "HYSA/CD/card/auto/HELOC stay as reference snapshots until a durable provider is configured."}

def main():
    status_path = DATA / "status.json"
    status = {"startedAt": now_iso(), "datasets": {}}
    refresh_economy(status)
    refresh_futures(status)
    refresh_rates(status)
    status["updated"] = now_iso(); status["completedAt"] = now_iso()
    states = [x.get("status") for x in status["datasets"].values()]
    status["overall"] = "ok" if states and all(x == "ok" for x in states) else "partial"
    save_json(status_path, status)
    print(json.dumps(status, indent=2))

if __name__ == "__main__":
    main()
