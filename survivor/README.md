# SURVIVOR

An autonomous meme-coin trading bot that starts with $20 USDC and tries to survive. Its equity is shown as a cyberpunk city: $1 = 1 citizen.

> **Read this first.** Most meme coins lose money, and the research in `RESEARCH.md` says most meme-coin trading strategies lose after fees. Any result on a $20 account is statistically noisy for a long time. Only fund the bot with money you can afford to lose completely.

## Quick start (Windows)

```powershell
cd survivor
.\run.ps1        # installs on first run (Python via winget if missing), then starts in the background
.\status.ps1     # running? last heartbeat, limits, recent log lines
.\stop.ps1       # emergency stop: creates KILL, waits for a clean exit, then force-stops
```

If PowerShell blocks the scripts, allow local scripts once for your user:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Safety rules (enforced in code)

| Rule | Where |
|---|---|
| Max 15% of equity per trade, max 3 open positions, 25% daily loss -> 24 h pause | `core/risk/limits.py` (config can only tighten these; tests in `tests/test_risk_limits.py`) |
| Emergency stop: `KILL` file checked every second | `core/killswitch.py`, `stop.ps1` |
| One bot per machine (no duplicate orders) | `core/singleton.py` |
| Burner wallet only, balance cap, no transfers out, key encrypted with DPAPI | milestone 2 |
| Simulate the sell before every buy (honeypot check) | milestone 2 |

The learning engine may tune strategy parameters. It cannot change the files above, spawn copies of itself, or install software.

## Layout

```
install.ps1 run.ps1 stop.ps1 status.ps1   PowerShell control scripts
config.json                                settings (risk values here can only be stricter than the hard limits)
core/        Python trading core (chains, data, screening, strategies, risk, execution, learning, ledger)
city/        cyberpunk dashboard (milestone 4)
reports/     daily summaries
data/        runtime state: ledger, logs, status, encrypted key (git-ignored)
tests/       pytest suite: .venv\Scripts\python -m pytest
```

## Milestones

1. **Research and skeleton** (this): `RESEARCH.md`, control scripts, main loop, locked risk limits, tests.
2. Data clients, screening, burner wallet, live and shadow execution, SQLite ledger, one tiny real test swap.
3. Strategy plug-ins, risk module, learning engine, daily reports.
4. City dashboard wired to the live ledger.
5. Strategy forks and districts.
