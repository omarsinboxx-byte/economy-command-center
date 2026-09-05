# Economy Command Center

A local-first economy, markets, rates, retirement and event dashboard.

## Design goals

- Public economic and market data refresh automatically on GitHub Actions.
- The hosted dashboard reads versioned JSON from `/data`.
- A standalone offline HTML snapshot is generated from the same project.
- Personal financial inputs stay in the browser and are **not committed to GitHub**.
- Every data source carries an observation date, last-checked time and health status.

## Project layout

```text
index.html                 Dashboard shell
assets/style.css           Glass UI / responsive styles
assets/app.js              Dashboard, charts, calendar and local settings
data/economy.json          Macro indicators and history
data/futures.json          Daily futures/market snapshot
data/rates.json            Rate benchmarks
data/calendar.json         Economic calendar events
data/status.json           Data-health metadata
scripts/update_data.py     Daily public-data refresh
scripts/build_offline.py   Builds standalone offline HTML
offline/                   Generated offline snapshot
.github/workflows/         Scheduled refresh/deployment workflows
```

## Privacy

Do not commit salary, account balances, debts, retirement balances, tax documents, account numbers, credentials, API secrets or other private financial information. Personal dashboard fields are stored locally in the browser and can be exported/imported separately.

## Refresh policy

The scheduled workflow checks public data daily. Daily series update when a new market observation is available; monthly/weekly indicators remain marked current until their next official release.

## Offline copy

`offline/Finance_Command_Center_Offline.html` is generated from the same dashboard and embeds the most recent public-data snapshot. It can be opened without a server or internet connection.
