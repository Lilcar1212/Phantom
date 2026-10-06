# SURVIVOR: research notes for a $20 autonomous meme-coin bot

Research date: **2026-10-06**. Audience: the SURVIVOR builder (US resident, Windows, Python 3.11). Capital: $20 USDC. The user accepts losing all of it.

**Bottom line.** Use **Solana**, executing through **Jupiter Swap API v2** at `https://api.jup.ag`, with a free API key. Trade only tokens that pass a strict, on-chain-verifiable filter. Prefer slow strategies on already-established meme tokens over new-listing sniping. A $3 round trip on an established, liquid token costs about **1.8%**. On a token under 24 hours old it costs about **8–9%**, and up to **16%** with tips. Forgetting to close a token account adds **another ~8%** in locked rent. **The most likely outcome of running this bot is a loss of most or all of the $20** (section 9).

---

## 0. How this was verified (read first)

**Live API probes: every one was blocked.** This session's egress proxy refused CONNECT (HTTP 403) to every target host. That covers both `curl` and the server-side WebFetch tool. Hosts tried at about 2026-10-06T20:00Z:

`lite-api.jup.ag`, `api.jup.ag`, `quote-api.jup.ag`, `dev.jup.ag`, `developers.jup.ag`, `station.jup.ag`, `jup.ag`, `api.dexscreener.com`, `docs.dexscreener.com`, `api.geckoterminal.com`, `apiguide.geckoterminal.com`, `public-api.birdeye.so`, `docs.birdeye.so`, `api.rugcheck.xyz`, `api.gopluslabs.io`, `mainnet.helius-rpc.com`, `www.helius.dev`, `docs.helius.xyz`, `api.mainnet-beta.solana.com`, `mainnet.block-engine.jito.wtf`, `bundles.jito.wtf`, `frontend-api-v3.pump.fun`, `mainnet.base.org`, `bsc-dataseed.bnbchain.org`, `api.coingecko.com`.

So **no endpoint in this document is "verified live"**. Every API row below carries "verified live on 2026-10-06: **no** (blocked by proxy)".

**What was verified instead.** Primary-source documentation was fetched on 2026-10-06 from places the proxy allowed:
- **Raw GitHub files** from the vendors' own repos. These were Jupiter's docs repo (`jup-ag/docs`) and agent-skill repo (`jup-ag/agent-skills`), Solana's docs repo (`solana-foundation/solana-com`), Jito's docs repo (`jito-labs/jito-docs`) and pump.fun's program docs (`pump-fun/pump-public-docs`). They also included the Helius SDK README and a third-party DexScreener client.
- **Vendor SDK packages** downloaded from npm and PyPI and inspected:
  - `@jup-ag/api` 6.0.48 (published 2025-12-28)
  - `helius-sdk` 3.2.0 (2026-09-08)
  - `goplus` 0.2.6 (2026-08-21)
  - `geckoterminal-py` 0.3.1 (2026-07-02)
  - `rugcheck` 1.0.0 (community, 2025-02-11)
- **Search-engine summaries** of pages that could not be fetched. These are marked **(snippet)**.

**Treat as a to-do.** On the first run from the user's Windows machine, run the probe checklist in §4.11 and record real HTTP statuses before trusting any row.

Re-used facts from the earlier notes are cited to their original sources. Those notes are in `research_notes/Crypto trading bot strategy plan/` and `reports/Crypto trading bot strategy plan.md`.

---

## 1. How meme coins work (Solana-centric)

