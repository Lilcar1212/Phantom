# Tooling, Backtesting Methodology, Risk Management, Infrastructure, and Security for a Personal Crypto Trading Bot (2026)

Context: solo US developer, beginner-to-intermediate, ~$20 capital, favoring free/cheap tooling. Research date: 2026-10-06. GitHub stats were pulled live from the GitHub API (search_repositories) on 2026-10-06.

## 1. Open-source framework comparison (Freqtrade, Hummingbot, Jesse, OctoBot, CCXT, NautilusTrader, backtrader/vectorbt)

### Takeaway
Freqtrade is the most popular and most actively maintained full bot framework (55k stars, commits on the day checked) with free backtesting, dry-run, hyperopt, Telegram and web UI, and it officially supports Kraken spot; it does not list Coinbase. For a US user who wants Coinbase Advanced, Hummingbot has a Coinbase Advanced Trade connector, and CCXT (the library underneath most of these) can talk to both. Jesse's live trading is a paid plugin (~$899+), which rules it out at $20 capital. backtrader is effectively unmaintained (last push Aug 2024).

### Cited Findings
**GitHub snapshot (2026-10-06, GitHub API)** — [GitHub search API results for the eight repos](https://github.com/freqtrade/freqtrade)
| Repo | Stars | Language | License | Last push | Notes |
|---|---|---|---|---|---|
| freqtrade/freqtrade | 55,071 | Python | GPL-3.0 | 2026-10-06 | 30 open issues; active |
| ccxt/ccxt | 44,269 | Python (also JS/TS, C#, PHP, Go, Java, Rust) | MIT | 2026-10-06 | "unified trading API with more than 100 crypto exchanges and prediction markets" |
| nautechsystems/nautilus_trader | 29,658 | Rust (Python API) | LGPL-3.0 | 2026-10-06 | described as "Production-grade Rust-native trading engine with deterministic event-driven architecture" |
| mementum/backtrader | 23,406 | Python | GPL-3.0 | **2024-08-19** | Issues disabled; stale |
| hummingbot/hummingbot | 20,323 | Python | Apache-2.0 | 2026-10-06 | topics include market-making, hft, hyperliquid, ai-agents |
| polakowo/vectorbt | 9,284 | Python | "Other" (non-standard) | 2026-09-26 | vectorized backtesting library |
| jesse-ai/jesse | 8,614 | Python | MIT | 2026-10-05 | |
| Drakkar-Software/OctoBot | 6,681 | Python | GPL-3.0 | 2026-10-06 | describes itself as automating "AI, Grid, DCA and TradingView strategies on Binance, Hyperliquid and 15+ exchanges, with a simple interface"; topics include coinbase-bot, paper-trading, telegrambot |

Sources for each row: [freqtrade](https://github.com/freqtrade/freqtrade), [ccxt](https://github.com/ccxt/ccxt), [nautilus_trader](https://github.com/nautechsystems/nautilus_trader), [backtrader](https://github.com/mementum/backtrader), [hummingbot](https://github.com/hummingbot/hummingbot), [vectorbt](https://github.com/polakowo/vectorbt), [jesse](https://github.com/jesse-ai/jesse), [OctoBot](https://github.com/Drakkar-Software/OctoBot)

**Freqtrade**
- Officially supported spot exchanges: Binance, BingX, Bitget, Bybit EU, Bybit, Gate EU, Gate, HTX, Hyperliquid (DEX), Kraken, MyOKX, OKX; futures: Binance, Bitget, Bybit, Gate, Hyperliquid, Kraken, OKX; community-tested: Bitvavo, Kucoin. Coinbase is not listed. — [Freqtrade README](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/README.md)
- Features: backtesting, "Strategy Optimization by machine learning" (hyperopt), dry-run, built-in WebUI, Telegram control, FreqAI adaptive ML modeling, performance tracking. — [Freqtrade README](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/README.md)
- Requirements: Python 3.11+, git, TA-Lib, Docker recommended; minimal hardware "2GB RAM, 1GB disk space, 2vCPU." — [Freqtrade README](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/README.md)
- Built on CCXT; exchanges not officially listed may work via CCXT but are untested. — [Freqtrade exchange notes mirror](https://gitcode.com/GitHub_Trending/fr/freqtrade/blob/develop/docs/exchanges.md)
- Kraken in Freqtrade supports GTC/IOC/PO time-in-force and stoploss_on_exchange with stop-loss-market and stop-loss-limit. — [Freqtrade exchange notes mirror](https://gitcode.com/GitHub_Trending/fr/freqtrade/blob/develop/docs/exchanges.md)
- Has a built-in `lookahead-analysis` command and "protections" (see sections 2 and 4). — [lookahead-analysis docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/lookahead-analysis.md); [protections docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/includes/protections.md)

**Hummingbot**
- Has a Coinbase Advanced Trade spot connector (`coinbase_advanced_trade`), WebSocket-based, supports LIMIT orders; listed as v1.0 status and does not support "V2 Strategies." — [Hummingbot Coinbase page](https://hummingbot.org/exchanges/coinbase/)
- Has a Kraken spot connector (`kraken`). — [Hummingbot exchanges list](https://hummingbot.org/exchanges/)
- Orientation is market-making / high-frequency / arbitrage (repo description: "create and deploy high-frequency crypto trading bots"). — [hummingbot GitHub](https://github.com/hummingbot/hummingbot)

**Jesse**
- Backtesting is free/open source (MIT), but live and paper trading require an official paid plugin with a license key; reported prices: Basic Lifetime $899, Pro Lifetime $999. — [Gurubase: Can Jesse Trade Live?](https://gurubase.io/g/jesse/can-jesse-trade-live); [toolradar Jesse pricing](https://toolradar.com/tools/jesse/pricing); [Jesse live trade docs](https://docs.jesse.trade/docs/livetrade)
- Jesse supports Coinbase Spot (Coinbase Advanced), Binance, Bitget among others. — [Jesse exchange setup guide](https://docs.jesse.trade/docs/supported-exchanges/exchange-setup-guide)

**CCXT**
- Library, not a bot: unified API to 100+ exchanges in many languages; MIT license; very active. — [ccxt GitHub](https://github.com/ccxt/ccxt)
- CCXT itself publishes comparisons vs Freqtrade and vs Jesse (positioning CCXT as the lower-level building block). — [CCXT vs Freqtrade](https://docs.ccxt.com/docs/comparisons/ccxt-vs-freqtrade); [CCXT vs Jesse](https://docs.ccxt.com/docs/comparisons/ccxt-vs-jesse)

### Inferences
- **Recommended path for this user:** Freqtrade on Kraken (officially supported, US-accessible, lower entry fees than Coinbase per section 4) — free backtest + dry-run + hyperopt + Telegram out of the box. If the user insists on Coinbase Advanced, options are Hummingbot (official connector, but market-making-oriented and steeper learning curve), OctoBot (repo topics mention coinbase-bot), or a small custom script on CCXT.
- **Learning curve (qualitative, my assessment):** OctoBot (GUI, easiest) < Freqtrade (Python strategy class, good docs) < Jesse (clean API, but paid live) < Hummingbot (market-making concepts, connectors/controllers) < NautilusTrader (institutional-grade, Rust core, event-driven; overkill for $20). vectorbt is a research/backtest library (fast parameter sweeps) rather than a live bot; backtrader should be avoided for new projects given no pushes since Aug 2024.
- GPL-3.0 licensing (Freqtrade, OctoBot) is irrelevant for personal use but matters if code is redistributed.
- With $20, any paid tool (Jesse live plugin at $899) costs >40x the capital; free tools are the only rational choice.

### Gaps
- Exact latest release tags/dates were not retrieved (GitHub REST release endpoints were blocked in this session); "last push" dates are used as a maintenance proxy.
- Did not verify whether Freqtrade has added Coinbase Advanced in any form beyond "not listed" (the freqtrade.io docs site was blocked by the egress proxy).
- Did not verify current OctoBot exchange list for Coinbase/Kraken beyond repo topics, nor NautilusTrader's Coinbase/Kraken adapter status.
- Hummingbot's "does not support V2 Strategies" note for Coinbase may be outdated; not cross-checked.

## 2. Backtesting pitfalls specific to crypto and best practices

### Takeaway
The dominant risk is fooling yourself: running many hyperopt trials guarantees some "great" backtests by chance. Use tools that quantify this (Deflated Sharpe Ratio, Probability of Backtest Overfitting), check for lookahead bias explicitly (Freqtrade has a command for it), include delisted coins or restrict to majors, model fees realistically, test across regimes, then dry-run before going live.

### Cited Findings
- **Deflated Sharpe Ratio (DSR):** Bailey & López de Prado (2014, Journal of Portfolio Management) — corrects for selection bias under multiple testing and non-normal returns; DSR is the probability that the observed Sharpe of the selected strategy exceeds a benchmark, conditional on number of trials, the cross-sectional variance of trial Sharpes, and skewness/kurtosis of returns. — [SSRN 2460551](https://papers.ssrn.com/abstract=2460551)
- **Probability of Backtest Overfitting (PBO):** Bailey, Borwein, López de Prado & Zhu (Journal of Computational Finance, 2015) — estimates PBO via combinatorially symmetric cross-validation (CSCV). — [SSRN 2326253](https://papers.ssrn.com/abstract=2326253)
- David H. Bailey also publishes overfitting tools/papers. — [davidhbailey.com overfit tools](https://www.davidhbailey.com/dhbpapers/overfit-tools-at.pdf)
- **Lookahead bias tooling:** Freqtrade's `lookahead-analysis` runs a baseline backtest, then re-runs sliced backtests per entry/exit signal and compares dataframes for differing column values, reporting bias. Limitations: only checks signals that actually produced trades (false negatives possible); pairlist-dependent strategies and FreqAI targets give false positives; limit orders with custom price callbacks can cause false positives. — [Freqtrade lookahead-analysis docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/lookahead-analysis.md)
- **Survivorship bias:** defined as analyzing only assets that still exist; overstates returns, understates drawdowns, overestimates liquidity. — [CoinAPI glossary](https://www.coinapi.io/learn/glossary/survivorship-bias)
- Research on 3,904 cryptocurrencies (2014–2021) found annualized survivorship bias of 0.93% for value-weighted and 62.19% for equal-weighted portfolios. — [University of St. Gallen (Alexandria)](https://alexandria.unisg.ch/handle/20.500.14171/108037) (as summarized in search results; full paper not fetched)
- Freqtrade protections can be simulated in backtests only with `--enable-protections`. — [Freqtrade protections docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/includes/protections.md)
- General backtesting-problem overview (overfitting, fees, slippage) from a bot vendor — [Gainium blog: common backtesting problems](https://gainium.io/blog/common-backtesting-problems); methodology discussion — [Trading Strategy docs: backtesting methodology](https://tradingstrategy.ai/docs/learn/backtesting.html)

### Inferences
- **Practical checklist for a solo dev:**
  1. Split data before touching it: e.g., optimize on one period, hold out a later period untouched. Include at least one bull (2021), one bear (2022) and one choppy/recovery period so regime dependence shows up.
  2. Walk-forward: re-optimize on rolling windows and only score on the following unseen window; report the concatenated out-of-sample equity curve, not the in-sample one.
  3. Count every hyperopt trial and strategy variant you tried; that count is the "number of trials" DSR needs. A Sharpe of 2 found after 1,000 hyperopt epochs is much weaker evidence than one found after 5.
  4. Run `freqtrade lookahead-analysis` (and Freqtrade's related recursive-analysis, if available in the installed version) on every strategy.
  5. Fees: set the backtest fee to your actual taker fee tier (at $20 you will be in the lowest/most expensive tier; see section 4). Assume market orders pay taker + spread; on illiquid alts add slippage.
  6. Monte Carlo: reshuffle/bootstrap the trade list to get a distribution of max drawdown, rather than trusting the single historical path.
  7. Dry-run (paper trade) for at least several weeks and compare dry-run fills to backtest expectations before risking money.
- Equal-weight altcoin baskets are where survivorship bias is extreme (62% annualized in the cited study); a $20 bot trading only BTC/ETH (or a fixed list of large caps chosen as of the start of the test period) largely sidesteps it.
- Candle-based backtests assume fills at candle prices; with a 1-minute or 5-minute strategy, intra-candle ordering of high/low is unknown, so stop-loss and take-profit fills are optimistic.

### Gaps
- No primary López de Prado walk-forward/CPCV text (Advances in Financial Machine Learning) was fetched; the walk-forward recommendation is based on general practice plus the PBO/DSR papers.
- Could not confirm Freqtrade's `recursive-analysis` command details in this session.
- No quantified crypto-specific slippage figures were found for small orders.

## 3. Historical data sources and pitfalls

### Takeaway
Free data is adequate for a $20 bot: Freqtrade's `download-data` (via CCXT) pulls OHLCV from the exchange you will trade on; Binance publishes bulk kline files; Kraken publishes downloadable OHLCVT/trade history. The main pitfalls are survivorship bias (delisted pairs removed), exchange mismatch (backtesting on Binance prices but trading on Kraken/Coinbase), and gaps.

### Cited Findings
- Binance Public Data (data.binance.vision / GitHub repo): daily and monthly files for all symbols; new daily data available next day; klines from 1 second to 1 month intervals with OHLCV. — [binance-public-data GitHub](https://github.com/binance/binance-public-data/)
- Binance spot data cannot produce a survivorship-bias-free dataset because delisted/dead assets are removed from the API; a source claims Binance Futures data retained delisted symbols. — [CoinAPI blog: historical data for delisted coins (Nov 2025)](https://www.coinapi.io/blog/historical-data-for-delisted-crypto-coins). Note: CoinAPI is a commercial data vendor with an incentive to emphasize free-data shortcomings.
- Kraken offers free complete OHLCVT data for every trading pair (2013–2025 coverage per article title). — [Concretum Group article](https://concretumgroup.com/how-to-get-free-full-crypto-intraday-data-2013-2025-from-kraken/) (page blocked by proxy; claim from title/snippet only)
- Freqtrade is built on CCXT, which supports 100+ exchanges, so data download works for any CCXT exchange. — [Freqtrade exchange notes mirror](https://gitcode.com/GitHub_Trending/fr/freqtrade/blob/develop/docs/exchanges.md); [ccxt GitHub](https://github.com/ccxt/ccxt)

### Inferences
- Backtest on data from the exchange you will trade on (Kraken data for a Kraken bot). Binance.com is not available to US users, and Binance.US prices/liquidity differ from Binance global, so Binance bulk files are fine for research but not for final validation.
- Paid vendors (Kaiko, CoinAPI, etc.) mainly add tick/order-book depth and delisted-asset coverage; not justified at $20 capital.
- Always check for missing candles (exchange outages, maintenance) and for pairs that started trading mid-period.

### Gaps
- No current pricing or free-tier details retrieved for Kaiko or CryptoDataDownload.
- Did not verify the exact current URL/format of Kraken's downloadable OHLCVT archive or how often it is updated.
- Coinbase Advanced historical candle API limits (max candles per request) not verified.

## 4. Risk management for bots

### Takeaway
At $20, the binding constraints are exchange minimum order sizes and fees, not sophisticated sizing. Use a fixed fractional or fixed stake per trade, a small number of max open trades, an exchange-side stop-loss where supported, and an automatic drawdown kill switch (Freqtrade's MaxDrawdown/StoplossGuard protections). Never use full Kelly; at most quarter-to-half Kelly, and only after a long dry-run.

### Cited Findings
- **Freqtrade protections (built-in kill switches):**
  - StoplossGuard: halts trading when stoploss count hits `trade_limit` within `lookback_period_candles`; pause for `stop_duration_candles`; per-pair or global.
  - MaxDrawdown: stops trading if drawdown exceeds `max_allowed_drawdown` (e.g., 0.2 = 20%); `calculation_mode` "equity" recommended.
  - LowProfitPairs: locks pairs below `required_profit`.
  - CooldownPeriod: prevents immediate re-entry after exit.
  - All can be backtested with `--enable-protections`. — [Freqtrade protections docs](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/docs/includes/protections.md)
- Freqtrade on Kraken supports stoploss_on_exchange (stop-loss-market / stop-loss-limit), so the stop lives on the exchange even if the bot dies. — [Freqtrade exchange notes mirror](https://gitcode.com/GitHub_Trending/fr/freqtrade/blob/develop/docs/exchanges.md)
- **Kelly caveats:** edges are estimated from small samples and usually overestimated; e.g., a win-rate estimate from 100 trades has ~±5% standard error, and estimating 60% when truth is 55% makes full Kelly overbet by ~50%. Half Kelly roughly halves volatility while reducing expected growth by ~25%; a quarter to half Kelly is the common range; under full Kelly, the probability of the account eventually halving is roughly one half. — [LuxAlgo: Kelly criterion](https://www.luxalgo.com/library/concept/kelly-criterion/); academic treatment of estimation error causing over-betting — [arXiv 2503.17927](https://www.arxiv.org/pdf/2503.17927)
- **Fees (conflicting sources):** Coinbase Advanced entry tier reported as 0.40% maker / 0.60% taker; Kraken Pro entry tier 0.25% maker / 0.40% taker — [financer.com Coinbase vs Kraken 2026](https://financer.com/crypto/coinbase-vs-kraken/); another source lists Kraken Pro at 0.16%/0.26% (that is likely a higher volume tier or older schedule) — [Coin Bureau Kraken vs Coinbase (Feb 2026)](https://coinbureau.com/analysis/kraken-vs-coinbase). Older Coinbase schedules (which this researcher recalls as 0.60%/1.20% at the lowest tier) may still apply; verify on the official fee pages.

### Inferences
- **Fee math at $20:** a round trip with taker orders costs ~0.8% (Kraken) to ~1.2% (Coinbase) per trade at the reported entry tiers. A strategy trading daily would need >0.8–1.2% gross edge per trade just to break even; prefer low-frequency strategies and limit (maker) orders.
- **Minimum order sizes** at exchanges (often a few dollars to ~$10 notional) mean $20 supports only 1–2 concurrent positions; set `max_open_trades` to 1–2 and a fixed stake.
- Fixed fractional (e.g., risk 1–2% of equity per trade, i.e., $0.20–$0.40) is mathematically fine but often impossible at $20 because of minimums; volatility targeting (size inversely to ATR/realized vol) is a reasonable upgrade once capital grows.
- **Exchange outages/API errors:** keep stops on the exchange (stoploss_on_exchange); on restart, reconcile local state with exchange open orders/balances before acting; use exponential backoff on rate-limit errors; make order placement idempotent by assigning your own client order ID and checking for it before retrying a timed-out request (a timeout does not mean the order failed). Freqtrade handles much of this internally via its database of trades.
- Spot only, no leverage/futures, for this capital level and experience; US access to crypto derivatives is also restricted.

### Gaps
- Did not fetch official Kraken/Coinbase fee schedule pages or minimum order size tables (fees conflict between sources above).
- No source fetched on CCXT/Freqtrade handling of client order IDs or retry behavior; idempotency advice is general engineering practice, not verified in docs this session.
- No source found on volatility-targeting specifics for crypto bots.

## 5. Infrastructure: home PC vs VPS vs Raspberry Pi; monitoring

### Takeaway
Freqtrade needs about 2 GB RAM / 2 vCPU, so a ~€3.50–5/month VPS or Oracle Cloud's always-free ARM instance is sufficient; a home PC or Raspberry Pi works but adds downtime risk (power, ISP, dynamic IP that breaks API IP-whitelisting). Use Docker with a restart policy, Freqtrade's Telegram bot for alerts/control, and its web UI.

### Cited Findings
- Freqtrade minimal hardware: 2 GB RAM, 1 GB disk, 2 vCPU; Docker recommended; Telegram and WebUI built in. — [Freqtrade README](https://raw.githubusercontent.com/freqtrade/freqtrade/develop/README.md)
- Oracle Cloud always-free ARM: up to 4 vCPU / 24 GB RAM, 200 GB block storage, 10 TB egress/month. — [Medium Oracle free tier guide 2026](https://medium.com/@imvinojanv/setup-always-free-vps-with-4-ocpu-24gb-ram-and-200gb-storage-the-ultimate-oracle-cloud-guide-bed5cbf73d34); [space-node Oracle free VPS 2026](https://space-node.net/blog/oracle-cloud-free-vps-guide-2026)
- One 2026 source reports Oracle cut its Always Free tier in 2026 — [braindetox: Oracle Always Free Tier Cut 2026](https://braindetox.kr/en/posts/oracle_always_free_tier_reduced_2026.html) (not fetched; conflicts with sources above—verify current limits).
- Oracle free tier storage is slow (~55 MB/s vs Hetzner ~2.52 GB/s read) and account setup is reported as frustrating; Hetzner seen as more reliable. — [Bitdoze Hetzner vs Oracle ARM](https://www.bitdoze.com/hetzner-oracle-arm-performance/)
- Hetzner introduced cost-optimized cloud plans starting at €3.49/month; Hetzner raised prices from April 2026 (CAX31 €11.99 → €15.99). — [Bitdoze Hetzner cost-optimized plans](https://www.bitdoze.com/md/hetzner-cloud-cost-optimized-plans.md); [Bitdoze Hetzner vs Oracle](https://www.bitdoze.com/hetzner-oracle-arm-performance/)
- Long-run review of Oracle free tier for production use — [bestusavps Oracle Cloud review 2026](https://bestusavps.com/reviews/oracle-cloud/)

### Inferences
- A VPS gives a static public IP, which is what makes exchange API IP-whitelisting practical (section 6). A home connection often has a dynamic IP.
- For $20 capital, a paid VPS at ~$4–6/month is a 20–30% annual drag on a $20 account (≈$50–70/year vs $20 capital). Free options (Oracle free tier, or the user's always-on home PC/Raspberry Pi 4/5 with ≥2 GB RAM) are economically preferable; the user should treat any VPS cost as a learning expense, not something the bot will earn back.
- Pick a VPS region close to the exchange's API endpoints only if latency matters; for candle-based strategies on 5m+ timeframes it does not.
- Ops basics: run via `docker compose` with `restart: unless-stopped`; enable Telegram notifications for entries/exits/errors/protection triggers; rotate and keep logs; keep the SQLite trade DB on persistent storage and back it up; add an external heartbeat (e.g., a free uptime check) so you learn when the bot is down.

### Gaps
- No primary source fetched on Raspberry Pi suitability (ARM builds, TA-Lib compile issues) or home-PC uptime.
- Current Oracle Always Free limits are conflicting between sources (possible 2026 reduction); not resolved.
- Exact cheapest US-region VPS prices (DigitalOcean, Vultr, Hetzner US) not retrieved.

## 6. API key security

### Takeaway
Create a dedicated key with View + Trade only (no Transfer/Withdraw), restrict it to the bot server's static IP, store it outside source code, enable 2FA on the exchange account, and rotate/expire keys. The 2022 3Commas leak (~100k keys, >$27M losses) shows that third-party bot platforms holding your keys are a single point of failure; self-hosting an open-source bot avoids that particular risk.

### Cited Findings
- **3Commas incident:** complaints from October 2022 of keys being used for unauthorized trades (including on FTX with the DMG token); 3Commas initially called reports "false rumors"; on Dec 28, 2022 Binance CEO Changpeng Zhao said he was "reasonably sure" 3Commas keys were leaking; 3Commas then confirmed leaked data was genuine and asked exchanges to revoke all 3Commas-connected keys. — [Cointelegraph: 3Commas CEO confirms API key leak](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz); [The Block: Binance warns about 3Commas API leak](https://www.theblock.co/news/ecosystems/2022-12-28-binance-warns-about-3commas-api-leak-says-users-should-disable-keys-198295); [ForkLog: 3Commas denies leak](https://forklog.com/en/3commas-denies-leak-of-users-api-keys/)
- Scale: ~100,000 API keys obtained, >$27 million lost, across Binance, KuCoin, Coinbase and others; HAPI analysis criticized exchange inaction; FBI reportedly opened an investigation. — [ForkLog: HAPI analysis of 3Commas incident](https://forklog.com/en/news/api-key-leaks-and-exchange-inaction-a-hapi-analysis-of-the-3commas-incident); [ForkLog: FBI probes 3Commas leak](https://forklog.com/en/fbi-probes-3commas-api-key-leak-reports-say/)
- Attack pattern: leaked trade-only keys were used for unauthorized trades (e.g., pumping illiquid tokens) rather than withdrawals — i.e., trade-only permission limits but does not eliminate loss. — [ForkLog: HAPI analysis](https://forklog.com/en/news/api-key-leaks-and-exchange-inaction-a-hapi-analysis-of-the-3commas-incident)
- **Coinbase (CDP keys):** keys are created on the Coinbase Developer Platform; permission levels View, Trade, Transfer (Transfer = send/receive funds on and off platform); IP allowlist can be set at key creation; `/api/v3/brokerage/key_permissions` endpoint returns a key's permissions. — [Coinbase CDP auth docs](https://docs.cloud.coinbase.com/advanced-trade/docs/auth); [Advanced Trade API permissions](https://docs.cloud.coinbase.com/advanced-trade/docs/rest-api-scopes); [Get API key permissions](https://docs.cdp.coinbase.com/api-reference/advanced-trade-api/rest-api/data-api/get-api-key-permissions.md)
- **Kraken:** grant minimum permissions—an order-placing key does not need Withdraw Funds; "Add Withdrawal Addresses" combined with "Withdraw Funds" lets an attacker add an address and withdraw with only the key; lock keys to your IPs ("prevents almost all key misuse even if the key is leaked"); separate keys per purpose; never embed keys in source; rotate periodically; set key expiry; nonce window setting. — [Kraken API keys guide](https://docs.kraken.com/exchange/guides/rest/api-keys); [Kraken: Withdrawal Addresses API permission](https://support.kraken.com/articles/withdrawal-addresses-api-permission); [Kraken: how to create an API key on Kraken Pro](https://support.kraken.com/gb/articles/how-to-create-an-api-key-on-kraken-pro)

### Inferences
- **Setup checklist:**
  1. Separate exchange sub-account or dedicated account funded with only the $20 you're willing to lose.
  2. Key permissions: Query/View + Trade only. Never Withdraw/Transfer or Add Withdrawal Address. Verify via Coinbase's key_permissions endpoint or Kraken's key settings.
  3. IP allowlist to the VPS's static IP.
  4. Store secrets in a `.env`/config file outside the git repo (add to `.gitignore`), file permissions 600; never paste into chat/Discord/screenshots. Freqtrade configs contain keys, so never commit or share `config.json` unredacted.
  5. Hardware-key or TOTP 2FA on the exchange account and email; enable withdrawal address allowlisting on the account itself.
  6. Harden the server: SSH keys only, disable password login, firewall; do not expose the Freqtrade web UI/API publicly (bind to localhost and use an SSH tunnel), set strong API/JWT passwords, and lock Telegram control to your own chat ID.
  7. Rotate keys periodically and immediately if a third-party tool or server may be compromised.
- Lesson from 3Commas: trade-only keys still allow an attacker to drain value by trading into illiquid tokens they control; IP whitelisting is the control that would have blocked use of leaked keys from attacker infrastructure.
- Beware fake/malicious "free bot" repos and strategy files—strategy code in Freqtrade is arbitrary Python executed with access to your config/keys; only run code you've read.

### Gaps
- Did not confirm whether 3Commas keys that were used had IP whitelisting enabled, or 3Commas' final root-cause statement.
- Did not find documented incidents of malicious Freqtrade strategy files or typosquatted trading-bot packages (searched not performed due to tool-call budget); recommendation is precautionary.
- Coinbase's current guidance on whether IP allowlisting is mandatory or optional for CDP trading keys was not confirmed.
