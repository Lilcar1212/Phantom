# US-Accessible Crypto Venues for a ~$20 Retail Algorithmic Trader (status as of Oct 2026)

> Research method note: All direct page fetches (coinbase.com, kraken.com support, gemini.com, robinhood.com, cointelegraph, cryptoslate, exchange public APIs) were blocked by this environment's egress proxy. Findings below come from web-search result snippets of those pages and news articles. Numbers should be re-verified on the official fee/API pages (or by calling each exchange's public product/market-info endpoint) before any money is deployed. Items I could not verify are listed under "Gaps".

## 1. Which centralized exchanges serve US residents with usable trading APIs (2026 status)

### Takeaway
Coinbase Advanced Trade, Kraken Pro, Binance.US, Gemini, OKX US, Crypto.com and Robinhood Crypto all serve US residents in 2026 and all have programmatic APIs; Coinbase and Kraken are the strongest all-round choices (spot + CFTC-regulated perps + good APIs + CCXT support), while Binance.US is now the cheapest for pure spot.

### Cited Findings
- **Coinbase Advanced Trade**: REST API for orders + WebSocket for real-time market data and account updates; WebSocket connections rate-limited at 750/sec per IP, unauthenticated WebSocket messages at 8/sec per IP — [Coinbase WS rate limits docs](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-rate-limits.md); [Advanced Trade overview](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/overview); REST rate-limit page exists at [docs.cdp.coinbase.com/advanced-trade/docs/rate-limits](https://docs.cdp.coinbase.com/advanced-trade/docs/rate-limits) (exact REST numbers not visible in snippets).
- Coinbase Advanced also exposes perpetual futures via the same API family ("Advanced Trade Perpetual Futures" docs) — [Coinbase perpetuals API docs](https://docs.cloud.coinbase.com/advanced-trade/docs/perpetuals).
- **Kraken Pro**: US clients get spot, spot margin, CME-listed futures and (since June 15, 2026) CFTC-regulated perpetual futures in one Kraken Pro interface/unified collateral pool — [Coinpaprika](https://coinpaprika.com/news/kraken-brings-crypto-60-trillion-perpetuals/); [crypto.jobs](https://crypto.jobs/news/kraken-brings-cftc-regulated-perpetual-futures-to-u-s-market-through-bitnomial-acquisition). Kraken launched regulated spot margin trading in the US following the Bitnomial deal — [The Block](https://www.theblock.co/post/400247/kraken-launches-regulated-crypto-spot-margin-trading-us-bitnomial-deal).
- **Binance.US**: still operating in 2026; cut spot fees to 0% maker / 0.02% taker on all pairs for all users (announced Apr 22, 2026); context is collapsing volume (~0.20% market share) and continued regulatory scrutiny (US senators in Feb 2026 urged Treasury/DOJ review of Binance compliance) — [Yahoo Finance](https://finance.yahoo.com/news/binance-us-cuts-fees-near-205834438.html); [Rutland Herald/BusinessWire, Apr 22 2026](https://www.rutlandherald.com/news/business/binance-us-slashes-spot-trading-fees-to-near-zero-for-all-users/article_03c05c3d-289a-557a-aef5-443d71beea8b.html); [Cointelegraph](https://cointelegraph.com/news/binance-us-cuts-spot-trading-fees-to-near-zero-in-push-to-undercut-rivals).
- **Gemini**: ActiveTrader and API fee schedules exist; search snippet indicates the schedule was updated as recently as Sept 1, 2026 — [Gemini ActiveTrader fee schedule](https://gemini.com/fees/activetrader-fee-schedule); [Gemini API fee schedule](https://gemini.com/fees/api-fee-schedule).
- **OKX US**: launched its US centralized exchange and self-custody wallet in April 2025 (HQ San Jose) after a $505M DOJ settlement; Okcoin users migrated to it; phased onboarding with broader nationwide launch planned later in 2025 — [Bloomberg](https://www.bloomberg.com/news/articles/2025-04-16/crypto-firm-okx-launches-us-exchange-after-settling-doj-charges); [CNBC via NBC Washington](https://www.nbcwashington.com/news/business/money-report/global-crypto-exchange-okx-pushes-into-u-s-market-with-trading-and-wallet-offering/3893179/).
- **Crypto.com**: launched an exchange in the US (initially institutional-grade) complementing the retail Crypto.com App; REST + WebSocket APIs — [The Paypers](https://thepaypers.com/cryptocurrencies/cryptocom-launches-exchange-in-the-us--1271892); [FintechNews SG](https://fintechnews.sg/106743/crypto/crypto-com-launches-exchange-us-institutional-traders/).
- **Robinhood Crypto**: has an official Crypto Trading API for US customers (market data, account info, order placement). Two versions: v2 ("Place crypto orders with fee tiers") is required for orders to count toward 30-day volume fee tiers; v1 orders do not count — [Robinhood Crypto API help](https://robinhood.com/us/en/support/articles/crypto-api); [Robinhood crypto fee tiers](https://robinhood.com/us/en/support/articles/crypto-fee-tiers).
- **CCXT** supports binanceus, gemini, kraken (all CCXT Pro / websockets), and coinbase (Coinbase Advanced) and cryptocom (both "CCXT Certified" + Pro) — [CCXT on PyPI](https://pypi.org/project/ccxt).

### Inferences
- For a bot, Coinbase Advanced and Kraken Pro are the safest defaults: large US liquidity, CCXT-certified/Pro support, and both now offer US-regulated perps under the same login.
- Binance.US is cheapest for spot but carries counterparty/business-continuity risk given its tiny market share and regulatory history.
- Robinhood's API is legitimate but its fee floor (0.85% at lowest tier) makes it unattractive for high-frequency strategies.
- Bitstamp: no 2026-specific findings retrieved (see Gaps). Bitstamp was acquired by Robinhood (closed 2025, from training knowledge — unverified here).

### Gaps
- Bitstamp's 2026 US retail status and fees not found in this session.
- OKX US current fee schedule and whether nationwide rollout completed: not found.
- Crypto.com Exchange US retail (vs institutional-only) access in 2026 unclear.
- Exact REST rate limits for each exchange (Coinbase, Kraken, Binance.US, Gemini) not retrieved; official docs pages were blocked.

## 2. Maker/taker fees at the lowest volume tier; zero-fee pairs and promotions

### Takeaway
At a $20 account size you will always be in the lowest tier: Binance.US (0% / 0.02%) is dramatically cheapest, followed by Gemini (0.20%/0.40%) and Kraken Pro (0.25%/0.40%); Coinbase Advanced (0.40%/0.60%) and Robinhood (up to 0.85%) are expensive enough to destroy most grid/scalping edges.

### Cited Findings
| Venue | Lowest-tier maker | Lowest-tier taker | Source |
|---|---|---|---|
| Binance.US (spot, all pairs, from Apr 22 2026) | 0.00% | 0.02% | [Rutland Herald/BusinessWire](https://www.rutlandherald.com/news/business/binance-us-slashes-spot-trading-fees-to-near-zero-for-all-users/article_03c05c3d-289a-557a-aef5-443d71beea8b.html); [Binance.US zero-fee page](https://binance.us/lp/zero-fee-trading) |
| Gemini ActiveTrader (<$10k 30d vol) | 0.20% | 0.40% | [Gemini ActiveTrader schedule](https://gemini.com/activetrader-fee-schedule); [NerdWallet Gemini review 2026](https://www.nerdwallet.com/investing/reviews/gemini) |
| Kraken Pro spot ($0–10k) | 0.25% | 0.40% | [Datawallet](https://www.datawallet.com/crypto/kraken-fees-explained); [Kraken support](https://support.kraken.com/cn/articles/201893638-how-trading-fees-work-on-kraken) |
| Coinbase Advanced (<$10k) | 0.40% | 0.60% | [Financer Coinbase review 2026](https://financer.com/review/coinbase); [GOBankingRates](https://www.gobankingrates.com/investing/crypto/coinbase-fees/) |
| Crypto.com Exchange | 0.25% | 0.50% | [DailyCoin comparison](https://dailycoin.com/crypto-exchange-fees-comparison/) (aggregator; may be outdated) |
| Robinhood Crypto (API v2 fee tiers) | range 0.03%–0.85% (0.85% at lowest volume) | | [Robinhood fee tiers](https://robinhood.com/us/en/support/articles/crypto-fee-tiers) |

- Kraken Pro full spot ladder: $0–10k 0.25/0.40; $10–50k 0.20/0.35; $50–100k 0.14/0.24; ... $10M+ 0.00/0.10 — [Datawallet](https://www.datawallet.com/crypto/kraken-fees-explained).
- Coinbase Advanced next tiers: $10–50k 0.25/0.40; $50–100k 0.15/0.25 — [Financer](https://financer.com/review/coinbase).
- Binance.US fees have no portfolio minimums, volume tiers or subscription; claimed "up to 98%" savings vs Coinbase — [Rutland Herald/BusinessWire](https://www.rutlandherald.com/news/business/binance-us-slashes-spot-trading-fees-to-near-zero-for-all-users/article_03c05c3d-289a-557a-aef5-443d71beea8b.html).
- Gemini tier is based on 30-day volume across order books (excluding stablecoin pairs) or total asset balance; recalculated daily — [Gemini API fee schedule](https://gemini.com/fees/api-fee-schedule).
- Robinhood has run promos giving 60 days at the lowest 0.03% fee — [Robinhood fee tiers promo](https://robinhood.com/us/en/support/articles/crypto-fee-tiers-promo).
- Perps fees: Coinbase US perps taker fees "as low as 0.02%" at launch — [CryptoSlate](https://cryptoslate.com/coinbase-starts-cftc-regulated-perpetuals-for-us-traders-offering-10x-leverage-and-0-02-fees/). Kraken Derivatives US perps: flat $0.15/contract per side all-in ($0.03 commission + $0.10 exchange/clearing + $0.02 NFA); double for round trip — [Kraken US futures fees](https://support.kraken.com/articles/us-futures-fees).

### Inferences
- Round-trip cost at lowest tier, maker both legs: Binance.US 0.00%; Gemini 0.40%; Kraken 0.50%; Coinbase 0.80%. Taker both legs: Binance.US 0.04%; Kraken/Gemini 0.80%; Coinbase 1.20%. A grid bot with 0.5–1% grid spacing is unprofitable on Coinbase/Kraken/Gemini at the base tier and only viable on Binance.US (or with maker-only post-only orders and wide grids).
- On a $20 account, volume needed to reach better tiers ($10k/30d) means turning the account over ~500x per month — not realistic; plan on lowest-tier fees.
- Kraken's flat $0.15/contract perp fee is very large relative to small contracts; the % cost depends on contract notional (unknown — see Gaps).

### Gaps
- Coinbase stablecoin-pair (e.g., USDT-USD/USDC) fee exceptions and any 2026 promotions not verified.
- Crypto.com Exchange US-specific fee schedule not verified from primary source.
- Whether Binance.US 0%/0.02% has an end date not confirmed.

## 3. Minimum order sizes / minimum notional (critical for a $20 grid)

### Takeaway
Binance.US allows $1 minimum orders on USD/stablecoin pairs (via Advanced Trading), making it the only venue where a $20 grid of ~10–20 orders is clearly feasible; Coinbase and Kraken have per-product minimums that must be read from their APIs (likely in the ~$1 and ~$0.50–$5 ranges respectively, unverified), and Kraken's costmin varies per pair (e.g., 10 USDT on LTC/USDT).

### Cited Findings
- Binance.US reduced minimums from $10 to $1 for buy and sell orders on all USD, stablecoin and DAI pairs placed via Advanced Trading — [Binance.US blog](https://blog.binance.us/tag/for-advanced-traders/). The legacy default MIN_NOTIONAL was $10 — [Binance.US API error codes reference](https://glama.ai/mcp/servers/@nirholas/bnbchain-mcp/blob/506d3dcc41778c2612838270b553353ea67ed1a9/binance-us-mcp-server/docs/ERROR_CODES.md).
- Kraken: each pair has `ordermin` (base volume) and `costmin` (price×volume) fields queryable via `/0/public/AssetPairs`; orders below either are rejected. Example: LTC/USDT minimum 10 USDT — [Kraken spot API errors guide](https://docs.kraken.com/api/docs/guides/spot-errors/); [Kraken minimums overview](https://support.kraken.com/articles/205893708-minimum-order-size-volume-for-trading).
- Coinbase: per-product `base_min_size`/`base_max_size`; `min_market_funds` repurposed as notional minimum for limit orders; errors read e.g. "Minimum order is 0.0001 BTC" or "Minimum order size is $5.00" (example messages relayed by a third-party bot vendor) — [Coinbase Exchange API create order docs](https://docs.cdp.coinbase.com/api-reference/exchange-api/rest-api/orders/create-new-order.md); [Altrady Coinbase errors](https://support.altrady.com/en/article/common-coinbase-error-messages-18gqfgc/).
- Robinhood app/API trades fractional crypto (dollar-based) — implied by API description; exact min not retrieved — [Robinhood Crypto API](https://robinhood.com/us/en/support/articles/crypto-api).

### Inferences
- A $20 grid split into 10 orders = $2/order: works on Binance.US ($1 min); likely works on Coinbase for majors if quote min is ~$1 (verify); likely fails or is marginal on Kraken pairs with $5+ or 10 USDT minimums. Split into 4–5 orders ($4–5 each) is the safer design if using Kraken/Coinbase.
- Bot code should always load minimums dynamically (CCXT `market['limits']['amount']['min']` and `['cost']['min']`) rather than hardcoding.

### Gaps
- Exact current `quote_min_size` for Coinbase BTC-USD/ETH-USD and `costmin` for Kraken XBT/USD: public APIs were blocked from this environment. (Training-knowledge recollection, unverified: Coinbase ~$1 quote min on most USD pairs; Kraken costmin ~0.5 USD on many USD pairs and ordermin 0.00005 BTC.) Must be verified by querying `api.coinbase.com/api/v3/brokerage/market/products` and `api.kraken.com/0/public/AssetPairs`.
- Gemini and Crypto.com minimum order sizes not found.

## 4. US-accessible derivatives in 2026 (perps, futures, margin) and funding/basis arbitrage feasibility

### Takeaway
US retail can now trade CFTC-regulated perpetual(-style) futures on Coinbase (since July 21, 2025; up to 10x, hourly funding accrual, nano 0.01 BTC contracts) and Kraken (since June 15, 2026, via Bitnomial; "as little as $25 intraday margin"; up to 50x), plus CME Micro Bitcoin (~$1.6–1.8k margin). Funding/basis arbitrage is legally possible for US retail, but every venue's per-contract minimums exceed a $20 account, and per-contract fees make it uneconomic at that size.

### Cited Findings
**Coinbase (Coinbase Financial Markets / Coinbase Derivatives)**
- US customers can trade CFTC-regulated perpetual-style futures since July 21, 2025; no monthly expiry; up to 10x leverage — [FOW](https://www.fow.com/insights/coinbase-hails-arrival-of-perpetual-style-futures-in-us); [MarketsMedia](https://www.marketsmedia.com/coinbase-brings-perpetual-futures-to-u-s).
- Launch contracts: nano Bitcoin Perpetual-Style Futures (0.01 BTC) and nano Ether Perpetual-Style Futures; taker fee as low as 0.02% — [CryptoSlate](https://cryptoslate.com/coinbase-starts-cftc-regulated-perpetuals-for-us-traders-offering-10x-leverage-and-0-02-fees/); [Bitcoin Magazine](https://bitcoinmagazine.com/news/interactive-brokers-nano-bitcoin-futures).
- Structurally they are 5-year-expiry futures trading 24/7, funding accrues hourly and is settled twice daily; margin is USDC in the perpetuals portfolio — [FX News Group](https://fxnewsgroup.com/forex-news/cryptocurrency/coinbase-derivatives-to-launch-us-perpetual-style-futures/); [Coinbase "Understand perpetuals trading"](https://www.coinbase.com/advanced-perpetuals).
- Coinbase expanded to perpetual-style equity index futures in the US on June 8, 2026, and stock perps (up to 10x single names, 20x ETFs, USDC-settled) — [The Defiant](https://thedefiant.io/converge/cefi/coinbase-perpetual-equity-index-futures-june-8-yclimy); [LetsDataScience](https://letsdatascience.com/news/coinbase-launches-stock-perpetual-futures-for-us-stocks-a-7625fc7). Interactive Brokers also lists Coinbase Derivatives nano BTC/ETH futures (Feb 2026) — [IBKR press release](https://brokerage.ibkr.com/en/general/about/mediaRelations/2-10-26.php).
- One search summary references a June 2026 CFTC clearance for Coinbase crypto perps — [DEXTools (German)](https://www.dextools.io/news/coinbase-cftc-clearance-us-crypto-perpetual-futures-june-2026-de) — possibly a move from "perpetual-style" (5-yr expiry) to true perpetuals; not confirmed from primary source.

**Kraken Derivatives US (Bitnomial)**
- Perps live for eligible US clients on Kraken Pro from June 15, 2026, via Payward's acquisition of CFTC-licensed Bitnomial (exchange + clearinghouse + brokerage), closed May 2026 — [Coinpaprika](https://coinpaprika.com/news/kraken-brings-crypto-60-trillion-perpetuals/); [crypto.jobs](https://crypto.jobs/news/kraken-brings-cftc-regulated-perpetual-futures-to-u-s-market-through-bitnomial-acquisition).
- Listed on Bitnomial Exchange; anyone who already unlocked US futures on Kraken Pro gets perps with no extra unlock — [Kraken support: US Perpetual Futures](https://support.kraken.com/articles/us-perpetual-futures).
- Product range: one source lists 16 USD-quoted contracts (BTC, ETH, SOL, XRP, ADA, DOGE, LINK, AVAX, LTC, DOT, XLM, SHIB, AAVE, HBAR, XTZ, BCH) — [Kraken futures page via search](https://www.kraken.com/features/futures); another lists 9 (BTC, ETH, SOL, XRP, ADA, LINK, DOGE, LTC, AVAX) — [Tangem/news via search](https://tangem.com/en/news/regulation/27793-kraken-brings-regulated-perpetual-futures-to-u-s-traders/). Likely launch set vs. later expansion ([MarketsMedia: "Kraken looks to expand perpetual futures suite"](https://www.marketsmedia.com/kraken-looks-to-expand-pepertual-futures-suite/)).
- Margin "as little as $25 intraday"; leverage varies by contract, up to 50x on BTC/ETH; collateral held in USD — [Kraken features/futures via search](https://www.kraken.com/en-br/features/futures); [Coinpaprika](https://coinpaprika.com/news/kraken-opens-regulated-perpetual-futures-us/).
- Funding: news describes an 8-hour funding rate; Kraken support says funding payments are aggregated and settled once daily at 3:00 pm CT — [Coinpaprika](https://coinpaprika.com/news/kraken-brings-crypto-60-trillion-perpetuals/); [Kraken US futures fees / support](https://support.kraken.com/articles/us-futures-fees) (consistent if funding accrues 8-hourly and cash-settles daily — not confirmed).
- Fees: $0.15/contract/side all-in; liquidation fee $25 first event, $50 each subsequent — [Kraken US futures fees](https://support.kraken.com/articles/us-futures-fees); [Kraken US perpetual futures](https://support.kraken.com/articles/us-perpetual-futures).

**CME Micro Bitcoin (MBT)**
- 0.1 BTC per contract, cash-settled on CME CF BRR; tick = $0.50; margin/maintenance ~ $1,808/$1,644 (April 2026); CME crypto futures trade 24/7 since May 29, 2026 — [CME Group MBT overview](https://www.cmegroup.com/education/lessons/micro-bitcoin-futures-product-overview.html); [Schwab](https://www.schwab.com/learn/story/micro-bitcoin-and-ether-futures-offer-small-bites-crypto) (margin figures from search snippet; verify).

### Inferences
- Funding/basis arb at $20: not feasible. A cash-and-carry needs (a) the full spot leg notional and (b) perp margin. One Coinbase nano BTC perp = 0.01 BTC notional (hundreds to ~$1,000+ depending on BTC price), needing ~1/10 of that in margin at 10x plus a matching spot purchase — total capital well above $20. Kraken's "$25 intraday margin" floor alone exceeds $20 and the $0.30 round-trip per-contract fee plus a $25 liquidation fee would wipe out the account. CME MBT requires ~$1.6–1.8k margin.
- Realistic minimum capital for a hedged funding/basis trade on Coinbase: roughly one nano contract's notional (spot) + ~10–20% margin buffer, i.e. on the order of $1–1.5k at typical 2025–26 BTC prices (estimate, depends on BTC price and contract size).
- Spot margin exists on Kraken US but has eligibility restrictions; at $20 it adds liquidation risk without enabling anything a spot bot can't do.

### Gaps
- Exact Kraken US perp contract sizes/multipliers and per-contract initial margin not found.
- Coinbase US perp maker fees, exact current initial margin requirements, and whether contracts are now true perpetuals (post June 2026 clearance) not verified.
- State-level exclusions for US perps (if any) not found.

## 5. DEX options (Uniswap on Base/Arbitrum, Hyperliquid, dYdX, Jupiter): costs, legality, sense for $20

### Takeaway
Spot swaps on L2 DEXes (Uniswap on Base) are legal for US persons and cost fractions of a cent in gas, but the 0.05–0.3% pool fee plus slippage/MEV still apply; perp DEXes (Hyperliquid, dYdX) exclude US persons by front-end geoblock and terms, so using them as a US resident means violating ToS and carries regulatory risk.

### Cited Findings
- Uniswap V3 swap on Base, early 2026: ~$0.0003 L2 execution + ~$0.0027 L1 blob data ≈ $0.003 total; L2s cost 50–100x less than Ethereum mainnet — [ethskills gas reference](https://skills.sh/austintgriffith/ethskills/gas); [Coin Bureau Uniswap review 2026](https://www.coinbureau.com/review/uniswap-uni).
- Hyperliquid geoblocks US IPs at the front end (no CFTC DCM license); protocol is permissionless but self-custody access by US persons "bears regulatory uncertainty"; May 15, 2026 CME and ICE lobbied CFTC/Congress about Hyperliquid's anonymous trading; no CFTC action filed as of 2026-05-27 — [OneKey blog](https://onekey.so/blog/ecosystem/geo-block-hyperliquid-dydx-us/); [pm.wiki comparison](https://pm.wiki/de/compare/hyperliquid-vs-polymarket).
- dYdX: protocol "not available in the U.S. or to U.S. persons"; dYdX said it cannot offer perps in the US but planned US entry with spot products (Reuters, Oct 2025) — [The Block](https://www.theblock.co/post/377073/dydx-enter-us); [Cointelegraph](https://cointelegraph.com/news/dydx-planning-us-market-entry-by-2026-report).

### Inferences
- For $20, an L2 DEX spot bot is gas-viable (~$0.003/swap on Base), but Uniswap pool fees (typically 0.05% for majors, 0.3% for most pairs — from protocol design, not retrieved here) plus price impact are comparable to or worse than Binance.US's 0–0.02%. Wallet funding/bridging costs and smart-contract risk add overhead. A CEX is simpler for a first bot.
- US persons should treat Hyperliquid/dYdX/Jupiter perps as off-limits (ToS violation; VPN use could lead to frozen front-end access and legal exposure).

### Gaps
- Jupiter (Solana) perps US restrictions and Solana per-swap costs not found in this session.
- Arbitrum per-swap gas in 2026 not retrieved.
- Status of dYdX's planned US spot product launch not confirmed.

## 6. API rate limits, websockets, sandbox/testnet, CCXT support

### Takeaway
All major US venues have REST + WebSocket APIs and CCXT support; Coinbase Advanced has a documented sandbox, but the most practical "testnet" for a $20 bot is paper trading on live data via CCXT/Freqtrade dry-run.

### Cited Findings
- Coinbase Advanced: WebSocket 750 connections/sec/IP; 8 unauthenticated msgs/sec/IP; REST + WS; sandbox doc page exists — [Coinbase WS rate limits](https://docs.cdp.coinbase.com/coinbase-app/advanced-trade-apis/websocket/websocket-rate-limits.md); [Coinbase sandbox docs](https://docs.cdp.coinbase.com/advanced-trade/docs/sandbox); third-party Rust SDK supports production and sandbox — [docs.rs coinbase-advanced](https://docs.rs/coinbase-advanced).
- Crypto.com Exchange: REST + WebSocket APIs aimed at HFT/institutions — [DailyCoin](https://dailycoin.com/crypto-exchange-fees-comparison/).
- Robinhood: Crypto Trading API v1/v2 (REST) — [Robinhood](https://robinhood.com/us/en/support/articles/crypto-api).
- CCXT: binanceus, gemini, kraken (Pro); coinbase and cryptocom (Certified + Pro) — [CCXT PyPI](https://pypi.org/project/ccxt).

### Inferences
- Coinbase's sandbox has historically been a static/mock environment (from training knowledge, unverified here), so it tests auth/order flow but not strategy P&L.
- CCXT's `set_sandbox_mode(True)` works only where the exchange offers a testnet; Kraken has a futures demo environment (demo-futures.kraken.com — training knowledge, unverified) but no spot testnet; Binance.US has no public testnet (training knowledge, unverified).

### Gaps
- Precise REST rate limits for Coinbase, Kraken (counter-decay model), Binance.US (request weight), Gemini not retrieved.
- Whether Robinhood's API offers WebSocket streaming not confirmed.

## 7. Free paper-trading options

### Takeaway
No exchange-native paper environment found that is clearly suited to a US retail spot bot; best practice is bot-framework dry-run on live public market data.

### Cited Findings
- Coinbase Advanced Trade sandbox exists — [Coinbase sandbox docs](https://docs.cdp.coinbase.com/advanced-trade/docs/sandbox).
- CCXT provides unified access to public market data for all of the above exchanges without keys — [CCXT PyPI](https://pypi.org/project/ccxt).

### Inferences
- Recommended path: run a Freqtrade/Hummingbot/custom CCXT bot in dry-run mode against Binance.US/Coinbase/Kraken public order book feeds, modeling the actual lowest-tier fees and minimum-notional rules from section 3, before funding $20.

### Gaps
- No 2026 source retrieved confirming Freqtrade/Hummingbot dry-run features or Kraken/Binance.US testnets; these are from training knowledge and should be verified.