### 1.1 Pump.fun bonding curve to PumpSwap (verified from pump.fun's own program docs)
- **Launch.** `create_v2` mints a **Token-2022** mint (`TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`) with 6 decimals and a metadata pointer. The mint authority is a Pump PDA ([pump COIN_CREATION.md](https://github.com/pump-fun/pump-public-docs/blob/main/docs/instructions/COIN_CREATION.md)). Older coins used the classic SPL Token program. A bot must handle both programs.
- **Curve.** It is a Uniswap-V2-style constant product over *virtual* reserves. Global parameters ([PUMP_PROGRAM_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/PUMP_PROGRAM_README.md)):

  | Parameter | Value |
  |---|---|
  | `initial_virtual_sol_reserves` | 30 SOL |
  | `initial_virtual_token_reserves` | 1.073B tokens |
  | `initial_real_token_reserves` | 793.1M tokens |
  | `token_total_supply` | 1B tokens |
  | `pool_migration_fee` | ~0.015 SOL |

- **Graduation (my arithmetic from those parameters).** k = 30 × 1.073B. When all 793.1M real tokens are sold, virtual token reserves are 279.9M and virtual SOL is about 115.0 SOL. Real SOL deposited is therefore about **85 SOL**. The price at completion implies a **market cap of about 411 SOL**, roughly $49k at SOL ≈ $120. Earlier notes cite "~$69K"; that figure assumed a higher SOL price. `complete` flips to true when `real_token_reserves == 0`. Anyone can then call the permissionless `migrate`, which moves liquidity to **PumpSwap**. "The LP tokens received from the PumpSwap pool are then burnt" (same doc). Raydium migration (`withdraw`) is disabled.
- **Fees.**
  - Bonding curve: about 1.25% per trade (0.95% protocol + 0.30% creator, schedule of May 2026) ([soltokencreator.io](https://www.soltokencreator.io/blog/pump-fun-fees-explained)).
  - PumpSwap: LP fee 20 bps + protocol 5 bps ([PUMP_SWAP_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/PUMP_SWAP_README.md)), plus a creator fee.
  - Since 2025-09-01, a dynamic fee program applies to curves and canonical PumpSwap pools. Protocol and creator bps are set by market-cap tier ([FEE_PROGRAM_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/FEE_PROGRAM_README.md)). Read the actual tier from `/order`'s `feeBps` and route data, not from constants.
- **Recent changes** ([pump README](https://github.com/pump-fun/pump-public-docs/blob/main/README.md)):
  - USDC-quoted coins via `buy_v2` / `sell_v2`.
  - "Holder rewards" coins.
  - Cashback mode deprecated.
  - "Mayhem mode" flag.
  - PumpSwap `virtual_quote_reserves`, which may be **negative** from Sept 30.
  - Takeaway: on-chain math changes often. Prefer Jupiter quotes over hand-rolled curve math.
- **Graduation rates:**
  - ~0.7–2% historically, with spikes driven by incentive changes ([notes §1](../research_notes/Crypto%20trading%20bot%20strategy%20plan/meme_coins.md)).
  - An academic sample found **0.63% of 655,770 tokens** graduated ([arXiv 2602.14860](https://arxiv.org/abs/2602.14860), snippet).
  - Wash-traded coins graduate *more* often: 2.0% vs 0.90% ([arXiv 2609.10246](https://arxiv.org/html/2609.10246v1), snippet). Graduation is a gameable signal.

### 1.2 DEX pools, liquidity, LP burn and lock
- After launch, price comes from AMM pools: PumpSwap, Raydium (CPMM/CLMM/LaunchLab), Meteora (DLMM/DAMM/DBC, which Jupiter Studio uses), Orca and others. Jupiter routes across them ([Jupiter swap overview](https://github.com/jup-ag/docs/blob/main/swap/index.mdx)).
- For a constant-product pool with quote-side reserve R, a buy of size Δ moves price by roughly Δ/(R+Δ). "Liquidity" on DexScreener and GeckoTerminal is usually both sides in USD, so R ≈ liquidity/2.
- **LP burn or lock** means the pool creator cannot withdraw liquidity. Pump.fun graduates have protocol-burned LP. For other pools, check the LP-locked % (RugCheck `markets[].lp.lpLockedPct`; GoPlus `lp_holders`, `locked_detail`). PumpSwap's `lp_supply` field deliberately ignores user burns ([PUMP_SWAP_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/PUMP_SWAP_README.md)), so do not compute burn % from it.
- **Jupiter's market-listing rule** is a useful liquidity sanity bar. Tokens under 30 days old get instant routing. Normal routing requires "< 30% loss on $500 round-trip OR < 20% price impact comparing $1k vs $500" ([Jupiter skill](https://github.com/jup-ag/agent-skills/blob/main/skills/integrating-jupiter/SKILL.md)).

### 1.3 Authorities and Token-2022 extensions (the Solana "contract risk" surface)
Solana tokens use one of two standard programs, so honeypot vectors are a **finite, enumerable set of flags**. That differs from EVM, where any contract code can hide a sell block or tax. This is a structural reason to prefer Solana for an automated filter.

| Flag | Where to read it | Risk |
|---|---|---|
| **Mint authority** not null | mint account (`getAccountInfo` jsonParsed: `mintAuthority`) | Infinite dilution. |
| **Freeze authority** not null | mint `freezeAuthority` | Issuer can freeze *your* account after you buy. This is the classic Solana honeypot ([DEXTools](https://www.dextools.io/tutorials/freeze-authority-and-update-authority-scams)). A frozen account can still be closed only if its balance is zero ([Solana docs](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/basics/close-account.mdx)). |
| **TransferFeeConfig** (Token-2022) | mint `extensions` | Tax on every transfer, withheld for the fee authority ([Solana docs: transfer fees](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/transfer-fees.mdx)). The fee *config can be changed* by its authority (GoPlus reports `transfer_fee_upgradable`). |
| **TransferHook** | mint `extensions` | Arbitrary program runs on every transfer and can block sells ([Solana docs: transfer hook](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/transfer-hook.mdx)). |
| **PermanentDelegate** | mint `extensions` | Delegate "can transfer or burn tokens from any account for that mint" ([Solana docs](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/permanent-delegate.mdx)), so your tokens can be seized. |
| **NonTransferable**, **DefaultAccountState=Frozen**, **Pausable** | mint `extensions` ([extension list](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/index.mdx)) | Cannot transfer or sell, new accounts start frozen, or the issuer can pause all transfers. |
| Mutable metadata | Metaplex/TokenMetadata update authority | Rename or impersonation risk; minor for trading. |

**Policy for SURVIVOR:**
- Require mint authority = null and freeze authority = null.
- Allow only these Token-2022 extensions: `MetadataPointer`, `TokenMetadata`, `ImmutableOwner` (account-level).
- Reject any `TransferFeeConfig` (even at 0 bps, because it is upgradable), `TransferHook`, `PermanentDelegate`, `NonTransferable`, `DefaultAccountState`, `Pausable`, confidential-transfer extensions, and anything unknown.

### 1.4 Holder concentration, dev wallets, bundled launches
- **Top-holder %.** Use RPC `getTokenLargestAccounts` (top 20 token accounts) and `getTokenSupply`, or Jupiter Tokens v2 `audit.topHoldersPercentage` (0–100 scale) and `audit.devBalancePercentage`. **Exclude pool vaults, the bonding-curve account and burn addresses** before computing.
- **Dev history.** Jupiter `audit.devMints` and `audit.devMigrations` count prior launches and graduations by the creator ([Jupiter skill](https://github.com/jup-ag/agent-skills/blob/main/skills/integrating-jupiter/SKILL.md)). Serial creators are a red flag: the top 1% of creator groups make 58.6% of all pump.fun coins ([arXiv 2609.10246](https://arxiv.org/html/2609.10246v1), snippet).
- **Bundles.** The creator and allied wallets buy in the launch block, usually via Jito bundles (≤5 transactions, atomic). This hides insider supply across many wallets, so naive top-10 checks **understate** concentration ([arXiv 2602.13480](https://arxiv.org/html/2602.13480v1); [Mobula](https://docs.mobula.io/almanac/detecting-snipers-bundlers)). Persistent sniper cohorts exist: 1,012 cohorts were found in two weeks of June 2026 ([arXiv 2607.02795](https://arxiv.org/abs/2607.02795)). RugCheck reports insider-network detection, and Birdeye and GMGN-style tools flag "bundled %". **No free, verified API for bundle % was confirmed here** (gap).

---

## 2. Failure modes, quantified where data exists

| Failure mode | Mechanism | Data |
|---|---|---|
| **Rug / pump-and-dump** | Creator or insiders dump, or pull un-burned liquidity | 98.6% of 7M+ pump.fun tokens (Jan 2024–Mar 2025) showed rug or P&D patterns. Fewer than ~100k kept >$1k liquidity. 93% of Raydium pools showed signs. Median Raydium rug $2,832 ([Solidus via CoinDesk](https://www.coindesk.com/business/2025/05/07/98-of-tokens-on-pump-fun-have-been-rug-pulls-or-an-act-of-fraud-new-report-says)). 12 wallet clusters drained 82% of liquidity (~$4.2M, Jan–Apr 2025) ([CryptoSlate](https://cryptoslate.com/how-traders-make-over-60k-per-week-rugging-98-of-memecoins-on-pumpfun/)). |
| **Honeypot** | Freeze authority, transfer hook, non-transferable, pausable, permanent delegate, transfer fee (§1.3) | No population-level rate found (gap). The vectors are fully detectable from mint data *before* buying, **except** a future freeze by a live freeze authority. Hence the hard requirement that freeze authority = null. |
| **Insider / bundled supply** | Supply split across wallets that dump on buyers | Copy-traders face an "imitation penalty" and are used as exit liquidity ([arXiv 2601.08641](https://arxiv.org/html/2601.08641v2), snippet). |
| **Wash trading / fake volume** | Self-trades inflate volume, holder counts and "trending" ranks | 82.89% of >100%-return meme tokens show artificial growth ([USENIX Sec '26 / arXiv 2507.01963](https://arxiv.org/html/2507.01963v2)). Bots make 60–80% of pump.fun volume ([arXiv 2609.10246](https://arxiv.org/html/2609.10246v1), snippet). An estimated 41.4% of Solana memecoin and NFT volume is wash trading (Flip Research, via [Bitquery](https://bitquery.io/blog/solana-volume-numbers-are-a-lie), snippet). Jupiter exposes `organicScore` and `buyOrganicVolume` to partly correct for this ([Tokens v2 doc](https://github.com/jup-ag/docs/blob/main/tokens/token-information.mdx)). |
| **Sandwich / MEV** | Searcher front-runs and back-runs a high-slippage swap | $370–500M extracted on Solana over ~16 months (2024–25). High memecoin slippage settings are the attack surface ([Helius MEV report](https://www.helius.dev/blog/solana-mev-report)). Mitigation: tight `slippageBps`, Jupiter `/execute` (MEV-protected landing), or Jito `sendTransaction` (MEV protection by default) ([Jito docs](https://github.com/jito-labs/jito-docs/blob/main/docs/source/lowlatencytxnsend.md)). At $3 trade size, the absolute sandwich loss is small, but the *percentage* is the same. |
| **Failed-transaction fees** | Failed Solana transactions still pay the base fee plus the priority fee | ~59% of non-vote transactions failed in one 2024 Blockworks Research snapshot. Bots fail 58–73% of the time (ISSTA 2025 / [arXiv 2504.18055](https://arxiv.org/html/2504.18055v1), snippet). Older data, but the mechanism holds. Each failure costs ≈ $0.004–0.04 here (§8). Jito `bundleOnly=true` gives revert protection: a failed bundle does not land, so it does not pay. |
| **Slippage on thin liquidity** | Price impact ≈ Δ/(R+Δ), plus price moves during latency | $3 into a $10k-liquidity pool (R ≈ $5k) is ~0.06% impact, so impact is *not* the main cost at $3. Latency and adverse selection are: fills arrive after faster bots move price. Jupiter's RTSE auto-slippage applies when `slippageBps` is omitted on `/order` ([order-and-execute](https://github.com/jup-ag/docs/blob/main/swap/order-and-execute.mdx)). |
| **Key/software theft** | Malicious bot repos and npm packages | Fake "solana-pumpfun-bot" GitHub repo stole keys ([Cointelegraph](https://cointelegraph.com/news/solana-trading-bot-github-malware-scam)). Use only vendor SDKs and pin versions. |

---

## 3. Chain choice for $20: **Solana** (recommendation)

| | **Solana** | **Base** (OP-stack L2) | **BNB Chain** |
|---|---|---|---|
| Base network fee | 5,000 lamports per signature (0.000005 SOL ≈ $0.0006) ([Solana fees doc](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/core/fees/index.mdx)) | Swaps about $0.01–0.20; "under $0.05" typical (snippets: [Portals](https://blog.portals.fi/cheapest-evm-chain-swap-2026/), [Spark](https://www.spark.money/tools/chain-fee-comparison)) | 0.05 gwei minimum gas, about $0.005 per transfer ([Cryptometer](https://www.cryptometer.io/news/bnb-chain-slashes-gas-fees-to-0-05-gwei-making-transactions-nearly-free/), snippet). A swap uses several times that gas, so roughly $0.01–0.03 (my estimate). |
| Priority / tip | Priority fee = ceil(CU price × CU limit / 1e6) lamports, 100% to the validator ([Solana docs](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/core/fees/index.mdx)). Typical swap 200–400k CU. Optional Jito tip ≥1,000 lamports ([Jito docs](https://github.com/jito-labs/jito-docs/blob/main/docs/source/lowlatencytxnsend.md)). | Priority fee is tiny | n/a |
| Per-token account cost | **ATA rent ≈ 0.00204 SOL** (SPL, 165 B) or **≈ 0.00207 SOL** (Token-2022 with ImmutableOwner, ~170 B; computed). Fully **refundable** by `CloseAccount` once the balance is 0 ([Solana close-account doc](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/basics/close-account.mdx)). Rent formula: (size+128) × 3,480 × 2 lamports ([Solana accounts doc](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/core/accounts/index.mdx)). | None, but an ERC-20 `approve` transaction per token unless the router uses Permit2 or permit | Same as Base |
| Meme activity | Dominant: pump.fun (with LetsBonk competing) and PumpSwap; Solana DEX volume $87.8B in Mar 2026 (snippet, [BlockEden](https://blockeden.xyz/blog/2026/04/22/meme-launchpad-2-pump-fun-letsbonk-anti-sniper-bonding-curve-professionalization/)) | Zora and Clanker; "well behind Solana" ([Coin Bureau](https://coinbureau.com/analysis/best-memecoin-launchpads)) | four.meme; episodic bursts ([The Block](https://www.theblock.co/post/367266/solana-memecoin-launchpad-war-flips-again-as-pump-takes-top-spot-amid-letsbonk-collapse)) |
| Honeypot checkability | **Enumerable flags** (§1.3) | Arbitrary contract code; needs simulation or GoPlus-style analysis | Same as Base; historically honeypot-heavy |
| US access | Self-custody plus Jupiter Swap. Jupiter geo-blocks the US **for Prediction Markets only** per its docs ([Jupiter skill](https://github.com/jup-ag/agent-skills/blob/main/skills/integrating-jupiter/SKILL.md)); no Swap-API geo-block found. pump.fun blocks the UK and sanctioned countries, not the US ([Datawallet](https://www.datawallet.com/crypto/pump-fun-restricted-countries)). | Coinbase on-ramp; free USDC withdrawals on Base (snippet, [eco.com](https://eco.com/support/en/articles/15247727-usdc-withdrawal-times-by-network)) | Binance.com is not for US persons ([The Block](https://www.theblock.co/post/85589/binance-blocking-us-users-14-day-deadline-new-email)). On-ramp is awkward. |
| Funding cost from a US exchange | Coinbase: free USDC withdrawals on Solana (snippet). Kraken: ~$1 USDC and ~0.01 SOL per withdrawal (snippet, [Kraken support](https://support.kraken.com/gr/articles/360000767986-Cryptocurrency-withdrawal-fees-and-minimums)) | Coinbase: free USDC on Base | — |

**Bridging.** Avoid it. Fund the Solana wallet *directly* from a US exchange: USDC on Solana plus a small SOL balance for fees and rent. Cross-chain bridges add fees, delay and contract risk. Their typical cost for a $20 transfer was **not verified** in this session.

**Recommendation: Solana.**
- It has the most meme flow and the deepest Jupiter routing.
- Honeypot checks are mechanical.
- Network fees are under a cent.
- The one Solana-specific cost (ATA rent, about $0.25 per token at SOL ≈ $120) is refundable if the bot always closes emptied accounts.
- Base is a reasonable second choice. It has no rent, but less meme liquidity, and EVM honeypots are harder to screen.
- Keep **~0.03 SOL** (≈ $3.60) in the wallet for fees and up to ~10 open token accounts. The rest stays in USDC.

---

## 4. Data and execution sources

Legend: **Live** = "verified live on 2026-10-06". All are **no (blocked by proxy, HTTP 403 on CONNECT)**. **Docs** shows where the facts were checked.

### 4.1 Jupiter (execution, quotes, token metadata, price): **primary execution venue**

**Base URL: `https://api.jup.ag`.** Auth is an `x-api-key` header, with keys from `https://developers.jup.ag/portal`.

**Key status (2026).** The developer platform launched on 2026-04-06; the grace period ended 2026-06-30.
- **Keyless** access on `api.jup.ag` at **0.5 RPS (30/min)** "replaces `lite-api.jup.ag`".
- `lite-api` is being "progressively deprecated" ([migration doc](https://github.com/jup-ag/docs/blob/main/portal/migration.mdx)).
- Tiers ([rate-limits doc](https://github.com/jup-ag/docs/blob/main/portal/rate-limits.mdx); [plans](https://github.com/jup-ag/docs/blob/main/portal/plans.mdx)):

  | Tier | RPS | Price |
  |---|---|---|
  | Keyless | 0.5 | free, no sign-up |
  | Free | 1 | free key; unlimited credits, rate-limited only |
  | Developer | 10 | $25/mo |
  | Launch | 50 | $100/mo |
  | Pro | 150 | $500/mo |

- The limit is a 60-second sliding window, applied per organisation. `/swap/v2/execute` has its own bucket: 20 RPS keyless, 50 free, 100 paid. Response headers are `x-ratelimit-remaining`, `x-ratelimit-current` and `x-ratelimit-reset`.
- **Conflict.** The Swap overview page says "All endpoints require an API key" ([swap/index.mdx](https://github.com/jup-ag/docs/blob/main/swap/index.mdx)), while the rate-limit, plan and migration pages document keyless access. **Get the free key**; it removes the ambiguity and doubles throughput.
- The npm SDK `@jup-ag/api` 6.0.48 (Dec 2025) still defaults to `https://lite-api.jup.ag/swap/v1` without a key and `https://api.jup.ag/swap/v1` with one. It is **stale relative to Swap v2**.

**Swap API versions:**
- **Swap v2 is current**, at `https://api.jup.ag/swap/v2` ([OpenAPI](https://github.com/jup-ag/docs/blob/main/openapi-spec/swap/v2/swap.yaml)).
- `/swap/v1/quote` and `/swap/v1/swap-instructions` (Metis v1) are **deprecated**.
- Ultra (`ultra-api.jup.ag`, `/ultra/v1/order|execute`) has been folded into v2 `/order` + `/execute`.
- The migration skill says to "remove once Jupiter decommissions v1… Review by 2026-09-01", so v1 may already be gone ([migration skill](https://github.com/jup-ag/agent-skills/blob/main/skills/jupiter-swap-migration/SKILL.md)).
- v2 supports **ExactIn only**.

**Endpoints SURVIVOR would use:**

| Use | Call | Notes |
|---|---|---|
| Quote (read-only) | `GET /swap/v2/order?inputMint=&outputMint=&amount=` **without `taker`** | Returns `outAmount`, `priceImpact` (in percentage points), `routePlan[].swapInfo.label`, `feeBps`, `platformFee`, `router`; `transaction` is null. |
| Swap (managed landing) | `GET /swap/v2/order?...&taker=<wallet>[&slippageBps=]`, then sign, then `POST /swap/v2/execute {signedTransaction, requestId}` | **Recommended.** Routers Metis, JupiterZ (RFQ), Dflow and OKX compete. Jupiter sets priority fee and slippage (RTSE) and lands via "Beam". `/execute` returns `status`, `code`, `signature`, `inputAmountResult`, `outputAmountResult`. Signed payload TTL is ~2 min, and the same `requestId` is idempotent for 2 min. Optional overrides: `priorityFeeLamports`, `jitoTipLamports`, `broadcastFeeType=maxCap|exactFee`, `excludeRouters`, `excludeDexes`. Setting any optional parameter switches `mode` from "ultra" to "manual". |
| Swap (self-built) | `GET /swap/v2/build?...&taker=`, then simulate, sign, and send via your own RPC or `POST https://api.jup.ag/tx/v1/submit` | Metis-only routing and **no Jupiter swap fee**. Returns instructions (`computeBudgetInstructions`, `setupInstructions`, `swapInstruction`, `cleanupInstruction`, `tipInstruction`, ALTs). `slippageBps` defaults to 50 or can be `rtse`. `computeUnitPricePercentile` accepts medium/high/veryHigh. The doc's example tip for `/submit` is 0.001 SOL. ([build doc](https://github.com/jup-ag/docs/blob/main/swap/build/index.mdx)) |
| Token metadata and audit | `GET /tokens/v2/search?query=<mint,...>` (≤100), `/tokens/v2/tag?query=verified`, `/tokens/v2/{toporganicscore\|toptraded\|toptrending}/{5m\|1h\|6h\|24h}`, `/tokens/v2/recent` | Fields include `audit.{mintAuthorityDisabled, freezeAuthorityDisabled, topHoldersPercentage, devBalancePercentage, devMints, devMigrations, isSus}`, `organicScore` (0–100), `isVerified`, `holderCount`, `liquidity`, `firstPool.createdAt`, `tokenProgram`, and `stats5m/1h/6h/24h` (volume, organic volume, buyers, net buyers). `audit.isSus` exists only when true. ([Tokens doc](https://github.com/jup-ag/docs/blob/main/tokens/token-information.mdx)) |
| Price | `GET /price/v3?ids=<≤50 mints>` | Returns `usdPrice`, `blockId`, `liquidity`, `priceChange24h`. Unreliable tokens are **omitted**, so fail closed. ([Price doc](https://github.com/jup-ag/docs/blob/main/price/index.mdx)) |

**Fees on `/order`** ([order-and-execute](https://github.com/jup-ag/docs/blob/main/swap/order-and-execute.mdx)):

| Pair type | Jupiter platform fee |
|---|---|
| SOL–stable | 2 bps |
| LST–stable | 5 bps |
| **Everything else** (meme tokens) | **10 bps** |
| **Tokens under 24 hours old** | **50 bps** |
| Buying Jupiter tokens; pegged pairs | 0 bps |

- **`/build` charges no Jupiter fee.** Integrator referral fees are 50–255 bps (irrelevant here).
- **Gasless.** Jupiter auto-sponsors gas and rent only when the taker holds under 0.01 SOL **and the trade is about $10 or more**, and it recoups the cost via a higher `feeBps`. **It will not fire for $3 trades.** Opt-out check: drop any quote where `signatureFeePayer != taker` ([gasless doc](https://github.com/jup-ag/docs/blob/main/swap/advanced/gasless.mdx)).

**Verdict for SURVIVOR:**
- Use `/swap/v2/order` + `/execute` for simplicity and MEV-protected landing. Cost: 10 bps.
- Consider `/swap/v2/build` + own RPC later, to save 10 bps and to bundle `CloseAccount` into the sell transaction. Tradeoff: own fee and slippage management, and Metis-only routing.

**Live: no** (blocked). **Docs: yes**, fetched from the `jup-ag/docs` main branch and the `jup-ag/agent-skills` repo on 2026-10-06.

### 4.2 DexScreener (discovery, pair stats)

**Base URL: `https://api.dexscreener.com`.** No key, free.

| Endpoint | Rate limit | Use |
|---|---|---|
| `GET /token-profiles/latest/v1` | 60/min | Newly profiled tokens (paid "enhanced info") |
| `GET /token-boosts/latest/v1` | 60/min | Paid promotion |
| `GET /token-boosts/top/v1` | 60/min | Paid promotion |
| `GET /orders/v1/{chainId}/{tokenAddress}` | 60/min | Paid orders |
| `GET /token-pairs/v1/{chainId}/{tokenAddress}` | 300/min | All pools for a token |
| `GET /tokens/v1/{chainId}/{addr1,addr2,…}` | 300/min | Up to 30 addresses (per the 2025 docs; verify) |
| `GET /latest/dex/pairs/{chainId}/{pairId}` | 300/min | Pair detail |
| `GET /latest/dex/search?q=` | 300/min | Search |

- Use `chainId = solana`. Pair objects carry `liquidity.usd`, `volume.h24/h6/h1/m5`, `txns.*.buys/sells`, `priceChange.*`, `pairCreatedAt` and `fdv`/`marketCap`.
- Paths and limits are confirmed by a third-party client's code (`nixonjoshua98/dexscreener`, [client.py](https://github.com/nixonjoshua98/dexscreener/blob/main/dexscreener/client.py)) and an MCP server README ([openSVM](https://github.com/opensvm/dexscreener-mcp-server)). The official docs page was blocked.
- Boosts and profiles are **paid promotion**. Treat them as marketing, not merit.

**Live: no** (blocked). Official docs not fetched.

### 4.3 GeckoTerminal (new pools, trending, OHLCV)

**Base URL: `https://api.geckoterminal.com/api/v2`.** No key. Free public API "currently 30 calls/min, up from 10" (snippet of [apiguide.geckoterminal.com](https://apiguide.geckoterminal.com/faq)). Higher limits require a paid CoinGecko plan.

Endpoints (paths confirmed in `geckoterminal-py` 0.3.1):
- `GET /networks/solana/new_pools`
- `GET /networks/solana/trending_pools`
- `GET /networks/solana/pools/{pool}/ohlcv/{timeframe}` with timeframe `day|hour|minute` plus an `aggregate` parameter (e.g. minute with 1/5/15; hour with 1/4/12), `before_timestamp` and `limit` (≤1000). The official parameter form is from memory of the docs, so verify it.
- `GET /simple/networks/solana/token_price/{addrs}` (≤30 addresses).

**Live: no** (blocked). Docs not fetched (blocked).

### 4.4 Birdeye

**Base URL: `https://public-api.birdeye.so`.** **Requires a key**: header `X-API-KEY` plus `x-chain: solana`.
- Free "Standard" plan: **30,000 compute units per month, 1 RPS, limited to a few endpoints**.
- Paid plans start at Starter, $99/mo, 3M CUs, 15 RPS (snippet of [docs.birdeye.so/docs/pricing](https://docs.birdeye.so/docs/pricing) and [rate-limiting](https://docs.birdeye.so/docs/rate-limiting)).
- Typical endpoints: `/defi/price`, `/defi/token_overview`, `/defi/token_security`, `/defi/v2/tokens/new_listing`, `/defi/token_trending`. Which ones the free tier allows is unverified.
- **Not needed for SURVIVOR.** 30k CUs per month is too small for continuous polling, and Jupiter plus DexScreener cover the same data.

**Live: no** (blocked).

### 4.5 RugCheck

**Base URL: `https://api.rugcheck.xyz/v1`.**
- `GET /tokens/{mint}/report/summary`: score, risks, LP-locked %.
- `GET /tokens/{mint}/report`: full report with `score`, `rugged`, `risks[] {name, level, score}`, `mintAuthority`, `freezeAuthority`, `topHolders`, `markets[].lp.lpLockedPct`, `totalMarketLiquidity`, insider-network fields.
- **Auth: none for read endpoints** (snippets from [Qodex](https://qodex.ai/blog/how-to-get-a-rugcheck-api-key-and-start-using-the-api) and MCP wrappers). An `X-API-KEY` is accepted if you have one. Write actions (votes) use wallet-signed auth.
- Rate limit: undocumented in what was found; returns 429 when exceeded.
- The `/report` path is confirmed in the community PyPI client `rugcheck` 1.0.0, whose code treats score <1000 as "Good", <5000 as "Warning" and above as "Danger". That is the client's heuristic, not RugCheck's.

**Live: no** (blocked). Official swagger (`/swagger`) blocked.

### 4.6 GoPlus Security

**Base URL: `https://api.gopluslabs.io`.**
- `GET /api/v1/solana/token_security?contract_addresses=<mint>` (labelled "Beta").
- Auth: an **optional** `Authorization: Bearer <access_token>` header. The SDK's `auth_settings` is empty, so anonymous calls are allowed. A token comes from `POST /api/v1/token` with app key and secret.
- Result fields (from SDK models): `mintable`, `freezable`, `closable`, `balance_mutable_authority`, `transfer_fee`, `transfer_fee_upgradable`, `transfer_hook`, `transfer_hook_upgradable`, `default_account_state`, `default_account_state_upgradable`, `none_transferable`, `metadata_mutable`, `holders`, `lp_holders`, `dex`, `creators`, `trusted_token`.
- Also `POST /pis/api/v1/solana/pre_execution` (transaction pre-execution or simulation).
- Free-tier rate limit: **not publicly documented** (snippet; a [GoPlus forum thread](https://docs.gopluslabs.io/discuss/68d6607e1c829d912557b2bb) asks the same question).
- Source: `goplus` 0.2.6 wheel (PyPI, 2026-08-21), `swagger_client/api/token_security_api_for_solana__beta_api.py`.

**Live: no** (blocked).

### 4.7 Helius (RPC, priority fees, transaction sending)

- **RPC URL:** `https://mainnet.helius-rpc.com/?api-key=<KEY>`. REST: `https://api-mainnet.helius-rpc.com/v0/...` (from the `helius-sdk` 3.2.0 bundle).
- **Free plan:** 1M credits per month, 10 RPC req/s, 2 req/s on DAS and Enhanced APIs; `sendTransaction` is limited to **1/s** on Free; Sender is 50/s on all plans (snippets: [helius.dev/pricing](https://helius.dev/pricing), [rate-limits](https://docs.helius.xyz/docs/billing/rate-limits.md)). The credit cost of `getPriorityFeeEstimate` was not found; standard RPC calls are generally 1 credit (unverified).
- **Priority fee API:** JSON-RPC `getPriorityFeeEstimate` with `params: [{ transaction | accountKeys, options: { priorityLevel: "Min|Low|Medium|High|VeryHigh|UnsafeMax" | includeAllPriorityFeeLevels: true } }]`. It returns micro-lamports per CU ([Helius SDK README](https://github.com/helius-labs/helius-sdk/blob/main/README.md)).
- **Sender:** `https://sender.helius-rpc.com/fast`, plus regional `http://{ewr,slc,ams,fra,lon,sg,tyo}-sender.helius-rpc.com`.
  - "Sender Max" requires a **0.001 SOL minimum tip** (≈ $0.12, **4% of a $3 trade per leg**). **Do not use it at this size.**
  - "SWQOS-only" (`swqos_only=true`) has a 0.000005 SOL minimum tip ([Helius SDK README](https://github.com/helius-labs/helius-sdk/blob/main/README.md)).
- **Use for SURVIVOR:** RPC reads (`getAccountInfo` jsonParsed for mint flags and extensions, `getTokenLargestAccounts`, `getTokenSupply`, `simulateTransaction`, `getSignatureStatuses`) and the sell simulation in §4.10. A free key is sufficient.

**Live: no** (blocked).

**Public Solana RPC.** `https://api.mainnet.solana.com` (the docs now use this name; `api.mainnet-beta.solana.com` was the older one). Limits per IP: 100 requests per 10 s, 40 per 10 s for a single method, 40 concurrent connections, 40 connections per 10 s, 100 MB per 30 s. "Not intended for production" ([Solana clusters doc](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/references/clusters.mdx)). Use it only as a fallback. **Live: no** (blocked).

### 4.8 Jito (block engine)

- **Endpoints:** `https://mainnet.block-engine.jito.wtf/api/v1/transactions` (`sendTransaction`, MEV-protected; `?bundleOnly=true` gives revert protection) and `/api/v1/bundles` (`sendBundle` with ≤5 transactions, `getBundleStatuses`, `getInflightBundleStatuses`, `getTipAccounts`). Regional hosts include `ny.` and `slc.mainnet.block-engine.jito.wtf` for the US.
- **Tip data:** `GET https://bundles.jito.wtf/api/v1/bundles/tip_floor` and `wss://bundles.jito.wtf/api/v1/bundles/tip_stream`.
- **Minimum tip:** 1,000 lamports. Pay it to one of 8 tip accounts, chosen at random, and do not reference it through an address lookup table. With `sendTransaction`, Jito suggests splitting priority fee and tip 70/30.
- **Rate limit:** 1 request/s per IP per region; no auth key needed for default sends.
- The doc's example `tip_floor` response shows a median landed tip of 1e-5 SOL and a 95th percentile of 0.00145 SOL. That is a historical example, not a live value ([Jito docs](https://github.com/jito-labs/jito-docs/blob/main/docs/source/lowlatencytxnsend.md)).
- **Usefulness at $20: marginal.** Jupiter `/execute` already handles landing and MEV protection. Jito is worth it only if SURVIVOR self-sends `/build` transactions: `bundleOnly=true` means failed sells do not pay fees, and the 1,000-lamport minimum is about $0.0001.

**Live: no** (blocked).

### 4.9 pump.fun data

- **No official public REST API.** `https://frontend-api-v3.pump.fun` (e.g. `GET /coins/latest`) is the website's backend. It is reverse-engineered, many endpoints require a JWT, and it changes without notice (snippets: [BankkRoll/pumpfun-apis](https://github.com/BankkRoll/pumpfun-apis)). **Unstable; do not depend on it.**
- **Official:** on-chain program documentation and IDLs ([pump-fun/pump-public-docs](https://github.com/pump-fun/pump-public-docs)), plus `@pump-fun/pump-sdk` and `@pump-fun/pump-swap-sdk` (npm).
- **Third-party:** PumpPortal, with a data WebSocket at `wss://pumpportal.fun/api/data` and a trading API. Its fees and terms were not verified.
- **For SURVIVOR:** get new and graduated pools from GeckoTerminal `new_pools`, DexScreener and Jupiter `/tokens/v2/recent`, rather than pump.fun endpoints. Jupiter routes pump.fun curves and PumpSwap pools directly.

**Live: no** (blocked).

### 4.10 Simulating a sell before buying (honeypot check)

Run these checks, cheapest first:

1. **Static flags.** Call RPC `getAccountInfo(mint, {encoding:"jsonParsed"})`.
   - Check that `mintAuthority` and `freezeAuthority` are null.
   - Check the owner program (Token vs Token-2022).
   - Check that the `extensions[]` list is within the allowlist from §1.3.
   - Cross-check with Jupiter `audit.*` and RugCheck or GoPlus. Any disagreement means reject.
2. **Reverse-route quote.** Call `GET /swap/v2/order?inputMint=<TOKEN>&outputMint=<USDC>&amount=<expected tokens from the buy quote>` with no `taker`.
   - Require a route to exist.
   - Require `priceImpact` > −1 (that is, less than 1% impact).
   - Require round-trip retention, `sell.outAmount / buy.inAmount`, of at least 1 − (expected fees + 1%).
   - This catches missing sell liquidity and transfer-fee taxes.
3. **Simulated sell from a real holder.** Pick a current non-pool holder from `getTokenLargestAccounts`. Fetch `GET /swap/v2/build?...&taker=<thatHolder>` for a small sell. Assemble the transaction and call RPC `simulateTransaction` with `sigVerify:false, replaceRecentBlockhash:true`. Signatures are not needed when `sigVerify` is off.
   - A failure with a transfer-hook or program error means a honeypot.
   - This tests the *current* rules. It **cannot** detect a future freeze, which is why step 1 requires freeze authority = null.
   - This technique follows Solana RPC semantics but was **not tested here**.
4. **After buying,** re-quote the sell immediately. If it is no longer routable, alert and stop trading that mint.

### 4.11 First-run probe checklist (run from the user's PC; record results here)

```
curl -sS -D- "https://api.jup.ag/swap/v2/order?inputMint=So11111111111111111111111111111111111111112&outputMint=EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v&amount=10000000"            # keyless, expect 200 + x-ratelimit-* headers
curl -sS -D- -H "x-api-key: $JUP_KEY" "https://api.jup.ag/swap/v2/order?...same..."   # free key
curl -sS -o NUL -w "%{http_code}" "https://lite-api.jup.ag/swap/v1/quote?...same..."   # expect deprecated/404/redirect
curl -sS "https://api.jup.ag/price/v3?ids=So11111111111111111111111111111111111111112"
curl -sS "https://api.dexscreener.com/token-pairs/v1/solana/<MINT>"
curl -sS "https://api.geckoterminal.com/api/v2/networks/solana/new_pools"
curl -sS "https://api.rugcheck.xyz/v1/tokens/<MINT>/report/summary"
curl -sS "https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses=<MINT>"
curl -sS https://bundles.jito.wtf/api/v1/bundles/tip_floor
curl -sS -X POST "https://mainnet.helius-rpc.com/?api-key=$HELIUS_KEY" -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getPriorityFeeEstimate\",\"params\":[{\"accountKeys\":[\"JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4\"],\"options\":{\"includeAllPriorityFeeLevels\":true}}]}"
```

Python libraries current as of today: `solana` 0.41.0 (requires Python ≥3.11, released 2026-10-03) and `solders` 0.29.0 (PyPI).

---

## 5. Evidence on retail meme-coin success rates

| Finding | Source | Caveat |
|---|---|---|
| Only **6.25% of 304,161** active Solana memecoin traders were profitable over 90 days. Median loss $120. Of winners, 88% made under $100; only 25 wallets made over $10k; ~$1.26B total losses | [Mitrade, 2026-08-19](https://www.mitrade.com/insights/news/live-news/article-3-2012817-20260819); [Cointribune](https://www.cointribune.com/en/crypto-solana-memecoins-trap-nearly-94-of-traders/) (snippets) | Underlying data provider not confirmed. Newest datapoint found. |
| Profitable pump.fun wallets: 30.1% (Jun 2025), then 56.8% (Feb 2026), 70.0% (Mar) and **73.3% (Apr 2026)**. 65% of winners made only $1–500; monthly actives fell 5.2M to 1.8M | CoinGecko via [Yahoo](https://finance.yahoo.com/markets/crypto/articles/73-pump-fun-traders-profit-094850577.html) | **Survivorship**: losers left. It counts wallets, not dollars. It conflicts in tone with the 6.25% figure (different universe and window). |
| 0.4% of pump.fun traders made over $10k (~Jan 2025) | [Decrypt](https://decrypt.co/300403/pump-fun-traders-millionaires) | Headline only. |
| 98.6% of pump.fun tokens tied to rug or P&D; <2% (0.63% in one sample) graduate | Solidus ([CoinDesk](https://www.coindesk.com/business/2025/05/07/98-of-tokens-on-pump-fun-have-been-rug-pulls-or-an-act-of-fraud-new-report-says)); [arXiv 2602.14860](https://arxiv.org/abs/2602.14860) | pump.fun disputed Solidus. |
| 82.89% of high-return meme tokens show artificial growth; 17k+ victim addresses lost over $9.3M | [arXiv 2507.01963](https://arxiv.org/html/2507.01963v2) (USENIX Sec '26) | Multi-chain sample of 34,988 tokens. |
| ~3,505 user-funded LLM memecoin vaults: "Neither fleet shows a directional edge" | [arXiv 2609.05663](https://arxiv.org/abs/2609.05663) | Closest analogue to SURVIVOR. |
| 988,905 wallets down $3.81B on TRUMP | [The Block](https://www.theblock.co/amp/post/407170/nearly-1-million-wallets-are-down-3-81-billion-on-trumps-memecoin-report) | Even a "blue-chip" meme. |
| Copy-trading: followers profitable 48.5% vs leaders 97% on own PnL | [YieldFund](https://yieldfund.com/is-copy-trading-profitable-a-90-day-multi-exchange-study) | Low-quality source. |

**Honest summary.** The base rate for a retail meme trader over any recent 90-day window is **most lose, the median loses**, and the winners mostly win small. No audited data shows that an automated retail meme bot is net profitable.

---

## 6. Strategy families

Sizing assumption: the 15% cap means about $3 per trade. Costs come from §8. "A" means an established token (about 1.8% round trip); "B" means a token under 24 hours old (about 8–9%).

### 6.1 Momentum / breakout on established meme tokens
- **Mechanism:** buy when price breaks an N-bar high (or a fast moving average crosses above a slow one) on 1h or 4h bars. Exit on a trailing stop or the opposite signal.
- **Evidence:** time-series momentum is the best-supported crypto anomaly. Concretum reports net Sharpe >1.5 on a top-20 coin rotation ([SSRN 5209907](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907)), and Han, Kang & Ryu report that TSMOM survives realistic costs better than cross-sectional momentum ([SSRN 4675565](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565)). **No study on Solana meme tokens specifically.** Crashes and fat tails dominate ([Springer FMPM 2025](https://link.springer.com/article/10.1007/s11408-025-00474-9)).
- **Cost sensitivity:** scenario A, about 1.8% per round trip. That is workable only with low turnover (a few trades per week). Breakouts on memes are often wash-traded (§2).
- **Data:** GeckoTerminal OHLCV (30/min is plenty for about 10 pools on 1h bars), Jupiter Price v3, DexScreener liquidity.
- **Risk:** false breakouts and overnight −50% gaps. Stops slip on thin books.

### 6.2 New-listing entries behind strict filters
- **Mechanism:** buy recently graduated or new pools that pass every §7 filter, aiming to catch early survivors.
- **Evidence:** strongly negative. Graduation runs 0.63–2%, 98.6% of tokens are rug or P&D, professional sniper cohorts take the first fills ([arXiv 2607.02795](https://arxiv.org/abs/2607.02795)), and wash trading *raises* graduation odds.
- **Cost sensitivity:** worst case, scenario B at about 8–9% per round trip: Jupiter's 50 bps new-token fee, high curve and pool fees, higher priority fees and slippage. A 24-hour age filter removes the 50 bps fee but also most of the "early" premise.
- **Data:** GeckoTerminal `new_pools`, Jupiter `/tokens/v2/recent`, RugCheck, GoPlus, RPC.
- **Risk:** highest. Rug and dev dumps happen within minutes. **Paper-trade only.**

### 6.3 Post-dip mean reversion on established tokens
- **Mechanism:** buy an established token (age over 30 days, liquidity over $500k) after a sharp drop, e.g. −25% in 24 hours or RSI(14, 1h) below 20. Take profit at +8–15% or after a time stop.
- **Evidence:** weak and indirect. Momentum papers note that "losers often rebound", which hurts short legs ([SSRN 4675565](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4675565)). No rigorous standalone crypto mean-reversion study was found ([notes](../research_notes/Crypto%20trading%20bot%20strategy%20plan/strategy_evidence.md)).
- **Cost sensitivity:** scenario A. A bounce target of 8% or more comfortably clears the ~1.8% cost.
- **Data:** OHLCV, liquidity trend (a liquidity drop alongside a price drop means a rug, not a dip), holder trend from Jupiter `stats1h.numNetBuyers`.
- **Risk:** "catching a knife". Many dips are the start of a terminal decline. Require that liquidity has *not* fallen more than 20%.

### 6.4 Volume and holder-growth spikes
- **Mechanism:** enter when 1h volume is at least 3× its 24h average, net buyers are positive, and organic volume share is high, on tokens aged 3–90 days.
- **Evidence:** volume is the most manipulated metric (§2: 41–93% non-organic claims; 82.89% artificial growth among winners). Jupiter's `organicScore` and `buyOrganicVolume` exist to correct for this, but their methodology is proprietary and unvalidated.
- **Cost sensitivity:** A to B depending on token age.
- **Data:** Jupiter Tokens v2 `stats*`, DexScreener `txns` and `volume`.
- **Risk:** being exit liquidity for wash-pumped tokens.

### 6.5 Smart-money wallet tracking
- **Mechanism:** mirror buys from wallets with a good track record.
- **Evidence:** a structural "imitation penalty" (the copier always fills at a worse price), and KOLs use copy-traders as exit liquidity ([arXiv 2601.08641](https://arxiv.org/html/2601.08641v2)). Sniper cohorts look skilled only through selection ([arXiv 2607.02795](https://arxiv.org/abs/2607.02795)). Only 12% of top traders keep their rank for 6 months ([KuCoin](https://www.kucoin.com/blog/is-crypto-copytrading-profitable-in-2026)).
- **Cost sensitivity:** usually scenario B, since smart wallets buy new tokens.
- **Data:** an RPC or Helius webhooks or WebSocket subscription on wallet addresses; wallet-label datasets are paid.
- **Risk:** high. Easily farmed and latency-dominated.

---

## 7. Suggested screening filters (**starting points to tune, not validated**)

| Filter | Start value | Reasoning |
|---|---|---|
| Mint authority / freeze authority | **null / null** | Hard rule (§1.3). Freeze authority is undetectable future honeypot risk. |
| Token-2022 extensions | Allowlist only `MetadataPointer`, `TokenMetadata` (+ `ImmutableOwner` on accounts) | Rejects transfer fee, hook, permanent delegate, non-transferable, default-frozen and pausable. |
| Max transfer tax | **0%** | Solana has no legitimate need for a tax. Any `TransferFeeConfig` is a reject. |
| Min pool liquidity (USD, both sides) | **$50k** (6.3: **$500k**) | Price impact on $3 is negligible either way. The bar exists because rug probability falls with liquidity: fewer than ~100k of 7M tokens ever held >$1k, and the median rug was $2.8k ([Solidus](https://www.coindesk.com/business/2025/05/07/98-of-tokens-on-pump-fun-have-been-rug-pulls-or-an-act-of-fraud-new-report-says)). It also means the bot is not a large share of flow. |
| Min 24h volume | **$100k**, and **volume/liquidity ≤ 20×** | Needs real trading. A very high turnover ratio suggests wash trading (heuristic). |
| Min token age (`firstPool.createdAt` / `pairCreatedAt`) | **≥24 h** (6.1/6.3: **≥30 days**) | Avoids Jupiter's 50 bps new-token fee and the first-day rug window. |
| Max top-10 holders % (excluding pool, curve and burn accounts) | **≤30%**; max single non-pool holder **≤8%**; dev balance **≤3%** | Bundling hides insiders, so be stricter than the common "≤50%". |
| LP burned/locked | **≥95%** (pump.fun graduates: protocol-burned) | Prevents liquidity pulls. |
| RugCheck | No `danger`-level risks; `rugged == false` | Treat RugCheck's score scale as opaque. Use risk levels. |
| Jupiter audit | `audit.isSus !== true`; `organicScoreLabel` ∈ {medium, high} (start: score ≥ 40) | Vendor heuristic; fail closed on missing fields. |
| Holder count | **≥ 500** | Weak, since it is easily faked. |
| Market cap | **$250k–$50M** | Below that is mostly launches; above it moves too slowly for meme-style targets. Tune per strategy. |
| Round-trip quote check | Buy quote and immediate reverse quote at **2×** position size; loss ≤ expected fees + **1%** | Catches hidden taxes and one-sided liquidity (§4.10). |
| Max `priceImpact` | **≤ 1%** at position size | Sanity check. At $3 this should be ~0. |
| Slippage setting | 100 bps (A) / 300 bps (B), or omit for RTSE | Tight slippage limits sandwich loss but raises the failure rate. |

---

## 8. Cost model: a $3 round trip on Solana via Jupiter

**Assumptions:**
- SOL = **$120** (search snippet for Oct 5–6, 2026, e.g. [MetaMask price page](https://metamask.io/price/solana); not verified live).
- Funding is from USDC, so a USDC→SOL hop is involved because PumpSwap pools are SOL-quoted.
- Route via `/swap/v2/order` + `/execute`, with the sell exiting back to USDC.
- One leg ≈ 300k CU.

| Line item | **A: established token** (>24h, liquidity $200k) | **B: fresh token** (<24h, liquidity $15k) | Source / basis |
|---|---|---|---|
| Jupiter platform fee | 0.10% × 2 = 0.20% | 0.50% × 2 = 1.00% | Jupiter fee table |
| Pool/LP fees (meme hop) | ~0.30% × 2 = 0.60% (PumpSwap 0.25% + low creator tier) | ~1.25% × 2 = 2.50% (curve-like or high creator tier; assumed upper bound) | pump.fun docs and notes; tier is dynamic |
| USDC↔SOL hop LP fee | ~0.02% × 2 = 0.04% | 0.04% | Assumption |
| Price impact Δ/R | $3/$100k ≈ 0.003% × 2 ≈ 0.01% | $3/$7.5k = 0.04% × 2 = 0.08% | CPMM math |
| Adverse fill / latency slippage (assumption) | 0.3% × 2 = 0.60% | 1.0% × 2 = 2.00% | Judgment; memes move fast |
| Network base fee | 5,000 lamports × 2 | same | Solana docs |
| Priority fee | 30k lamports × 2 (100k µlamports/CU × 300k CU) | 300k lamports × 2 (1M µlamports/CU) | Assumption; Jupiter sets it automatically |
| Close-ATA transaction | ~6k lamports | ~6k lamports | Base fee plus a small priority fee |
| **SOL-denominated total** | ≈ 0.000076 SOL ≈ **$0.009 (0.30%)** | ≈ 0.000616 SOL ≈ **$0.074 (2.5%)** | |
| **Percentage-denominated total** | ≈ **1.45%** ($0.044) | ≈ **5.6%** ($0.169) | |
| **Round-trip cost** | **≈ 1.75% ($0.053)** | **≈ 8.1% ($0.24)** | |
| **Break-even move** c/(1−c) | **≈ +1.8%** | **≈ +8.8%** | |
| ATA rent (Token-2022 ~0.00207 SOL) | **$0.25 = 8.3% of $3**, locked while held and **refunded on close** | same | Solana rent formula |
| If the ATA is *not* closed (dust left or bug) | Cost rises to **≈ 10.1%**, break-even ≈ +11% | **≈ 16.4%**, break-even ≈ +20% | |
| Optional Jito/Sender tip 0.001 SOL per leg | +$0.24 = +8% | +8% | Helius Sender Max minimum |
| Each failed attempt | +$0.004 (A) / +$0.036 (B) | | Fees are charged on failure |

**Implications:**
- At about $0.05 per round trip (A), 100 trades cost about $5, or **25% of the $20**. At about $0.24 (B), 100 trades cost **more than the whole account**.
- **Close every emptied token account.** Sell the *entire* raw balance; if dust remains, burn it, then `CloseAccount`. Rent is the largest single fixed cost at $3 size.
- **Never pay 0.001 SOL tips at this size.**
- Jupiter's gasless mode does not apply below about $10 per trade.
- Open positions tie up about $0.25 of rent each. Three open positions lock about $0.75, roughly 4% of equity.

---

## 9. Ranked shortlist to test, and the expected outcome

Order of work: **paper-trade first.** Run quotes-only mode against live data for at least 2 weeks, logging hypothetical fills from `/order` quotes plus the §8 costs. Then go live with $3 positions.

> **Build decision (owner's rule overrides this recommendation):** SURVIVOR trades live from day one with small positions. Shadow trading runs alongside purely as extra data and never gates live trading. Strategies ranked "paper only" or "do not run live" below start with a live allocation of zero, and the learner may only raise it from evidence.

1. **Momentum/breakout on established Solana meme tokens** (6.1). It has the best evidence family (TSMOM), the lowest cost (scenario A, ~1.8%), and data that is free and reliable. Use low turnover: at most about 5 round trips per week.
2. **Post-dip mean reversion on established tokens** (6.3). Same cost profile, and targets of 8% or more clear costs easily. The evidence is weak, so run it as a parallel paper strategy and keep whichever survives.
3. **Volume and holder-growth spikes on mid-age tokens** (6.4). It is testable with Jupiter's organic-volume fields, but wash-trading risk is high. Paper only until 1–2 show positive expectancy net of costs over 100 or more signals.
4. **New-listing entries behind strict filters** (6.2). Cost of about 8–9% and a 98%+ adverse base rate. Paper only, mainly to validate the safety filters.
5. **Smart-money wallet tracking** (6.5). Structurally disadvantaged and actively farmed. Do not run live.

**Explicit expectation.** Given costs of 1.8–9% per round trip, a population where about 94% of active Solana meme traders lost money in the latest 90-day window found, and no evidence of a durable retail edge, **the most likely outcome is that SURVIVOR loses money, with a meaningful probability of losing most of the $20.** A "profitable" stretch over a few dozen trades is statistically indistinguishable from luck. The realistic value of the project is a tested, safe pipeline: honeypot filters, rent reclamation, cost accounting and tax logs.

US tax note (from the earlier notes): every swap is a taxable disposal, and DEX trades produce no 1099. Log the timestamp, amounts, fees and USD value for every fill ([notes](../research_notes/Crypto%20trading%20bot%20strategy%20plan/us_legal_tax.md)).

---

## 10. Sources (all accessed 2026-10-06)

**Primary docs fetched from raw GitHub or package registries (read in full or in relevant part):**
- Jupiter docs repo: [portal/rate-limits.mdx](https://github.com/jup-ag/docs/blob/main/portal/rate-limits.mdx), [portal/plans.mdx](https://github.com/jup-ag/docs/blob/main/portal/plans.mdx), [portal/migration.mdx](https://github.com/jup-ag/docs/blob/main/portal/migration.mdx), [portal/setup.mdx](https://github.com/jup-ag/docs/blob/main/portal/setup.mdx), [swap/index.mdx](https://github.com/jup-ag/docs/blob/main/swap/index.mdx), [swap/order-and-execute.mdx](https://github.com/jup-ag/docs/blob/main/swap/order-and-execute.mdx), [swap/build/index.mdx](https://github.com/jup-ag/docs/blob/main/swap/build/index.mdx), [swap/advanced/gasless.mdx](https://github.com/jup-ag/docs/blob/main/swap/advanced/gasless.mdx), [tokens/token-information.mdx](https://github.com/jup-ag/docs/blob/main/tokens/token-information.mdx), [price/index.mdx](https://github.com/jup-ag/docs/blob/main/price/index.mdx), [openapi-spec/swap/v2/swap.yaml](https://github.com/jup-ag/docs/blob/main/openapi-spec/swap/v2/swap.yaml), [llms.txt](https://github.com/jup-ag/docs/blob/main/llms.txt)
- Jupiter agent skills: [integrating-jupiter/SKILL.md](https://github.com/jup-ag/agent-skills/blob/main/skills/integrating-jupiter/SKILL.md), [examples/swap.md](https://github.com/jup-ag/agent-skills/blob/main/skills/integrating-jupiter/examples/swap.md), [jupiter-swap-migration/SKILL.md](https://github.com/jup-ag/agent-skills/blob/main/skills/jupiter-swap-migration/SKILL.md)
- npm `@jup-ag/api` 6.0.48 ([npm](https://www.npmjs.com/package/@jup-ag/api)); npm `helius-sdk` 3.2.0 ([npm](https://www.npmjs.com/package/helius-sdk)); [Helius SDK README](https://github.com/helius-labs/helius-sdk/blob/main/README.md)
- pump.fun: [README](https://github.com/pump-fun/pump-public-docs/blob/main/README.md), [PUMP_PROGRAM_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/PUMP_PROGRAM_README.md), [PUMP_SWAP_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/PUMP_SWAP_README.md), [FEE_PROGRAM_README](https://github.com/pump-fun/pump-public-docs/blob/main/docs/FEE_PROGRAM_README.md), [FAQ](https://github.com/pump-fun/pump-public-docs/blob/main/docs/FAQ.md), [COIN_CREATION](https://github.com/pump-fun/pump-public-docs/blob/main/docs/instructions/COIN_CREATION.md)
- Solana docs (solana-foundation/solana-com): [clusters](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/references/clusters.mdx), [fees](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/core/fees/index.mdx), [accounts](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/core/accounts/index.mdx), [close-account](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/basics/close-account.mdx), [transfer-hook](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/transfer-hook.mdx), [permanent-delegate](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/permanent-delegate.mdx), [transfer-fees](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/transfer-fees.mdx), [extensions index](https://github.com/solana-foundation/solana-com/blob/main/apps/docs/content/docs/en/tokens/extensions/index.mdx)
- Jito: [lowlatencytxnsend.md](https://github.com/jito-labs/jito-docs/blob/main/docs/source/lowlatencytxnsend.md)
- GoPlus: PyPI [`goplus` 0.2.6](https://pypi.org/project/goplus/) (wheel inspected); [goplus-mcp README](https://github.com/GoPlusSecurity/goplus-mcp/blob/main/README.md)
- GeckoTerminal: PyPI [`geckoterminal-py` 0.3.1](https://pypi.org/project/geckoterminal-py/) (wheel inspected)
- DexScreener (third-party): [nixonjoshua98/dexscreener client.py](https://github.com/nixonjoshua98/dexscreener/blob/main/dexscreener/client.py); [openSVM dexscreener-mcp-server](https://github.com/opensvm/dexscreener-mcp-server)
- RugCheck (third-party): PyPI [`rugcheck` 1.0.0](https://pypi.org/project/rugcheck/) (wheel inspected)
- PyPI [`solana`](https://pypi.org/project/solana/), [`solders`](https://pypi.org/project/solders/)

**Search-engine summaries (snippets; pages blocked or not fetched):**
- Jupiter: [developers.jup.ag migration](https://developers.jup.ag/docs/portal/migration); [JupDevRel on X: Lite API deprecation](https://x.com/JupDevRel/status/1995521411767791886); [Ultra get-started](https://developers.jup.ag/docs/ultra/get-started.md)
- GeckoTerminal: [FAQ](https://apiguide.geckoterminal.com/faq); [llms-full](https://apiguide.geckoterminal.com/llms-full.txt)
- Birdeye: [pricing](https://docs.birdeye.so/docs/pricing); [rate-limiting](https://docs.birdeye.so/docs/rate-limiting)
- Helius: [pricing](https://helius.dev/pricing); [rate limits](https://docs.helius.xyz/docs/billing/rate-limits.md); [priority fee API](https://www.helius.dev/docs/priority-fee-api.md)
- RugCheck: [Qodex guide](https://qodex.ai/blog/how-to-get-a-rugcheck-api-key-and-start-using-the-api); [goat-mcp RugCheck api.ts](https://glama.ai/mcp/servers/@cryptoleek-team/goat-mcp/blob/d2e796192eac82c5c78f93be345183d7007d034f/rugcheck/src/api.ts)
- GoPlus: [forum thread on rate limits](https://docs.gopluslabs.io/discuss/68d6607e1c829d912557b2bb)
- pump.fun data: [BankkRoll/pumpfun-apis](https://github.com/BankkRoll/pumpfun-apis); [PumpPortal (QuickNode guide)](https://www.quicknode.com/builders-guide/tools/pumpportal-by-pumpportal-team)
- Chain costs: [Portals cheapest EVM chain 2026](https://blog.portals.fi/cheapest-evm-chain-swap-2026/); [Spark chain fee comparison](https://www.spark.money/tools/chain-fee-comparison); [Cryptometer BNB 0.05 gwei](https://www.cryptometer.io/news/bnb-chain-slashes-gas-fees-to-0-05-gwei-making-transactions-nearly-free/); [eco.com USDC withdrawal networks](https://eco.com/support/en/articles/15247727-usdc-withdrawal-times-by-network); [Kraken withdrawal fees](https://support.kraken.com/gr/articles/360000767986-Cryptocurrency-withdrawal-fees-and-minimums)
- SOL price: [MetaMask SOL price](https://metamask.io/price/solana); [Investing.com SOL history](https://www.investing.com/crypto/solana/historical-data)
- Priority fees: [rpcfast fees explainer](https://rpcfast.com/blog/solana-transaction-fees-explained); [Chainstack: Jupiter priority fees](https://docs.chainstack.com/docs/solana-priority-fees-for-a-jupiter-in-python)
- Failed transactions: [Blockworks Lightspeed](https://blockworks.com/news/lightspeed-newsletter-dropped-solana-transactions); [arXiv 2504.18055](https://arxiv.org/html/2504.18055v1); [The Defiant](https://thedefiant.io/news/defi/bots-spam-better-than-humans-leading-to-transaction-failures-on-solana)
- Honeypots: [DEXTools freeze/update authority scams](https://www.dextools.io/tutorials/freeze-authority-and-update-authority-scams); [dev.to freeze authority honeypot](https://dev.to/mrvlyouknowwho/freeze-authority-is-the-solana-honeypot-how-to-check-any-spl-token-in-10-seconds-free-no-wallet-15h4)
- Wash trading and launchpads: [Bitquery: Solana volume numbers](https://bitquery.io/blog/solana-volume-numbers-are-a-lie); [The Block launchpad war](https://www.theblock.co/post/367266/solana-memecoin-launchpad-war-flips-again-as-pump-takes-top-spot-amid-letsbonk-collapse); [BlockEden meme launchpad 2.0](https://blockeden.xyz/blog/2026/04/22/meme-launchpad-2-pump-fun-letsbonk-anti-sniper-bonding-curve-professionalization/)
- Retail outcomes: [Mitrade 6% of Solana meme traders](https://www.mitrade.com/insights/news/live-news/article-3-2012817-20260819); [Cointribune 94% lose](https://www.cointribune.com/en/crypto-solana-memecoins-trap-nearly-94-of-traders/); [The Block TRUMP losses](https://www.theblock.co/amp/post/407170/nearly-1-million-wallets-are-down-3-81-billion-on-trumps-memecoin-report)
- Academic: [arXiv 2602.14860 Pump.fun success prediction](https://arxiv.org/abs/2602.14860); [arXiv 2512.11850 Solana memecoin phenomenon](https://arxiv.org/html/2512.11850v3)

**Re-used from the earlier notes** (original URLs are cited inline above): Solidus Labs/CoinDesk, CoinGecko/Yahoo, Decrypt, arXiv 2507.01963, 2601.08641, 2607.02795, 2609.10246, 2602.13480, 2609.05663, Helius MEV report, soltokencreator.io pump.fun fees, Datawallet pump.fun restrictions, Coin Bureau launchpads, Cointelegraph GitHub malware, SSRN 5209907, SSRN 4675565, Springer FMPM 2025, KuCoin and YieldFund copy-trading, The Block (Binance US), Mobula bundler docs. Local copies: `research_notes/Crypto trading bot strategy plan/{meme_coins,strategy_evidence,tooling_risk_security,us_legal_tax}.md` and `reports/Crypto trading bot strategy plan.md`.

**Blocked, not verified (egress proxy 403):** every API host listed in §0, plus `dev.jup.ag`, `developers.jup.ag`, `docs.dexscreener.com`, `apiguide.geckoterminal.com`, `docs.birdeye.so`, `docs.coingecko.com`, `www.helius.dev`, `docs.helius.xyz`, `tessl.io`, `skills.cat`, `pluang.com`, `cdn.jsdelivr.net`, and the `github.com` web UI. Raw GitHub, PyPI and npm were reachable.
