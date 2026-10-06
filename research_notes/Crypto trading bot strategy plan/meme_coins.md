# Automated Meme Coin Trading Bots for a US Retail Individual (~$20 capital), 2026

Research date: 2026-10-06. Method note: arxiv.org, coingecko.com, decrypt.co and cnitarot.github.io were blocked by the network proxy in this session, so several academic/on-chain figures below come from search-engine abstracts/snippets of those primary sources rather than full-text reads. These are flagged "(snippet)" where relevant. Treat exact figures from snippets as likely-correct but not personally verified in full context.

## 1. Where meme coins trade in 2026, and US accessibility

### Takeaway
Solana (pump.fun bonding curve -> PumpSwap) remains the dominant venue for new meme coin launches; Base (Zora, Clanker) and BNB Chain (four.meme) are secondary and well behind on volume. Pump.fun does not geoblock US users for ordinary trading (it does block the UK and sanctioned countries), but US persons were excluded from its PUMP token sale. Large-cap meme coins (DOGE, SHIB, PEPE, BONK, WIF) trade on regulated US venues such as Robinhood.

### Cited Findings
- Pump.fun has ~11.9M total launches; fewer than 2% ever "graduate" to a DEX. Graduation occurs at ~$69K market cap (~85 SOL deposited in the bonding curve) — [Solana Compass](https://solanacompass.com/news/pumpfun-launched-42000-tokens-in-one-day-fewer-than-2-will-ever-reach-a-dex); [soltokencreator.io](https://www.soltokencreator.io/blog/pump-fun-graduation-explained)
- Pump.fun captured ~80% of Solana memecoin launches (Cointelegraph analysis) — [TradingView/Cointelegraph](https://www.tradingview.com/news/cointelegraph:9c3a24b10094b:0-how-pump-fun-captured-80-of-solana-memecoins-and-can-it-last/)
- Pump.fun fee schedule (last updated May 20, 2026): bonding curve charges a flat 1.25% per trade (0.30% creator + 0.95% protocol). PumpSwap (post-graduation AMM) base fee 0.25% (0.20% LPs, 0.05% protocol), plus a creator fee that is tiered by market cap (up to 0.95% above 420 SOL market cap, dropping to 0.05% at higher tiers) — [soltokencreator.io](https://www.soltokencreator.io/blog/pump-fun-fees-explained); [Blofin Academy](https://blofin.com/en/academy/education/pumpfun/pump-fun-fees-explained); [HackMD fee schedule](https://hackmd.io/@ywCDVVcJSvmW9RTEhuT1xw/Hy3x3i4Yxx); [blocmates on PumpSwap creator fee](https://www.blocmates.com/news-posts/pump-fun-s-dex-pumpswap-launches-0-05-creator-fee-on-transactions)
- Pump.fun Terms bar persons in jurisdictions sanctioned by the UK/US/EU/UN; it blocks the UK (since Dec 2024 after an FCA warning), Russia, Iran, Syria, Cuba, North Korea. It operates in ~160 countries without identity checks, and Similarweb data show the US supplying ~41.9% of recent visits. Terms last updated 25 Sept 2026 — [Datawallet](https://www.datawallet.com/crypto/pump-fun-restricted-countries); [pump.fun terms](https://pump.fun/docs/terms-and-conditions); [Binance Square on UK block](https://www.binance.com/en/square/post/17215888046034)
- US and UK buyers were excluded from pump.fun's ~$600M PUMP token sale — [Brave New Coin](https://bravenewcoin.com/insights/us-and-uk-buyers-excluded-from-pump-funs-600m-token-sale)
- Four.meme is BNB Chain's leading memecoin launchpad (77,000+ tokens since H2 2024); Zora (Base) mints creator/content coins with a 1% trading fee and fixed 1B supply; Clanker (Base, Farcaster-native) was acquired by Farcaster and has been surpassed by Zora on Base volume; Base and BNB remain "well behind Solana on daily volume" — [Coin Bureau](https://coinbureau.com/analysis/best-memecoin-launchpads); [QuickNode](https://www.quicknode.com/builders-guide/best/top-10-memecoin-launchpads)
- Robinhood (US) lists PEPE, BONK, WIF, SHIB (plus DOGE), tradable 24/7; Robinhood "Connect" lets users fund Uniswap wallets to trade long-tail meme coins — [CoinMarketCap Academy](https://coinmarketcap.com/academy/article/robinhood-lists-3-new-meme-coins-as-crypto-trading-expands-after-trumps-election); [crypto.news on WIF](https://crypto.news/robinhood-lists-dogwifhat-meme-coin/); [Yahoo Finance](https://finance.yahoo.com/news/robinhood-investors-now-buy-bonk-183231762.html); [Robinhood PEPE page](https://www.robinhood.com/us/en/crypto/PEPE)
- Graduation rate history: ~0.7–0.8% in Jul–Aug 2025; 1.15% later in 2025 after "cashback coin" incentives; 2.01% week of Mar 9–15, 2026; a spike to 6.7% on one day after the "BOOST" feature launch (vs. June 2026 average roughly 1/8 of that) — [Cryptopolitan](https://www.cryptopolitan.com/pump-fun-graduating-tokens-break-to-1-15-of-new-launches/); [CryptoRank](https://cryptorank.io/news/feed/542eb-pump-fun-graduating-tokens-break-to-1-15-of-new-launches); [99Bitcoins](https://99bitcoins.com/news/presales/pump-crypto-graduation-rate-price-analysis/); [Cryptopolitan six-month high](https://www.cryptopolitan.com/pump-fun-token-graduations-six-month-high/)

### Inferences
- A US retail user can technically use pump.fun and Solana DEX aggregators (Jupiter) via a self-custody wallet today; legal access is not the binding constraint — economics and fraud are.
- The only meme coin venues with US regulatory oversight, broker 1099 reporting and no smart-contract/rug risk are CEX/brokers (Robinhood, Coinbase, Kraken), limited to a handful of large-cap meme coins.
- Graduation-rate spikes are driven by platform incentive changes (cashback, BOOST), so "graduation" is a moving and partly gameable signal, not a stable survival rate.

### Gaps
- Could not confirm whether Jupiter's or Axiom's front-ends geoblock US IPs in 2026 (none found reported). Did not verify Coinbase/Kraken current US meme coin listing lists in full.
- No reliable source found for 2026 market-share split (Solana vs Base vs BNB) in daily memecoin volume — only qualitative "well behind".

## 2. Bot strategy types and Telegram/web bot fees

### Takeaway
Common strategies are launch sniping, copy-trading "smart money", DEX momentum, and CEX trend-following. Telegram/web trading bots charge ~0.75–1% per trade on top of on-chain fees; academic work shows copy-traders are structurally disadvantaged ("imitation penalty") and actively farmed by manipulative bots/KOLs.

### Cited Findings
- Bot fees (2026): Trojan ~0.9% (volume tiers lower it), Axiom 0.95% start, down to ~0.75% net via SOL cashback tiers, Photon ~1%, BONKbot 1% flat, GMGN 0.8–1% — [solanatools.io](https://solanatools.io/blog/solana-trading-bot-fees-compared); [axiompedia](https://axiompedia.com/compare); [memegateway](https://memegateway.com/academy/solana-trading-bot-fees-compared-2026/); [madeonsol fee calculator](https://madeonsol.com/compare-bots)
- One fee-comparison site estimates true per-trade cost on a typical pump.fun migration as: 1.0% bot fee + 0.1–0.3% priority/Jito + 0.5–2% slippage + occasional MEV losses (vendor/affiliate site; treat as indicative) — [solanatools.io](https://solanatools.io/solana-trading-bot-fees)
- Copy-trading study (arXiv 2601.08641, 2026): KOLs coordinate multiple bots to accumulate early, inflate prices while concealing exposure, and wash trade to fake demand, using copy traders as exit liquidity; even an instantaneous copier trades at a worse point on the bonding curve ("imitation penalty"); taxonomy of bundle, sniper, bump and comment bots (snippet) — [arXiv 2601.08641](https://arxiv.org/html/2601.08641v2)
- Coordinated Sniper Cohorts paper (arXiv 2607.02795): 1,578,333 buyer observations across 166,098 pump.fun launches (Jun 12–26, 2026) found 1,012 persistent wallet cohorts (2–12 wallets, 2,965 addresses) that repeatedly co-fire as early buyers; top cohort (9 wallets) was among first 10 buyers of 42 launches in 11 days at average rank 2.29. Cohort-touched launches show +132% first-30-minute buyer counts, but placebo tests indicate selection (snipers pick winners) rather than causal effect (snippet) — [IDEAS/RePEc](https://ideas.repec.org/p/arx/papers/2607.02795.html); [arXiv](https://arxiv.org/abs/2607.02795)
- Meme Coin Factories (arXiv 2609.10246, 2026): analysed all ~15M pump.fun coins over two years; top 1% of creator groups create 58.6% of all coins; bots account for 60–80% of trading volume; 3.5M (23.5%) coins created after Twitter/Truth Social posts; "Market-Manipulation-as-a-Service" tools sold to non-technical users; five manipulation classes: wash trading, creator address obfuscation, coordinated sell, copycat coins, social media manipulation (snippet) — [arXiv 2609.10246](https://arxiv.org/html/2609.10246v1)

### Inferences
- Launch sniping is a latency/infrastructure race dominated by persistent professional wallet rings co-located with validators; a $20 retail bot on a public RPC will systematically be later than them and thus buying from them.
- Copy-trading is mechanically disadvantaged (always worse fill) and adversarially targeted; "smart money" wallet lists published by GMGN etc. are exactly what manipulators farm.
- Bot fees of ~1% per side are a guaranteed ~2% round-trip drag, before pump.fun's 1.25% per side.

### Gaps
- No independent, audited P&L data on users of any specific Telegram bot (Trojan, BonkBot, etc.) was found; bot marketing ("X% win rate") is unverifiable.
- No data found on profitability of DEX momentum/breakout bots for small accounts.

## 3. Hard data on outcomes (survival, profitability, rugs, MEV)

### Takeaway
The overwhelming majority of new meme coins die or are scams (Solidus: 98.6% of pump.fun tokens tied to rug/pump-and-dump patterns; <2% graduate). Wallet "profitability" rates swing wildly (30% mid-2025 to 73% in April 2026) because losers exit; profits for most "winners" are tiny ($1–$500). Sandwich MEV on Solana extracted hundreds of millions, disproportionately from high-slippage memecoin traders.

### Cited Findings
- Solidus Labs (2025): of 7M+ pump.fun tokens (Jan 2024–Mar 2025), 98.6% associated with rug pulls/pump-and-dumps; fewer than 100,000 kept liquidity above $1,000; 93% of Raydium liquidity pools showed rug/pump-and-dump signs; median Raydium rug $2,832, 25% under $732 — [Forklog](https://forklog.com/en/report-98-of-pump-funs-memecoins-deemed-scams/); [The Defiant](https://thedefiant.io/news/defi/alarming-99-of-memecoin-launches-on-pumpfun-are-pump-and-dumps-or-rug-pulls-report); [Bitcoin.com News](https://news.bitcoin.com/report-exposes-98-6-of-solana-meme-coins-on-pump-fun-as-fraudulent/)
- CoinGecko (2026): share of profitable pump.fun traders (active wallets with exited positions) 30.08% low in June 2025; 50.08% Jan 2026, 56.83% Feb, 70.00% Mar, 73.28% Apr 2026. ~2.05M wallets (65.14%) recorded gains of only $1–$500; just 168,795 wallets (5.37%) cleared >$1,000. CoinGecko attributes the rise to unprofitable traders leaving: monthly active wallets fell from a 5.2M peak (May 2025) to 1.8M (Dec 2025) — [Yahoo Finance](https://finance.yahoo.com/markets/crypto/articles/73-pump-fun-traders-profit-094850577.html); [BeInCrypto](https://beincrypto.com/pump-fun-traders-profit-comeback-meme-coin-season/); [CoinInsider](https://www.coininsider.com/news/pump-fun-hits-two-year-high-as-73-of-traders-turn-profitable-in-april-2026); [CoinGecko research (primary, not fetched)](https://www.coingecko.com/research/publications/pump-fun-traders-are-making-a-comeback)
- Earlier on-chain analysis (Decrypt, ~Jan 2025): only 0.4% of pump.fun traders had made more than $10,000 (headline; full article blocked) — [Decrypt](https://decrypt.co/300403/pump-fun-traders-millionaires)
- "A Midsummer Meme's Dream" (USENIX Security 2026; 34,988 tokens across Ethereum, BNB, Solana, Base): 82.89% of high-return (>100%) tokens show evidence of artificial growth (wash trading, liquidity-pool-based price inflation); identified 17,000+ victim addresses with realized losses >$9.3M (note: one search summary attributed the $9.3M figure to "Meme Coin Factories" — it appears to belong to this paper) — [arXiv 2507.01963](https://arxiv.org/html/2507.01963v2); [USENIX](https://www.usenix.org/conference/usenixsecurity26/presentation/mongardini)
- Chainalysis (2022 data, older/outdated context): 24% of new tokens launched that year fell 90%+ in the first week (pump-and-dump signature); 9,900+ tokens on BNB/Ethereum; ~445 groups profited ~$30M — [Forklog citing Chainalysis](https://forklog.com/en/?p=74261) (via search summary)
- Solana sandwich MEV: $370M–$500M extracted over ~16 months (2024–25); memecoin traders especially vulnerable due to high slippage settings; early-2025 analysis counted 500K+ sandwiches with ~$7.7M victim losses (different scope/time window); >$3.2M SOL extracted in Oct 2025 alone; Jito shut its public mempool in March 2024 but sandwiching continued via other block engines/modified validators; JitoSOL committee banned 15 more validators; coordinated measures cut sandwich profitability 60–70% in 2025 — [Helius MEV report](https://www.helius.dev/blog/solana-mev-report); [Solana Compass Accelerate](https://solanacompass.com/learn/accelerate-25/scale-or-die-at-accelerate-2025-the-state-of-solana-mev); [CryptoRank](https://cryptorank.io/news/feed/4d1c4-jito-bans-15-additional-validators-after-data-emerges-of-widespread-sandwich-attacks); [99Bitcoins](https://99bitcoins.com/news/altcoins/sandwich-attacks-spiraling-out-of-control-on-solana-over-3-2m-of-sol-crypto-extracted-in-october/); [CryptoNinjas](https://www.cryptoninjas.net/news/solana-slashes-500m-sandwich-attacks-as-75-of-sol-gets-staked-in-2025-security-overhaul/)
- Peer-reviewed measurement: "Quantifying the Threat of Sandwiching MEV on Jito" (ACM IMC 2025) — [ACM DL](https://dl.acm.org/doi/10.1145/3730567.3764493) (full text not retrievable here)
- Insiders hide concentration by splitting holdings across multiple accounts (bundling); MemeTrans/MELT dataset covers 41k+ launches with bundled-account traces — [arXiv 2602.13480](https://arxiv.org/html/2602.13480v1)

### Inferences
- The 73% "profitable" figure is survivorship-biased (losers left; denominator shrank ~65%) and measures count of wallets, not dollars; the median "winner" made under $500. It does not imply a new entrant has a 73% chance of profit.
- The sandwich loss range ($7.7M vs $370–500M) reflects different methodologies/scopes; the consistent point is that high slippage settings typical in memecoin bots are the attack surface.
- Base rate for a random new launch is near-total loss; any edge must come from filtering, and the Midsummer paper says even "winners" are mostly manufactured.

### Gaps
- No found study measuring net profitability of retail Telegram-bot users specifically, or sniper-bot net P&L after fees.
- CoinGecko's exact profit definition (fees included? SOL price effects?) not verified because the primary page was blocked.

## 4. Costs per trade for a ~$20 account

### Takeaway
Stacking pump.fun's 1.25% curve fee, ~1% bot fee, slippage and priority tips, a round trip on a fresh pump.fun token costs roughly 5–9% of position size, plus ~0.002 SOL refundable rent per new token account. With zero gross edge, ~10 round trips would cut $20 roughly in half.

### Cited Findings
- Pump.fun bonding curve fee 1.25% per trade; PumpSwap 0.25% + tiered creator fee — [soltokencreator.io](https://www.soltokencreator.io/blog/pump-fun-fees-explained)
- Telegram/web bot fee ~0.75–1% per trade — [solanatools.io](https://solanatools.io/blog/solana-trading-bot-fees-compared)
- Slippage on pump.fun migrations 0.5–2%; priority/Jito 0.1–0.3% (indicative, vendor site) — [solanatools.io](https://solanatools.io/solana-trading-bot-fees)
- Each new SPL token account requires a rent deposit of ~0.00203928 SOL (refundable when the emptied account is closed) — [Raydium docs](https://docs.raydium.io/solana-fundamentals/rent-and-reclaimable-rent); [Solana docs](https://www.solana.com/docs/tokens/basics/close-account)
- Zora creator/content coins carry a 1% trading fee — [Coin Bureau](https://coinbureau.com/analysis/best-memecoin-launchpads)
- CEX fees: Kraken Pro entry tier 0.40% maker / 0.80% taker — [Kraken support](https://support.kraken.com/hc/en-us/articles/201893638); Coinbase Advanced entry tier reported variously as 0.60%/1.20% or 0.50%/0.90% (maker/taker) — sources conflict and Coinbase requires login to view tiers — [financer.com](https://financer.com/review/coinbase); [DiarioBitcoin](https://www.diariobitcoin.com/exchanges/coinbase-reduce-sus-comisiones-de-advanced-y-baja-el-umbral-inicial-a-usd-10-000/); [conductatlas](https://conductatlas.com/platform/coinbase/coinbase-fee-schedule/advanced-trade-makertaker-fee-schedule)

### Inferences (my arithmetic, not sourced figures)
- Pump.fun bonding-curve round trip via a Telegram bot: 2 x (1.25% + ~1% bot + 0.5–2% slippage) ≈ 5.5–8.5%, before priority tips. On a $20 position that is ~$1.10–$1.70 per round trip.
- Priority fees/Jito tips are usually set as fixed SOL amounts, not percentages, so on a $5–$20 trade they are proportionally much larger than the 0.1–0.3% cited for typical (larger) trades.
- Token account rent at an assumed SOL price of $150 is ~$0.31 per new token (~1.5% of $20) locked until the user closes the account.
- Compounding: at ~7% round-trip cost and zero edge, $20 x 0.93^10 ≈ $9.68 after 10 round trips; ~$4.70 after 20. A bot trading several times a day would exhaust $20 in days on costs alone.
- On a CEX at ~0.8–1.2% taker, a round trip costs ~1.6–2.4%; maker limit orders roughly halve that. Still a large hurdle for frequent trading, but far below on-chain memecoin costs and with no rug risk.

### Gaps
- Did not find a current authoritative figure for median Solana priority fee/Jito tip in SOL during 2026, nor current Base gas cost per swap.
- Robinhood's crypto spread on meme coins (commission-free but spread-based) not found in a sourced form.

## 5. Security risks (custody, hacks, scam bots)

### Takeaway
Telegram bots are custodial or semi-custodial hot wallets and have been exploited repeatedly; fake "pump.fun bot" GitHub repos with inflated stars steal private keys. Running unknown open-source sniper code with a funded key is a major risk.

### Cited Findings
- Banana Gun (Sept 2024): ~$3M exploit via a Telegram message-oracle vulnerability affecting 11 users; unauthorized manual transfers; bot halted; added 2FA and 2-hour transfer delay; treasury reimbursement pledged — [The Defiant](https://thedefiant.io/news/defi/banana-gun-pledges-to-pay-back-victims-of-usd3-million-exploit); [The Block](https://www.theblock.co/post/317282/banana-gun-telegram-bot); [Rekt](https://rekt.news/bananagun-rekt)
- Unibot (Oct 2023): >$600K stolen via call-injection on its router contract from wallets that had not revoked approvals; Maestro also lost ~$200K in a similar exploit — [The Defiant](https://thedefiant.io/news/defi/hacker-ransacks-usd600-000-from-popular-telegram-trading-bot-unibot)
- Fake GitHub repo "solana-pumpfun-bot" (account zldp2002, July 2025): Node.js project with obfuscated dependency "crypto-layout-utils" that scanned local files and uploaded private keys; inflated stars/forks; multiple malicious forks (SlowMist investigation) — [Cointelegraph](https://cointelegraph.com/news/solana-trading-bot-github-malware-scam); [Radom](https://www.radom.com/insights/crypto-theft-alert-scammers-use-github-bot-to-target-solana-users)
- Malicious npm packages stealing Solana private keys also reported — [MEXC News](https://www.mexc.com/news/malicious-npm-package-steals-private-keys-solana-user-assets-are-stolen/33630)

### Inferences
- Any bot that holds the private key (all Telegram bots, most web terminals) carries counterparty/hack risk; minimum hygiene is a dedicated burner wallet holding only the $20, never a main wallet.
- GitHub stars are not a trust signal for trading-bot code; review dependencies or use well-known SDKs only.

### Gaps
- No found 2025–2026 major exploit of Trojan/Axiom/Photon/GMGN specifically (absence of evidence in this search, not proof of safety).

## 6. Lower-risk meme coin approach for a bot

### Takeaway
The lowest-risk automated "meme coin" approach is trend-following or simple rules on liquid large-cap meme coins (DOGE, SHIB, PEPE, BONK, WIF) on a regulated US venue, using limit orders and low trade frequency. If trading on-chain at all, safety filters (revoked mint/freeze authority, locked/burned LP, holder concentration incl. bundled wallets) reduce but do not eliminate rug risk, and evidence suggests manipulated tokens dominate even the "winners".

### Cited Findings
- Robinhood lists PEPE, BONK, WIF, SHIB, tradable 24/7 — [CoinMarketCap Academy](https://coinmarketcap.com/academy/article/robinhood-lists-3-new-meme-coins-as-crypto-trading-expands-after-trumps-election)
- Insiders hide concentration across multiple accounts (bundling), so naive top-holder checks understate concentration — [arXiv 2602.13480](https://arxiv.org/html/2602.13480v1); snipers/bundlers detection docs — [Webacy](https://docs.webacy.com/glossary/snipers-bundlers.md); [Mobula](https://docs.mobula.io/almanac/detecting-snipers-bundlers)
- 82.89% of high-return meme tokens show artificial growth — [arXiv 2507.01963](https://arxiv.org/html/2507.01963v2)
- An open-source "filter-first" sniper exists with rug/honeypot/dev-history filters and paper-trading by default (example only; not vetted) — [GitHub](https://github.com/vineetdev02/Memcoin-Sniper-Bot)

### Inferences
- Realistic lowest-risk path for $20: (1) paper-trade first; (2) if live, use a US broker/exchange for a large-cap meme coin with a slow trend rule (e.g., daily/4h moving-average crossover), few trades per month, limit (maker) orders; (3) accept that fees still make edge hard and that meme coins carry extreme drawdowns (often 80–90%+ in bear phases — general market knowledge, not sourced here).
- On-chain, the "least bad" bot design would trade only graduated tokens with deep pools, cap slippage tightly (to reduce sandwich exposure), run filters (mint/freeze revoked, LP burned/locked, top-10 holders and bundle clusters via RugCheck-style tools), and use a burner wallet. Expected value remains doubtful given the data in sections 3–4.
- Expected value framing: with ~1–2% graduation, 98.6% scam-associated launches, professional sniper rings and 5–9% round-trip costs, a $20 automated sniping/copy bot should be modeled as a negative-EV lottery ticket / learning expense.

### Gaps
- No rigorous backtest found of trend-following on DOGE/PEPE/etc. net of US retail fees.
- RugCheck's own documentation on scoring methodology was not fetched; effectiveness of such filters is not quantified in any study found.

## 7. US tax and legal notes

### Takeaway
Every swap (including token-to-token on a DEX) is a taxable disposition of property; DEX trades produce no 1099 so the user must self-track; the wash-sale rule does not apply to crypto as of mid-2026. The SEC staff says meme coins are generally not securities, but fraud/manipulation (pump-and-dump, insider schemes) remains actionable under other laws.

### Cited Findings
- SEC Staff Statement (Feb 27, 2025): meme coins are "akin to collectibles", generally not securities under Howey; not binding on the Commission; does not cover disguised securities; fraudulent conduct remains subject to other federal and state laws — [Winston & Strawn](https://winston.com/en/blogs-and-podcasts/non-fungible-insights-blockchain-decrypted/sec-staff-under-new-administration-issues-statement-declaring-that-meme-coins-are-not-securities); [Polsinelli](https://www.polsinelli.com/publications/staff-statement-on-meme-coins-signals-shift)
- Form 1099-DA issued starting January 2026 for 2025 proceeds; cost-basis reporting phases in for 2026 trades; Congress repealed the IRS DeFi broker rule in April 2025, so self-custody/DEX trades produce no 1099 and reporting falls on the investor; wash-sale rule (IRC 1091) applies only to stocks/securities, crypto treated as property since 2014 — [Harness](https://www.harness.co/articles/new-1099-da-broker-reporting-rules-for-2026-what-crypto-investors-need-to-know); [Harness on wash sales](https://www.harness.co/articles/crypto-tax-loss-harvesting-in-2026-does-the-wash-sale-rule-still-not-apply); [Beancount](https://beancount.io/es/blog/2026/05/10/form-1099-da-digital-asset-broker-reporting-2026-crypto-investors-cost-basis-form-8949-guide)
- Crypto-to-crypto swaps are taxable events — [DEXTools tutorial](https://www.dextools.io/tutorials/do-you-pay-tax-on-a-crypto-to-crypto-swap-irs-rules)

### Inferences
- A bot making hundreds of micro-swaps creates hundreds of Form 8949 line items; tax-tracking software cost/effort may exceed the $20 stake.
- Launching or coordinating a token pump (as creator/insider) carries fraud exposure even if the token is not a security; a buyer-only bot does not, but participating in coordinated "pump groups" could.
- The wash-sale status could change with legislation; flag for re-check.

### Gaps
- Did not find a 2026 DOJ/CFTC enforcement case specifically against a pump.fun insider; CFTC jurisdiction over meme coins as commodities not researched here.
