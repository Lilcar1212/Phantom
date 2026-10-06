# Evidence on Automated Crypto Trading Strategy Types for a Retail Individual (as of Oct 2026)

> Method note: The egress proxy blocked direct fetches of arxiv.org, bis.org and sciencedirect.com, so every number below comes from search-engine summaries of the cited pages, not from reading the full papers. Treat point estimates as "reported by the source as summarized." Where a source is marketing, a vendor blog or of unclear rigor, it is flagged. Evidence from before 2020 is flagged as older.

---

## 1. What academic studies say: numbers (Sharpe, CAGR, drawdowns) and periods, by strategy type

### Takeaway
Trend following / time-series momentum (TSMOM) has the strongest and most repeated academic support in crypto. Cross-sectional momentum is weak and crashes badly. Funding-rate/basis carry was historically very high-Sharpe but has compressed sharply, and one study finds it turned negative in 2025. Simple grid trading has roughly zero expected return in theory. ML and LLM prediction mostly fails once trading costs are included. Pairs trading works only at high frequency and is very sensitive to costs. Triangular and cross-exchange arbitrage are not profitable after costs for anyone without low-latency infrastructure.

### Cited Findings

**Trend following / time-series momentum (TSMOM)**
- Liu & Tsyvinski ("Risks and Returns of Cryptocurrency", NBER w24877; older data, roughly 2011–2018): crypto returns have no exposure to most stock, macro, currency or commodity factors. Only crypto-specific momentum and investor-attention proxies consistently explain returns, and the paper reports "a strong time-series momentum effect." — [NBER WP](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf); [SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3226952)
- In Liu & Tsyvinski, the top momentum quintile averaged about 5.33%/week (Sharpe 0.45, weekly) and the bottom quintile 2.60%/week (Sharpe 0.19). This comes from an early, extreme-return sample (OLDER evidence, pre-2020). — [NBER WP](https://www.nber.org/system/files/working_papers/w24877/w24877.pdf)
- Han, Kang & Ryu (SSRN, Jan 2024), "Time-Series and Cross-Sectional Momentum … under Realistic Assumptions": once transaction costs and intraday price swings are included (i.e., positions get liquidated), "many momentum portfolios are liquidated and many with statistically significant returns earn insignificant profits." TSMOM evidence is strong and cross-sectional evidence is weak. The momentum effect is concentrated in winners, and losers often rebound and cause large losses. Mean return is a poor test because returns are heavily skewed and fat-tailed. — [SSRN 4675565](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565)
- Zarattini, Pagani & Barbon (Concretum Group, SSRN May 2025), "Catching Crypto Trends": an ensemble of Donchian-channel trend models with different lookbacks plus volatility-based sizing, applied as a rotational portfolio of the top 20 most liquid coins on a survivorship-bias-free dataset covering all coins since 2015. Reported net-of-fees Sharpe is above 1.5, with about 10.8% annualized alpha versus BTC. This is a practitioner firm's paper, and it is backtested, not live. — [SSRN 5209907](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907); [Concretum](https://concretumgroup.com/catching-crypto-trends-a-tactical-approach-for-bitcoin-and-altcoins/)
- "Time-Series Momentum in Cryptocurrency Markets: A Pre and Post Spot Bitcoin ETF Analysis" (Zenodo, not peer-reviewed): TSMOM returned 18.03%/yr before the ETF (Sharpe 0.82) and 28.58%/yr after the Jan 11, 2024 ETF launch (Sharpe 1.22). The post-ETF window is short. — [Zenodo](https://zenodo.org/records/19671502)
- Huang, Sangiorgi & Urquhart (SSRN 4825389), volume-weighted TSMOM: a winner-minus-loser portfolio is reported at 0.94%/day with an annualized Sharpe of 2.17. This is a long-short academic construction and is unlikely to survive retail costs at face value. — [SSRN](https://papers.ssrn.com/sol3/Delivery.cfm/4825389.pdf?abstractid=4825389&mirid=1)
- A comparative study (Business, Administration and Technology Perspectives journal, Vilnius University): TS momentum returned 31.96%/yr versus 14.59%/yr for cross-sectional momentum, with TS achieving more than double the Sharpe ratio. — [journals.vu.lt](https://www.journals.vu.lt/BATP/en/article/download/44540/42590/138419)

**Cross-sectional momentum (buying recent winners across coins and shorting losers)**
- "Cryptocurrency momentum has (not) its moments" (Financial Markets and Portfolio Management, 2025): crypto momentum is subject to severe crashes, including −255.23% in December 2020. A single coin can make portfolio returns insignificant. Variance of tail returns is statistically undefined (power-law tails). Volatility scaling improves payoffs but "does not change the tail risk." — [Springer](https://link.springer.com/article/10.1007/s11408-025-00474-9)
- Han, Kang & Ryu: "evidence of cross-sectional momentum is weak." — [SSRN 4675565](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565)

**Funding-rate / basis (cash-and-carry) arbitrage**
- Schmeling, Schrimpf & Todorov, "Crypto Carry" (BIS WP 1087, Apr 2023, revised Oct 2025; published in Management Science 2026): crypto carry (futures minus spot) "can reach exceptionally high levels, sometimes exceeding 40% per annum," and varies widely over time. It is driven by (i) demand from smaller, trend-chasing investors for leveraged long exposure and (ii) limited arbitrage capital because of regulatory and margin frictions. — [BIS](https://www.bis.org/publications/working-paper-1087-crypto-carry); [Management Science](https://pubsonline.informs.org/doi/10.1287/mnsc.2024.05069); [VoxEU summary](https://cepr.org/voxeu/columns/crypto-carry-market-segmentation-and-price-distortions-digital-asset-markets)
- One-month BTC basis was reported at about 8% on OKEx and 6.4% on CME, with maxima around 55% and 45% respectively. Search summaries attribute this to the BIS/crypto-carry literature; the exact source paper was not verified. — [BIS WP 1087](https://www.bis.org/publ/work1087.pdf)
- "Cryptocurrency as an Investable Asset Class: Coming of Age" (arXiv 2510.14435): a carry strategy on Binance perpetuals (Aug 2020–May 2025) had a full-sample Sharpe of 6.45. From 2024 the Sharpe fell to 4.06, and it "turns negative in 2025." Funding averaged roughly 8% with about 0.8% volatility over the full sample. — [arXiv](https://arxiv.org/html/2510.14435v2)
- Springer Digital Finance (2026) on CEX-DEX funding arbitrage, using Binance BTC/ETH/SOL from Jan 2021 to Dec 2024: net returns come mainly from funding carry but are "highly assumption-sensitive and should not be interpreted as frictionless arbitrage profits." — [Springer](https://link.springer.com/article/10.1007/s42521-026-00213-3)
- "Exploring risk and return profiles of funding rate arbitrage on CEX and DEX" (ScienceDirect, 2025): the best case (Drift XRP at 7x leverage) returned 115.9% over six months with a 1.92% max drawdown. This is a cherry-picked best performer, not the typical result. 17% of observations had economically significant spreads, but only 40% of top opportunities were profitable after transaction costs. Funding risk plus market risk make up more than half of strategy variance, alongside liquidity, liquidation and settlement risk. The strategy is uncorrelated with HODL. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2096720925000818); [ResearchGate](https://www.researchgate.net/publication/394323707_Exploring_Risk_and_Return_Profiles_of_Funding_Rate_Arbitrage_on_CEX_and_DEX)
- A growing set of crypto "yield" products depend on funding. If funding premia compress or become more volatile, those strategies' economics deteriorate. — [BIS WP 1087](https://www.bis.org/publ/work1087.pdf)

**Grid trading**
- Chen, Chen & Jang, "Dynamic Grid Trading Strategy: From Zero Expectation to Market Outperformance" (arXiv 2506.11921, June 2025): under simple assumptions, the traditional grid's expected return is essentially zero. Buy-low/sell-high profit inside the grid exactly offsets the loss when price exits the grid. Their dynamic-reset variant outperformed traditional grid and buy-and-hold on minute-level BTC/ETH data from Jan 2021 to Jul 2024, by IRR and risk control. This is the authors' own backtest, and code is public. — [arXiv abstract](https://arxiv.org/abs/2506.11921); [GitHub](https://github.com/colachenkc/Dynamic-Grid-Trading)

**Statistical / pairs arbitrage**
- Crypto pairs-trading studies: the cointegration method earned about 1.36%/month at daily frequency. The common daily distance method returned −0.07%/month, versus 11.61%/month at 5-minute frequency. Results are "quite sensitive to parameter settings" and to transaction costs and execution lag. — [Tandfonline (Investment Analysts Journal 2023)](https://www.tandfonline.com/doi/abs/10.1080/10293523.2023.2268386); [ResearchGate: Pairs Trading in Cryptocurrency Markets](https://www.researchgate.net/publication/346845365_Pairs_Trading_in_Cryptocurrency_Markets)
- Equity benchmark (older, Rad, Low & Faff): distance, cointegration and copula methods earned 91, 85 and 43 bps/month before costs, but only 38, 33 and 5 bps after. This shows how much costs consume pairs profits. — [SSRN 2614233](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2614233)

**Triangular / cross-exchange arbitrage**
- "Wish or reality? On the exploitability of triangular arbitrage in cryptocurrency markets" (Finance Research Letters, 2024): 4,879 possible triangular opportunities were found in high-frequency Binance data, but "transaction costs and limited trading volumes in the order book eliminate their profitability." — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S154461232401537X)
- Cross-exchange price deviations decline over time but persist even in mature markets. What remains is limited by latency, fees and order-book depth. — [ScienceDirect (CEX-DEX arbitrage, J. Banking & Finance 2026)](https://www.sciencedirect.com/science/article/pii/S0378426626000956)

**ML / sentiment / LLM prediction bots**
- arXiv 2606.00060 (2026), walk-forward XGBoost, LSTM and iTransformer forecasts for BTC: naive sign-based strategies show positive gross performance but "collapse after transaction costs because they trade too frequently." A cost-aware filter that cuts turnover by more than an order of magnitude restores positive net performance only in "selected XGBoost configurations." — [arXiv](https://arxiv.org/html/2606.00060v1)
- Another study: a quantile long-short ML strategy earned up to 39% monthly before costs but negative returns after costs, because holding periods were so short. Models with ROC-AUC around 0.60 cannot reliably produce economically significant returns after costs. — [ScienceDirect: ML for crypto market prediction and trading](https://www.sciencedirect.com/science/article/pii/S2405918822000174)
- Alpha Arena Season 1 (Nof1, Oct 18–Nov 3, 2025): six LLMs got $10k each of real money to trade Hyperliquid perps. Four of six lost money, with GPT down about 63%. Qwen3 Max finished +22.3% and DeepSeek +4.9%. This is a two-week, n=6 contest, so it is anecdote rather than evidence of edge. — [Protos](https://protos.com/llm-crypto-trading-contest-finds-llms-cant-trade-crypto/); [Bitcoin.com](https://news.bitcoin.com/6-bots-with-real-money-hyperliquid-hosts-first-ever-ai-trading-showdown/)
- "What LLM Trading Agents Actually Do in Production" (arXiv 2609.05663, 2026) studied about 3,505 user-funded memecoin vaults (Feb–Mar 2026) and 500–599 Hyperliquid perp agents (Jun–Aug 2026). Findings: "Neither fleet shows a directional edge." The perp fleet was unprofitable and trailed a matched Hyperliquid retail benchmark (41% vs 50% round-trip win rate). Median leverage was 5.0x regardless of volatility. 43.2% of positions reached at least +300 bps of favorable move within 24h, yet 49.3% of those closed at a loss. — [arXiv](https://arxiv.org/abs/2609.05663); [DXRG blog](https://www.dxrg.ai/blogs/continuous-record-paper)

**DCA**
- BTC DCA versus lump sum: one analysis of six years of data found lump sum accumulated 3–75% more BTC depending on DCA length. Several backtests say lump sum wins in about 65–80% of windows. DCA lowers maximum drawdowns. These are mostly Bitcoin-company and blog sources (Swan, Amdax, Nakamoto Portfolio), so quality is moderate. — [Amdax](https://medium.com/amdax-asset-management/lump-sum-or-dollar-cost-averaging-42c8f5bb9938); [Nakamoto Portfolio PDF](https://nakamotoportfolio.com/static/docs/DCA_Lumpsum.pdf); [Swan](https://www.swanbitcoin.com/dollar-cost-averaging-vs-lump-sum-investing/)
- Missing the 15 largest 3-day BTC moves in one study's period turned a +127% total return into −84.6%. This illustrates the cost of being out of the market, which matters for timing and trend bots that sit in cash. — [Amdax](https://medium.com/amdax-asset-management/lump-sum-or-dollar-cost-averaging-42c8f5bb9938)

**On-chain: MEV, sniping, copy-trading**
- MEV on Ethereum: the number of "core" arbitrage entities earning significant profit often does not exceed 20 in any week. Searchers often pay more than 90% of revenue to proposers. Independent searchers keep only about 17% of profits, while validators take up to 72% and builders about 10%. — [Extropy cross-chain MEV analysis 2025](https://academy.extropy.io/pages/articles/mev-crosschain-analysis-2025.html)
- MEV on Solana: average arbitrage profit is about $1.58 per transaction and average sandwich profit about 0.0425 SOL (~$8.7). Jito holds about 94% of validator client share. Competitive auctions push searchers to bid away most profit. — [Extropy](https://academy.extropy.io/pages/articles/mev-crosschain-analysis-2025.html); [Gate.com report (exchange blog)](https://www.gate.com/learn/articles/a-comprehensive-report-the-evolution-of-mev-on-solana-and-its-pros-and-cons/8189)
- Sniping on pump.fun: Solidus Labs found about 98.6–98.7% of pump.fun tokens and 93% of Raydium pools showed pump-and-dump or rug-pull characteristics. Of more than 7M tokens (Jan 2024–Mar 2025), only about 97,000 kept liquidity above $1,000. Pump.fun disputed the report. — [Solidus Labs](https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance); [CoinDesk](https://www.coindesk.com/business/2025/05/07/98-of-tokens-on-pump-fun-have-been-rug-pulls-or-an-act-of-fraud-new-report-says); [The Defiant](https://thedefiant.io/news/defi/alarming-99-of-memecoin-launches-on-pumpfun-are-pump-and-dumps-or-rug-pulls-report)
- Also reported: "fewer than 5% of unique wallets" buying pump.fun tokens are net profitable, and more than 95% of rug pulls finish within 10 seconds of pool creation. The search summary did not attribute these to a primary dataset, so they are unverified. — [Solidus Labs](https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance) (attribution unconfirmed)
- Copy trading: across 100,236 outcomes, 97.04% of lead traders were profitable on their own PnL, but only 43.61% produced positive PnL for followers, and only 48.48% of copiers were profitable. This is a small yield-product site, not peer-reviewed. — [YieldFund 90-day study](https://yieldfund.com/is-copy-trading-profitable-a-90-day-multi-exchange-study)
- KuCoin (an exchange that sells copy trading) says only 12% of top traders keep their ranking for more than 6 months, and followers trail leaders because of execution delay and slippage. — [KuCoin blog](https://www.kucoin.com/blog/is-crypto-copytrading-profitable-in-2026)

### Inferences
- The robust result in the literature is a slow-moving trend/TSMOM filter on liquid coins (BTC/ETH, or a top-20 rotation). Its main benefit is avoiding deep drawdowns, not reliably beating BTC in raw return. Sharpe of roughly 0.8–1.5 is the plausible range for honest, net-of-cost versions. Claims above 2 come from long-short or academic constructions.
- Carry was a real, structural premium, paid by leveraged retail longs to arbitrageurs. Its decay (Sharpe 6.45 → 4.06 → negative in 2025 in one study) is consistent with more institutional and ETF-era arbitrage capital entering.
- Every short-horizon strategy (pairs, triangular arb, ML sign prediction, MEV) works gross and fails net. This pattern holds across studies.

### Gaps
- The full papers could not be read, so drawdown figures for TSMOM and Concretum, CAGR for carry, and exact cost assumptions are missing.
- No rigorous peer-reviewed study of standalone mean-reversion bots on liquid crypto was found. The only related evidence is the reversal of losers within momentum papers.
- No academic study of "smart DCA" (DCA with indicator triggers) was found.

---

## 2. What practitioners report (Freqtrade/Hummingbot, bot marketplaces), and what fraction of retail bots are profitable

### Takeaway
No credible, audited statistic exists on the share of retail crypto bots that are profitable. Exchange bot marketplaces (Pionex, 3Commas, Binance) publish marketing, not outcome distributions. The closest proxies (copy-trading follower PnL, pump.fun wallets, production LLM agents) all point to most retail automated traders losing money or matching the market at best.

### Cited Findings
- Pionex's own blog says grid bots can be profitable in 2026, in sideways or mildly trending markets with good configuration, and claims the lowest fee drag at 0.05% maker/taker. This is vendor marketing. — [Pionex blog](https://www.pionex.com/blog/best-grid-trading-bot/)
- Affiliate review sites cite grid bots earning "0.5–2% a day when running." These are unaudited, affiliate-driven claims and should be treated as marketing. — [CoinCodeCap](https://coincodecap.com/grid-trading)
- Hummingbot (open-source market-making framework) argues individuals and small firms are better suited than large market makers for small-cap pairs, because big firms won't allocate inventory there. Hummingbot users get 10–20% fee rebates (OKX, KuCoin, Gate 20%; Binance 10%). — [Hummingbot liquidity mining paper](https://hummingbot.org/liquidity-mining.pdf); [Hummingbot FAQ](https://hummingbot.org/faq/)
- Third-party reviews say small accounts "may struggle to operate efficiently once fees, minimum order sizes, and spread dynamics are considered." User reports are mixed, and profitability comes only after a steep learning curve and tuning. — [Finestel review](https://finestel.com/blog/hummingbot-review/); [arti-trends review](https://arti-trends.com/ai-investment/hummingbot-review-2026/)
- Copy-trading follower profitability was 48.48%, varying by platform (Binance 66.5%, MEXC 57.79%, Bybit 43.65% win rates). Low-quality source. — [YieldFund](https://yieldfund.com/is-copy-trading-profitable-a-90-day-multi-exchange-study)
- LLM agent fleet in production: unprofitable, with a 41% round-trip win rate versus 50% for a matched Hyperliquid retail benchmark. — [arXiv 2609.05663](https://arxiv.org/abs/2609.05663)
- The CFTC advisory "AI Won't Turn Trading Bots into Money Machines" (Jan 2024) warns that bot and AI-arbitrage claims of huge returns are a fraud hallmark. — [CFTC](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html)

### Inferences
- Without audited distribution data, the safest prior from adjacent evidence is that a majority of retail bot users underperform buy-and-hold BTC after fees, and that many lose money outright.
- Marketplace "top bot" leaderboards suffer from survivorship bias, the same way copy-trading leaderboards do (only 12% of top traders stay on top for 6 months).

### Gaps
- No Freqtrade community dataset of live (not backtest) results was found. Freqtrade/Robot Wealth/Reddit concrete PnL data did not come up in searches.
- Pionex, 3Commas and Binance do not publish the share of grid/DCA bots closed at a profit. No independent dataset was found.
- No Kaiko, Binance Research or Coinbase Institutional report on retail bot performance was found.

---

## 3. Which edges have decayed or been arbitraged away, and why

### Takeaway
Triangular and simple cross-exchange arbitrage are effectively gone for retail: opportunities still show up in data but disappear after fees, depth and latency. MEV and sniping are dominated by fewer than about 20 professional entities per week on Ethereum and by auctions on Solana that push profits to validators. Funding carry has compressed substantially from 2024 to 2025. Trend following has not been arbitraged away, because it is a risk premium or behavioral effect rather than a mispricing.

### Cited Findings
- Triangular arbitrage on Binance: 4,879 opportunities were detected, but none were profitable after costs and depth. — [Finance Research Letters 2024](https://www.sciencedirect.com/science/article/pii/S154461232401537X)
- Triangular arb has three legs, each with a fee, and fees easily exceed the gap. Inefficiencies have shifted from obvious inter-exchange gaps to "subtle, fleeting mismatches often caused by latency and microstructure quirks." This is from a vendor blog. — [Altrady](https://www.altrady.com/blog/crypto-trading-strategies/crypto-arbitrage-guide-2026)
- Cross-exchange deviations decline over time but persist. — [J. Banking & Finance 2026](https://www.sciencedirect.com/science/article/pii/S0378426626000956)
- Carry Sharpe fell from 6.45 (full sample since 2020) to 4.06 (2024) to negative (2025). — [arXiv 2510.14435](https://arxiv.org/html/2510.14435v2)
- Carry exists because arbitrage capital is constrained by regulation and margin. Easing those frictions (e.g., spot ETFs, CME access) predicts compression. — [BIS WP 1087](https://www.bis.org/publications/working-paper-1087-crypto-carry)
- Ethereum MEV: fewer than about 20 core profitable entities per week, with more than 90% of revenue paid to proposers. — [Extropy](https://academy.extropy.io/pages/articles/mev-crosschain-analysis-2025.html)
- pump.fun is "dominated by automated sniper bots" that react within milliseconds. Twelve wallet clusters made 18% of launches and drained 82% of liquidity (about $4.2M, Jan–Apr 2025). — [Solidus Labs](https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance); [CryptoSlate](https://cryptoslate.com/how-traders-make-over-60k-per-week-rugging-98-of-memecoins-on-pumpfun/)
- In the ETF-era study, TSMOM's Sharpe rose from 0.82 to 1.22 after the spot ETF, so it has not decayed so far, though the post-ETF sample is short. — [Zenodo](https://zenodo.org/records/19671502)

### Inferences
- Pure-arbitrage strategies decay because they are a speed and cost race: whoever has the lowest fees (VIP tiers, rebates) and lowest latency (co-location, private order flow) captures them. Retail at 0.4–0.6% fees cannot compete.
- Strategies that earn compensation for bearing risk (trend, carry) decay more slowly. Carry is still crowding as institutional capital arrives.

### Gaps
- No 2024–2026 dataset quantifying retail-accessible cross-exchange spread sizes in bps after fees was found.

---

## 4. How each strategy performs vs buy-and-hold BTC, especially after fees

### Takeaway
After realistic fees, most retail bot strategies underperform buy-and-hold BTC in bull markets. Trend following's main documented edge is lower drawdown and better risk-adjusted return, and the Concretum top-20 version reports about 10.8% annual alpha versus BTC. Grid trading is roughly zero-expectancy relative to holding, because of inventory losses when price leaves the range. Carry is uncorrelated with HODL but its yield has fallen. Lump sum beats DCA in most historical BTC windows.

### Cited Findings
- Trend: Concretum reports net-of-fees Sharpe above 1.5 and about 10.8% annualized alpha versus BTC (backtest since 2015). — [SSRN 5209907](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907)
- Being out of the market is costly: missing the 15 best 3-day windows turned +127% into −84.6%. — [Amdax](https://medium.com/amdax-asset-management/lump-sum-or-dollar-cost-averaging-42c8f5bb9938)
- Grid: traditional grid expectation is about zero. The dynamic grid beat buy-and-hold on BTC/ETH (2021–Jul 2024) in the authors' backtest. — [arXiv 2506.11921](https://arxiv.org/abs/2506.11921)
- Funding arbitrage shows no correlation with HODL and much lower volatility. — [ScienceDirect 2025](https://www.sciencedirect.com/science/article/pii/S2096720925000818)
- ML prediction: positive gross, negative net, because of turnover. — [arXiv 2606.00060](https://arxiv.org/html/2606.00060v1)
- DCA vs lump sum: lump sum accumulated 3–75% more BTC (six-year sample), and wins in about 65–80% of windows. DCA reduces drawdowns. — [Amdax](https://medium.com/amdax-asset-management/lump-sum-or-dollar-cost-averaging-42c8f5bb9938); [Nakamoto Portfolio](https://nakamotoportfolio.com/static/docs/DCA_Lumpsum.pdf)
- US retail fee reality: Coinbase Advanced Trade's lowest tier (under $10k 30-day volume) is 0.60% taker and 0.40% maker. — [CoinCodeCap: Coinbase fees](https://coincodecap.com/coinbase-fees); [Financer](https://financer.com/review/coinbase)

### Inferences
- At 0.4–0.6% per side, a round trip costs about 0.8–1.2%. A grid with spacing under about 1% loses money on every filled cycle at Coinbase's base tier. A strategy trading weekly would pay roughly 40–60% per year in fees, which makes high-turnover bots non-viable for a small US account. A slow trend filter changing position a few times a year pays only a few percent.
- "Smart DCA" and indicator-triggered DCA bots have no rigorous evidence of beating plain recurring buys.

### Gaps
- No independent after-fee comparison of exchange grid/DCA bot cohorts versus BTC HODL over 2022–2026 was found.

---

## 5. Which strategies are viable with ~$20 vs needing thousands (US retail)

### Takeaway
With about $20, essentially nothing except long-only spot strategies (plain DCA/HODL, or a very low-turnover trend filter on BTC/ETH) is practical. Fees, order minimums and contract sizes rule out grids with tight spacing, market making, pairs, arbitrage and US-regulated perps. Carry needs hundreds to thousands of dollars plus derivatives access. MEV and sniping need infrastructure and are mostly fraud-adjacent for small buyers.

### Cited Findings
- US perps: Coinbase Financial Markets launched CFTC-regulated "perpetual-style" futures for US customers on July 21, 2025, with up to 10x leverage and fees from 0.02%. The nano BTC contract is 0.01 BTC and the nano ETH is 0.10 ETH. — [The Block](https://www.theblock.co/news/business/2025-07-22-coinbase-launches-perpetual-futures-363796); [Coinbase blog](https://www.coinbase.com/blog/perpetual-futures-have-arrived-in-the-us); [MarketsWiki](https://www.marketswiki.com/wiki/Nano_Bitcoin_Perpetual_Futures)
- Small accounts struggle with market making because of fees, minimum order sizes and spreads. — [Finestel](https://finestel.com/blog/hummingbot-review/)
- Pairs and arb returns depend on high frequency and low costs. — [Tandfonline](https://www.tandfonline.com/doi/abs/10.1080/10293523.2023.2268386); [FRL 2024](https://www.sciencedirect.com/science/article/pii/S154461232401537X)
- The best funding-arb result used 7x leverage on a DEX (Drift). Liquidation and settlement risk are explicit risk components. — [ScienceDirect 2025](https://www.sciencedirect.com/science/article/pii/S2096720925000818)
- Coinbase base-tier fees are 0.60% taker and 0.40% maker. — [CoinCodeCap](https://coincodecap.com/coinbase-fees)

### Inferences
- Per-strategy viability at about $20 (arithmetic and judgment from the cited facts):
  - **DCA/HODL, long-only spot BTC/ETH**: viable. Costs scale with size, and US exchanges allow fractional buys. Best evidence-to-cost ratio.
  - **Slow trend filter (e.g., in or out of BTC on a long moving average or Donchian signal)**: technically viable. A few trades a year at about 0.4–0.6% is affordable. On $20, the dollar outcome is cents to a few dollars a year, so the value is educational.
  - **Grid**: poor. Expected value is about zero before fees, and fees of 0.8–1.2% per round trip on Coinbase make tight grids negative. Pionex's 0.05% fee is lower, but Pionex's US availability is unverified (gap).
  - **Cash-and-carry / funding arb**: not viable at $20. A nano BTC perp is 0.01 BTC of notional. At any BTC price above $20,000, that notional exceeds $200, so even at 10x leverage the margin exceeds $20. The hedge also needs a matching spot leg. The trade has a capital floor of hundreds of dollars and realistically thousands for a margin buffer. The premium has also compressed or turned negative in 2025.
  - **Market making, pairs, triangular or cross-exchange arb**: not viable, because fees exceed edge and retail cannot compete on latency.
  - **ML/LLM bots**: no demonstrated net edge, and API/LLM costs alone could exceed returns on $20.
  - **Sniping, MEV, copy-trading memecoins**: negative expected value. About 98% of pump.fun tokens are rugs or pump-and-dumps, and MEV is won by fewer than 20 pros.
- Directional leverage on $20 is the most likely route to a total loss. The LLM-agent study found volatility-blind 5x median leverage, with one slider cell holding 62% of liquidations.

### Gaps
- Exact Coinbase nano-perp initial margin requirements and minimum account sizes were not found.
- Current minimum order sizes on Coinbase and Kraken were not verified in this session.
- Pionex availability to US residents in 2026 was not verified.

---

## 6. Common scams and failure modes

### Takeaway
The main failure modes are: (1) paid "guaranteed return" or AI-arbitrage bots, a pattern the CFTC flags as fraud; (2) API-key theft through phishing clones of bot platforms; (3) overfit backtests that collapse live; (4) leverage and liquidation; (5) rug pulls and pump-and-dumps that dominate memecoin sniping; (6) copy-trading leaderboard survivorship bias and Martingale-style leaders.

### Cited Findings
- CFTC: scammers claim AI bots, trade-signal algorithms and "crypto-asset arbitrage algorithms" generate huge returns. Red flags include "high guaranteed returns (for example, 20-50%)" with little or no risk. — [CFTC customer advisory](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/AITradingBots.html); [CFTC press release 8854-24](https://www.cftc.gov/PressRoom/PressReleases/8854-24); [CFTC fraudulent sites alert](https://www.cftc.gov/LearnAndProtect/AdvisoriesAndArticles/watch_out_for_digital_fraud.html)
- 3Commas, Oct 2022: FTX API keys linked to 3Commas were used for unauthorized trades on DMG pairs. 3Commas said the keys came from phishing sites impersonating 3Commas. (The 3Commas CEO later confirmed an API key leak in Dec 2022 per Cointelegraph.) — [The Block](https://www.theblock.co/post/179237/ftx-api-keys-3commas-exploited); [Cointelegraph](https://cointelegraph.com/news/3commas-ceo-confirms-api-key-leak-following-warning-from-cz)
- Overfitting and costs: many momentum portfolios that look statistically significant become insignificant or get liquidated under realistic assumptions. — [Han, Kang & Ryu](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565)
- An ML strategy earning 39% monthly gross was negative net. — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S2405918822000174)
- Pairs results are "quite sensitive to parameter settings." — [Tandfonline](https://www.tandfonline.com/doi/abs/10.1080/10293523.2023.2268386)
- Momentum tail risk: −255% crash in Dec 2020, and tail variance is undefined. — [Springer FMPM 2025](https://link.springer.com/article/10.1007/s11408-025-00474-9)
- Rug pulls: about 98.6% of pump.fun tokens collapsed into pump-and-dumps. Twelve clusters drained 82% of liquidity. — [Solidus Labs](https://www.soliduslabs.com/reports/solana-rug-pulls-pump-dumps-crypto-compliance); [CoinDesk](https://www.coindesk.com/business/2025/05/07/98-of-tokens-on-pump-fun-have-been-rug-pulls-or-an-act-of-fraud-new-report-says)
- Copy trading: followers trail leaders, and leaders with 300% ROI may have switched to Martingale strategies. A win rate above 57% can still lose money if losing trades are larger. — [KuCoin](https://www.kucoin.com/blog/is-crypto-copytrading-profitable-in-2026); [YieldFund](https://yieldfund.com/is-copy-trading-profitable-a-90-day-multi-exchange-study)
- LLM agents gave back gains: 49.3% of positions that reached +300 bps closed at a loss, with volatility-blind leverage. — [arXiv 2609.05663](https://arxiv.org/abs/2609.05663)
- Funding-arb hidden risks: liquidation, settlement and venue risk (FTX-type failure), stress-tested in the 2026 CEX-DEX paper. — [Springer 2026](https://link.springer.com/article/10.1007/s42521-026-00213-3)

### Inferences
- Practical safeguards supported by the evidence: use API keys with trading only (withdrawals disabled) and IP whitelisting; never pay for "guaranteed" bots; test on out-of-sample or walk-forward data with real fee levels; avoid leverage on tiny accounts; treat any memecoin sniping as gambling.

### Gaps
- No quantified total of retail losses specifically to fake trading-bot schemes for 2024–2026 was found. FTC and FBI IC3 crypto-investment-fraud totals were not retrieved in this session.
