# US Legal and Tax Considerations for an Individual Running a Personal Crypto Trading Bot (status as of October 2026)

> Informational research notes, not legal or tax advice. Research date: 2026-10-06. Several primary sources (irs.gov, orrick.com, sovos.com, accountingtoday.com, chainwisecpa.com) were blocked by the research network proxy, so some IRS facts below are taken from search-result summaries of those pages and from secondary sources (law firms, Big 4, tax software blogs) rather than read in full. Any claim drawn from the researcher's background knowledge without a source fetched in this session is listed under "Gaps" and marked as unverified.

## 1. Tax treatment of bot trading (property, short vs long term, every trade taxable, many lots, cost-basis methods, Rev. Proc. 2024-28)

### Takeaway
For federal tax purposes crypto is property, so every bot sale or crypto-to-crypto swap is a capital-gains event. Almost all bot profits will be short-term, taxed at ordinary rates of 10%–37%. Since 1 January 2025, cost basis must be tracked separately for each wallet or account (Rev. Proc. 2024-28). Temporary IRS relief (Notice 2025-7, extended by Notice 2026-20 through 31 December 2026) lets a taxpayer pick which lots are sold by recording that choice in their own books, including as a standing order.

### Cited Findings
- The IRS treats crypto as property, not a security. That is why stock-specific rules such as the Section 1091 wash-sale rule do not reach it. — [Countonsheep: Crypto Wash Sale Rule 2026](https://countonsheep.com/blog/crypto-wash-sale-rule-2026); [Taxstra](https://taxstra.com/crypto-wash-sale-rules/)
- The property treatment comes from IRS Notice 2014-21. — [CoinTracker: write off unlimited losses](https://www.cointracker.io/blog/write-off-unlimited-losses)
- Crypto held one year or less produces short-term gain taxed at ordinary income rates (10%–37%). Crypto held more than one year qualifies for long-term rates of 0%, 15% or 20%. — [SoFi: How crypto is taxed 2026](https://www.sofi.com/learn/content/how-is-crypto-taxes/); [TokenTax](https://tokentax.co/blog/how-is-crypto-taxed)
- 2026 long-term capital-gains thresholds:
  - The 0% rate applies up to $49,450 (single) or $98,900 (married filing jointly).
  - The 15% rate applies up to $545,500 (single) or $613,700 (joint).
  - Above those amounts the rate is 20%.
  - The 3.8% Net Investment Income Tax applies above $200,000 MAGI (single) or $250,000 (joint). Those NIIT thresholds are not inflation-indexed.
  — [Kiplinger: 2026 capital gains thresholds](https://www.kiplinger.com/taxes/irs-updates-capital-gains-tax-thresholds); [ustax.tools](https://ustax.tools/capital-gains-tax-rates-2026/)
- Rev. Proc. 2024-28 ended the "universal" method of tracking basis across all holdings and moved taxpayers to the "wallet-by-wallet" method. Each wallet or exchange account is now an independent ledger. — [Koinly: Rev. Proc. 2024-28](https://koinly.io/blog/irs-revenue-procedure-crypto-depot/); [Awaken Tax](https://awaken.tax/media/article/irs-crypto-regulations-rev-proc-2024-28-per-wallet-accounting)
- To use the Rev. Proc. 2024-28 safe harbor, taxpayers had to allocate their unused basis to specific wallets and accounts as of 1 January 2025.
  - The allocation could use a specific-unit method or a global allocation method.
  - It was required to be "reasonable": each wallet must hold the same number and type of units as the basis assigned to it.
  - The stated purpose is to make brokers' Forms 1099-DA match taxpayers' Forms 8949 once brokers start reporting basis for 2026 transactions.
  — [The Tax Adviser (AICPA), Oct 2024](https://www.thetaxadviser.com/news/2024/oct/universal-accounting-for-digital-assets-concludes-but-safe-harbor-available/); [bitcoin.tax](https://bitcoin.tax/blog/irs-rev-proc-2024-28-preparing-2025-crypto-reporting-requirements)
- Notice 2025-7 gave temporary relief for calendar year 2025. Taxpayers holding crypto with a custodial broker could make an "adequate identification" of which units were sold in either of two ways:
  - noting the specific units in their own books and records no later than the time of sale, or
  - recording a standing order in their own books and records.
  Either way they did not have to communicate the choice to the broker. This is the mechanism that allows specific identification, such as HIFO, instead of the FIFO default. — [Journal of Accountancy, May 2025](https://www.journalofaccountancy.com/issues/2025/may/temporary-relief-for-adequate-identification-of-digital-assets/); [Freeman Law](https://freemanlaw.com/irs-provides-temporary-relief-on-adequate-identification-rules-for-sales-of-digital-assets/); [Deloitte alert (PDF)](https://www.deloitte.com/content/dam/assets-zone3/us/en/docs/services/2025/bda-tax-alert-notice02025-7-jan-10-2025.pdf)
- Notice 2026-20 (March 2026) extends that relief one more year, so the relief period now runs 1 January 2025 through 31 December 2026.
  - Taxpayers may use their own records to decide which lots are treated as sold, even when that differs from what the broker reports on Form 1099-DA.
  - The extension was granted because many brokers are still building systems to accept specific-identification instructions.
  - The relief remains subject to Rev. Proc. 2024-28 and does not change brokers' reporting obligations.
  — [KPMG TaxNewsFlash, Mar 2026](https://kpmg.com/us/en/taxnewsflash/news/2026/03/tnf-notice-2026-20-one-year-extension-of-temporary-relief-for-making-adequate-identification-of-units-of-digital-assets-held-in-brokers-custody.html); [Winston & Strawn](https://www.winston.com/en/blogs-and-podcasts/tax-impacts/irs-extends-digital-asset-reporting-relief-through-2026-under-notice-2026-20); [Greenback Tax](https://www.greenbacktaxservices.com/blog/digital-asset-identification-relief-extended/)

### Inferences
- A bot that makes hundreds or thousands of round trips a year creates hundreds or thousands of separate tax lots and disposals. Each one needs a date, a time, proceeds and cost basis on Form 8949. That is why import-capable tax software (section 5) is essentially mandatory.
- Because bot holding periods are short, nearly all net profit will be short-term gain taxed like wages. The 0%/15%/20% long-term rates will rarely apply unless the bot also holds a long-term core position.
- Per-wallet tracking means that if the bot runs on Exchange A while the user also holds BTC on Exchange B or in a self-custody wallet, basis on A cannot be "borrowed" from lots held on B. The bot's API account should be treated as its own ledger.
- Specific identification can lower taxes, for example by selling the highest-cost lots first. Using it reliably in 2026 means the bot or the tax software must record lot selection (or a written standing order) at the time of each trade. Otherwise the default ordering is FIFO within that account.

### Gaps
- The IRS digital-asset FAQ and Rev. Proc. 2024-28 could not be read directly (irs.gov was blocked). The wording of the default ordering rule (FIFO per wallet when there is no adequate identification) is the researcher's understanding plus secondary sources. No primary IRS text was fetched.
- Unverified background knowledge: realized net capital losses can offset only $3,000 per year of ordinary income ($1,500 if married filing separately), with the rest carried forward. This is consistent with the CoinTracker source's mention of the "$3,000 annual limit".
- Unverified background knowledge: fees paid on a trade are generally added to basis or subtracted from proceeds rather than deducted separately.
- Unverified background knowledge: stablecoin-to-crypto swaps and crypto-to-crypto swaps are disposals, just like sales for USD.

## 2. Broker reporting on Form 1099-DA, and what it means for bot traders

### Takeaway
Custodial US brokers and exchanges began issuing Form 1099-DA for 2025 transactions, reporting gross proceeds only. For transactions on or after 1 January 2026 they must also report cost basis for "covered securities", meaning assets acquired after 2025 in a custodial account at that broker. A bot trader will receive a 1099-DA that may list every disposal. It will often disagree with the trader's own records when assets were transferred in, or when the trader uses specific identification. The trader must reconcile the two, or risk IRS mismatch notices (CP2000).

### Cited Findings
- From the 2026 instructions for Form 1099-DA (per search-result summaries):
  - For 2026 and later, brokers must report basis for digital assets that are covered securities, and may voluntarily report basis for noncovered ones.
  - A covered security is a digital asset acquired after 2025 (for cash, other digital assets, property or services) and held in an account where the broker provides custodial services.
  - Basis-reported short-term transactions use code G and long-term ones use code J.
  — [IRS 2026 Instructions for Form 1099-DA (PDF)](https://www.irs.gov/pub/irs-pdf/i1099da.pdf); [Sovos: IRS releases 2026 Form 1099-DA instructions](https://sovos.com/regulatory-updates/trr/irs-releases-2026-form-1099-da-instructions/); [TaxBandits](https://blog.taxbandits.com/form-1099-da-instructions-for-tax-year-2026-a-complete-guide/)
- For covered securities, brokers must complete boxes 1d, 1g, 2 and 6, and boxes 1h and 1i where applicable. — [IRS 2026 Instructions for Form 1099-DA (PDF)](https://www.irs.gov/pub/irs-pdf/i1099da.pdf) (via search summary)
- Form 1099-DA includes Box 1i, "Wash Sales Loss Disallowed". It is a structural slot only, because the wash-sale rule does not currently apply to crypto (see section 3). — [Countonsheep](https://countonsheep.com/blog/crypto-wash-sale-rule-2026)
- In 2026, all centralized crypto exchanges operating in the US must report gains and losses to the IRS on Form 1099-DA. — [SoFi](https://www.sofi.com/learn/content/how-is-crypto-taxes/)
- Practitioner commentary warns that 1099-DAs can be inaccurate and lead to CP2000 notices. Reconciliation, and sometimes rebuilding cost basis, may be needed. — [Summ: Why your 1099-DA could be inaccurate](https://summ.com/us/blog/why-your-1099-da-could-be-inaccurate); [Summ: How Form 1099-DA will get you a CP2000](https://summ.com/us/blog/how-form-1099-da-will-get-you-a-cp2000); [Camuso CPA](https://camusocpa.com/1099-da-reconciliation-vs-cost-basis-reconstruction/)
- Notice 2026-20 lets taxpayers' own lot identifications control even when they differ from the broker's 1099-DA, through 31 December 2026. — [Winston & Strawn](https://www.winston.com/en/blogs-and-podcasts/tax-impacts/irs-extends-digital-asset-reporting-relief-through-2026-under-notice-2026-20)

### Inferences
- For a high-frequency bot, the 1099-DA could be very long, or could use an aggregate or optional reporting method. The trader's 8949 must still tie to the broker's totals.
- Crypto deposited into the bot's exchange account from elsewhere, or bought before 2026, is "noncovered". The broker may report $0 or unknown basis for it, which overstates gains unless the trader supplies basis.
- Trades on offshore or non-custodial venues (DEXs, foreign exchanges) produce no 1099-DA. They remain fully taxable and must be self-reported.

### Gaps
- Unverified background knowledge: in April 2025 Congress used the Congressional Review Act to repeal the Treasury rule that would have treated DeFi and non-custodial front-ends as brokers. No source was fetched to confirm this.
- Unverified background knowledge: optional or aggregate reporting thresholds for qualifying stablecoins ($10,000) and specified NFTs ($600). The instructions PDF could not be opened.
- Unverified background knowledge: details of the backup-withholding penalty relief that accompanied 1099-DA.

## 3. Wash-sale rule status for crypto in 2026

### Takeaway
As of October 2026 the wash-sale rule (IRC §1091) does **not** apply to crypto, because crypto is property rather than "stock or securities". A bot can sell at a loss and rebuy immediately and still recognize the loss. However, two live proposals would extend §1091 to digital assets:
- the Lummis Senate bill (S.2207, July 2025), and
- the bipartisan Miller–Horsford House discussion draft (December 2025).

Neither is law. The Senate draft as introduced would apply to tax years beginning after 2025, so a 2026 enactment could in principle reach 2026 trades. That creates real retroactivity uncertainty.

### Cited Findings
- As of 2026, crypto is not subject to the wash-sale rule because §1091 covers "stock and securities" and the IRS classifies crypto as property. — [Countrytaxcalc wash-sale guide 2026](https://www.countrytaxcalc.com/tax-guides/usa/wash-sale-rule-guide-2026/); [Countonsheep](https://countonsheep.com/blog/crypto-wash-sale-rule-2026); [Reed Corp](https://reedcorp.tax/helpful-guides/crypto/crypto-wash-sale-rule/)
- As of July 2026 two active proposals target the crypto wash-sale gap: a Senate digital-asset tax bill introduced in 2025 and a bipartisan House discussion draft from December 2025. Neither is law. The Senate draft as introduced would apply to tax years beginning after 2025, so a bill enacted in mid-2026 could reach transactions already completed that year. — [Countonsheep](https://countonsheep.com/blog/crypto-wash-sale-rule-2026) (search summary); [Chainwise CPA](https://chainwisecpa.com/crypto-wash-sale-2026/)
- Senator Lummis's digital asset tax bill (S.2207, July 2025):
  - a $300 de minimis exemption for small transactions;
  - lending treated as generally non-taxable;
  - mining and staking income deferred until sale;
  - extension of §1091 to digital assets, excluding payment stablecoins and assets held by dealers in the ordinary course.
  — [Lummis press release](https://www.lummis.senate.gov/press-releases/lummis-unveils-digital-asset-tax-legislation/); [The Tax Adviser, Aug 2026](https://www.thetaxadviser.com/issues/2026/aug/tax-legislation-for-digital-assets-whats-the-conversation-in-congress/)
- The House discussion draft from Reps. Max Miller (R-OH) and Steven Horsford (D-NV), released December 2025, would also apply §1091 to digital assets. — [Sullivan & Cromwell tax policy update, Jan 2026](https://www.sullcrom.com/insights/memo/2026/January/December-29-January-5-Tax-Policy-Update); [Stocktwits](https://stocktwits.com/news-articles/markets/cryptocurrency/congress-plan-to-slap-washsale-rules-on-bitcoin-criticsm/cZ00IOfReDf?.tsrc=rss)
- Earlier attempts failed: the 2021 Build Back Better Act and the Lummis-Gillibrand RFIA both included crypto wash-sale language. — [Countonsheep](https://countonsheep.com/blog/crypto-wash-sale-rule-2026)
- The House Ways & Means oversight subcommittee held a cryptocurrency tax hearing in July 2025. — [EY Tax News, 16 July 2025](https://taxnews.ey.com/news/2025-1503-ways-and-means-subpanel-holds-cryptocurrency-hearing)

### Inferences
- Bot strategies that harvest losses by selling and immediately rebuying, or that churn the same asset at a loss, would be most affected if §1091 is extended. Developers should log enough data (61-day windows, replacement lots) to recompute wash-sale adjustments if a law passes with a 2026 effective date.
- Separately from §1091, the IRS could in principle challenge purely tax-motivated round trips under general doctrines such as economic substance. No 2026 source discussed this for crypto specifically.

### Gaps
- No confirmation was found that any crypto wash-sale provision was enacted between July and October 2026. The search returned no such news, so the status is presumed "not enacted", but it is not definitively confirmed for the most recent weeks.
- The Miller–Horsford draft's exact effective date and whether it has been formally introduced as a numbered bill were not confirmed.

## 4. Trader tax status (TTS) and the §475(f) mark-to-market election for crypto

### Takeaway
TTS is a facts-and-circumstances test from case law, with no statutory bright line. It requires substantial, frequent, regular and continuous trading aimed at short-term swings. A bot can help show frequency, but courts also weigh the trader's personal involvement and whether trading is a business. The §475(f) election covers only "securities" and "commodities". Because the IRS treats crypto as property, eligibility for spot crypto is a contested grey area. The case is stronger for BTC and ETH, which the CFTC treats as commodities, and for regulated crypto futures. For a small personal account this is generally not realistic or worth the audit risk without a specialist CPA.

### Cited Findings
- There is no statutory law with objective tests for trader tax status; subjective case law applies (Green Trader Tax / Robert Green CPA). — [NexusFi summary of GreenTraderTax](https://nexusfi.com/d/tax-legal/greentradertax)
- §475(f) mark-to-market treats all positions as sold at fair market value on the last day of the year. Gains and losses become ordinary rather than capital. — [NexusFi summary of GreenTraderTax](https://nexusfi.com/d/tax-legal/greentradertax)
- Per Green's 2025 guidance: "the IRS continues to treat most digital assets as 'property,' not securities or commodities, and crypto still isn't subject to wash sale or 475 MTM rules", but "there is a strong case that major cryptocurrencies, such as bitcoin or Ethereum, would be considered commodities." — [Interactive Brokers Campus / Green Trader Tax PDF, Sept 2025](https://www.interactivebrokers.com/campus/wp-content/uploads/sites/2/2025/09/CRYPTOCURRENCIES-AMPAMP-DIGITAL-ASSETS-–-TAX-TREATMENT-IN-2025-UPDATED.PDF-Content-Attachment-9_17_2025-8_30_46-PM.pdf); [NexusFi summary](https://nexusfi.com/d/tax-legal/greentradertax)
- Lukka and McDermott Will & Emery analysis: taxpayers may be able to take the position that their virtual currency is a security or commodity and make a §475 election. The taxpayer must also be a "trader" rather than an investor, meaning someone seeking speculative profit from short-term market swings. — [Lukka](https://lukka.tech/can-traders-in-virtual-currency-elect-the-mark-to-market-and-character-rules-of-section-475f/)
- CoinTracker's summary of the trade-offs:
  - Benefits: a §475(f) election removes the $3,000 capital-loss limit and allows unrealized losses at year-end to be deducted.
  - Costs: all gains, including on positions held more than 12 months, become ordinary income.
  - Eligibility: because crypto is "property" under Notice 2014-21, applying §475(f) to it is a grey area, but it is clearer for bitcoin and crypto derivatives that the CFTC treats as commodities.
  — [CoinTracker](https://www.cointracker.io/blog/write-off-unlimited-losses)
- Bitcoin.tax also has a dedicated explainer on TTS for crypto. — [bitcoin.tax: trader tax status for cryptocurrency](https://bitcoin.tax/blog/trader-tax-status-for-cryptocurrency)

### Inferences
- For a small account, the main §475(f) benefit is turning large losses into ordinary losses. That matters only if the bot loses money. If the bot makes money, short-term gains are already taxed at ordinary rates, so §475 adds little apart from avoiding wash-sale tracking, which is currently moot for crypto.
- TTS without §475 can still allow business-expense deductions (servers or VPS, data feeds, software) on Schedule C. The case-law tests make TTS hard to defend for part-time or small accounts. Practitioners often look for high volume, near-daily activity and meaningful account size. No specific numeric thresholds were verified in this research.
- The bot doing the trading does not by itself establish TTS. The trader's own business activity in developing and supervising the system is what counts.

### Gaps
- Unverified background knowledge: the §475(f) election deadline (generally by the original due date of the prior year's return, e.g., about 15 April 2026 for tax year 2026, for existing individual taxpayers) and the Form 3115 filing requirement. No primary source was fetched.
- No 2026 IRS guidance specifically addressing §475(f) for crypto was found. The issue appears unresolved.
- Practitioner rules of thumb for TTS volume (such as trades per year or days traded) were not verified from a source in this session.

## 5. Tax software that can import thousands of bot trades, and cost

### Takeaway
The major consumer crypto-tax tools price by number of transactions per tax year. A bot doing more than 3,000 trades a year will be on the top consumer tiers, roughly $199–$599 a year or more. The tools import via exchange API or CSV and produce Form 8949, Schedule D and TurboTax/TaxAct files.

### Cited Findings
- Koinly:
  - Newbie: up to 100 transactions, $49 per tax year.
  - Hodler: up to 1,000, $99.
  - Trader: up to 3,000, $199.
  - Pro: up to 10,000 (price not confirmed in the source).
  - Transactions above 10,000 are sold in packs of 1,000 on the Pro plan.
  - All plans have the same features, and you pay only to download reports.
  - US outputs include Form 8949, Schedule D, TurboTax/TaxAct files and full history.
  — [Koinly support: tax plans](https://support.koinly.io/en/articles/9856841-tax-plans); [Koinly support: how pricing works](https://support.koinly.io/en/articles/9489958-how-pricing-works-in-koinly)
- CoinLedger:
  - Hobbyist: $49 (100 transactions).
  - Investor: $99 (1,000).
  - Pro: $199 and up (3,000 and up).
  - A free tier offers unlimited-transaction tracking, but reports require a paid plan.
  — [Summ: best software for 1099-DA reporting](https://summ.com/us/blog/best-software-for-1099-da-reporting) (secondary)
- CoinTracker: $59 for 100 transactions up to $599 for 10,000 transactions, plus full-service options up to $3,499. — [Summ: best software for 1099-DA reporting](https://summ.com/us/blog/best-software-for-1099-da-reporting) (secondary)

### Inferences
- A bot doing, say, 50 trades a day produces about 18,000 disposals a year (plus fees and transfers), which is above the standard 10,000-transaction tiers. Expect custom or enterprise pricing, add-on packs, or a CPA engagement.
- Tight bot design helps: fewer, larger trades, and native logging of fills with timestamps, fees and lot IDs. This lowers software cost and makes 1099-DA reconciliation easier.
- Per-wallet basis and 1099-DA reconciliation features are now key selection criteria.

### Gaps
- Koinly Pro's exact 2026 price and the per-1,000 add-on price were not confirmed.
- CoinLedger and CoinTracker prices come from a secondary blog (Summ, a competitor) and should be checked on the vendors' pricing pages.
- Other tools (TokenTax, ZenLedger, Awaken, CoinTracking, Summ) were not price-checked.
- Whether vendors count fills, orders or both as "transactions" affects cost for bots and was not verified.

## 6. Legal: running a bot, exchange ToS, market manipulation, offshore exchanges and VPNs, CFTC jurisdiction, and 2025–2026 developments

### Takeaway
No US federal law prohibits an individual from running an automated bot on their own account. Major US exchanges explicitly allow API-based bots: Kraken does, and Coinbase and others offer APIs. The legal risks lie elsewhere:
- **Manipulative strategies.** Wash trading, spoofing and pump-and-dump schemes are prosecuted for crypto (the DOJ's Gotbit case ended in prison time).
- **Offshore venues.** Using offshore exchanges that bar US persons, especially via VPN or false information, breaches their terms and risks account lock or freeze. The exchanges themselves have faced criminal penalties: OKX pleaded guilty and paid more than $504M in February 2025.

On regulation:
- The GENIUS Act (stablecoins) became law on 18 July 2025.
- The CLARITY Act (market structure) passed the House in July 2025 but failed a Senate cloture vote 49–50 on 15 September 2026. It is stalled, not dead.
- The CFTC has authorized US-listed perpetual futures (Coinbase, July 2025; Kalshi BTC perp and a policy statement, May 2026) and listed spot crypto on DCMs (December 2025).

### Cited Findings

**Bots and exchange terms**
- Kraken allows customers to trade with bots, either their own built on Kraken's REST/WebSocket APIs or third-party bots. — [Kraken Support: Does Kraken allow trading bots?](https://support.kraken.com/es/articles/360001373983)
- Binance.com's Terms of Use say it "is unable to provide services to any U.S. person."
  - Users identified as US persons got a 14-day deadline to close positions and withdraw, after which accounts were locked.
  - Some users may be required to show their registrations comply with the ToS.
  - Although some US users bypassed blocks with VPNs, that violates the terms.
  — [The Block: Binance blocking US persons, 14-day deadline](https://www.theblock.co/post/85589/binance-blocking-us-users-14-day-deadline-new-email); [Decrypt](https://decrypt.co/49317/binance-gives-us-users-14-days-to-leave-exchange)

**Offshore exchanges serving US persons**
- OKX's operator, Aux Cayes FinTech, pleaded guilty (February 2025) to operating an unlicensed money transmitting business serving US customers and agreed to pay more than $504M: $420.3M forfeiture and an $84.4M fine.
  - Court documents say an OKX employee told a prospective American customer to "just put a random country" to get past sign-up.
  - OKX served US customers who made more than $1 trillion in transactions from 2018 to early 2024.
  — [DOJ SDNY press release](https://www.justice.gov/usao-sdny/pr/okx-pleads-guilty-violating-us-anti-money-laundering-laws-and-agrees-pay-penalties); [Decrypt](https://decrypt.co/307554/okx-pleads-guilty-500-million-us-customers)

**Market manipulation enforcement**
- DOJ crypto market manipulation crackdown (October 2024): 14 individuals and 4 firms charged (Gotbit, ZM Quant, CLS Global, MyTrade) for wash trading and market manipulation. Gotbit's software traded between multiple controlled accounts to fake volume. Founder Aleksei Andriunin was sentenced to 8 months in prison and the firm forfeited $23M. DOJ called Gotbit the third crypto market maker convicted in the crackdown. — [Decrypt: Gotbit founder sentenced](https://decrypt.co/325111/gotbit-founder-sentenced-prison-crypto-wash-trading); [Decrypt: charges](https://decrypt.co/285503/feds-charge-gotbit-others-market-manipulation?amp=1)
- The SEC brought parallel charges against Gotbit and others for wash trading. — [Global Relay GRIP](https://grip.globalrelay.com/?p=95190); [FinTelegram](https://fintelegram.com/gotbit-and-russian-executives-charged-by-u-s-doj-and-sec-for-crypto-market-manipulation/)

**CFTC jurisdiction and recent CFTC actions**
- The CFTC treats bitcoin and some crypto derivatives as commodities. — [CoinTracker](https://www.cointracker.io/blog/write-off-unlimited-losses)
- Coinbase Derivatives (a DCM) self-certified nano BTC and ETH perpetual-style futures on 26 June 2025. The CFTC did not object, and trading became effective 21 July 2025. — [Proskauer](https://www.proskauer.com/alert/opening-the-door-to-perps-the-cftc-approves-us-listed-perpetual-futures); [Coinbase blog](https://www.coinbase.com/blog/perpetual-futures-have-arrived-in-the-us); [Pillsbury](https://www.pillsburylaw.com/en/news-and-insights/cftc-perpetual-futures-btc-eth-crypto-derivatives.html)
- On 29 May 2026 the CFTC:
  - approved KalshiEX's bitcoin perpetual futures contract;
  - issued a policy statement on other exchanges listing perpetual contracts;
  - published a staff advisory on 24/7 trading and clearing;
  - issued an interpretive letter and no-action position letting Coinbase Financial Markets treat Deribit perpetuals as foreign futures, which opens access for US clients.
  — [Proskauer](https://www.proskauer.com/alert/opening-the-door-to-perps-the-cftc-approves-us-listed-perpetual-futures); [Yahoo Finance: Coinbase wins CFTC approval for global perps/options](https://finance.yahoo.com/markets/crypto/articles/coinbase-wins-cftc-approval-offer-150730699.html)
- On 4 December 2025, Acting Chairman Caroline Pham announced that CFTC-registered DCMs may for the first time list spot crypto contracts, including leveraged retail spot. Bitnomial launched the first such market the week of 8 December 2025. — [CFTC press release 9163-25](https://www.cftc.gov/PressRoom/PressReleases/9163-25); [Morrison Foerster](https://www.mofo.com/resources/insights/251210-cftc-announces-launch-of-first-leveraged-spot-cryptocurrency); [Hogan Lovells](https://www.hlc.com/en/publications/cftc-authorizes-spot-crypto-trading-on-dcms)
- Pham served as Acting Chair from 20 January 2025, ran the CFTC "Crypto Sprint", and later left to become MoonPay's chief legal officer. — [Bloomberg Government](https://news.bgov.com/crypto/moonpay-says-cftcs-caroline-pham-will-join-crypto-payments-firm); [Finance Magnates](https://www.financemagnates.com/executives/cftc-promotes-caroline-pham-as-acting-chair-report/)

**Legislation**
- The GENIUS Act was signed 18 July 2025. It creates the first federal framework for payment stablecoins, covering issuer licensing, reserves, disclosure and compliance. — [Debevoise](https://www.debevoise.com/insights/publications/2025/07/genius-act-progresses-in-congress-as-stablecoin); [Covington](https://www.cov.com/news-and-insights/insights/2025/07/the-genius-act-becomes-law-key-provisions-from-the-federal-stablecoin-regulatory-framework); [The Block](https://theblock.co/post/363425/trump-signs-stablecoin-genius-act-cementing-first-major-crypto-framework-in-us-law)
- CLARITY Act (Digital Asset Market Clarity Act):
  - Passed the House 294–134 on 17 July 2025.
  - Advanced by the Senate Banking Committee on 14 May 2026.
  - Failed Senate cloture 49–50 on 15 September 2026 (60 votes were needed).
  - The main sticking points were ethics provisions on officials' crypto holdings and stablecoin yield.
  - Sen. Tillis voted no in order to preserve a motion to reconsider. The next windows are after the 3 November 2026 midterms and in the lame-duck session.
  — [Orrick, Oct 2026](https://www.orrick.com/en/Insights/2026/10/The-CLARITY-Act-Stalls-in-the-Senate-Whats-Next-for-Digital-Asset-Regulation); [Davis Wright Tremaine, May 2026](https://www.dwt.com/blogs/financial-services-law-advisor/2026/05/senate-banking-crypto-market-structure-bill); [DeFi Rate](https://defirate.com/clarity-act-fact-sheet/); [CoinDesk, Aug 2026](https://www.coindesk.com/policy/2026/08/05/here-are-the-possible-outcomes-for-clarity-right-now); [Latham crypto policy tracker](https://www.lw.com/en/us-crypto-policy-tracker/legislative-developments)
- The SEC and CFTC are coordinating ("joining forces") on crypto regulation. — [Summ](https://summ.com/us/blog/the-sec-and-cftc-are-joining-forces-on-crypto-regulation) (secondary; details not verified)

### Inferences
- **Practical legality.** Running a bot on a regulated US venue (Coinbase, Kraken, Gemini, or a CFTC-regulated DCM) with your own money, within the venue's API terms (rate limits, no abuse), is legal and common.
- **Bot logic to avoid.** The bot must never:
  - place orders it intends to cancel before execution in order to move prices (spoofing or layering);
  - trade with itself or with coordinated accounts to fake volume (wash trading);
  - coordinate pumps.
  These patterns are what DOJ, CFTC and SEC cases target. They can be triggered by accident, for example a market-making bot crossing its own orders, so self-trade prevention settings should be enabled.
- **Offshore perps.** US individuals can now get regulated perpetual-style exposure onshore (Coinbase Derivatives nano perps, Kalshi BTC perp, Deribit access via Coinbase Financial Markets). That lowers the incentive to use offshore perp venues through VPNs. Doing so breaches ToS and risks frozen funds with little US legal recourse. The exchange-level criminal exposure in the OKX case falls on the platform, but users face loss of access to funds and tax reporting obligations on gains regardless.
- **CLARITY failure.** With CLARITY stalled, the SEC/CFTC split over which tokens are securities and which are commodities remains unsettled in statute. Agency-level guidance and no-action relief remain the main tools in 2026.

### Gaps
- Unverified background knowledge: the CEA anti-spoofing provision (7 U.S.C. §6c(a)(5)(C)) and the CFTC's anti-manipulation rule 180.1 apply to spot crypto "commodities" in interstate commerce (fraud and manipulation authority). No CFTC primary source was fetched for this.
- Unverified background knowledge: specific CFTC spoofing cases involving crypto by individuals. No 2025–2026 example was verified.
- Unverified background knowledge: Coinbase's and Gemini's API terms on bots. Only Kraken's was confirmed.
- No source was found on whether merely using a VPN to access an offshore exchange is itself a crime for an individual user. The documented consequences are ToS breach and account lock or freeze. User-level criminal exposure appears low but unverified.
- Unverified background knowledge: foreign-account reporting for funds on offshore exchanges (FBAR / FinCEN 114 and FATCA Form 8938). FinCEN has historically said virtual currency alone does not trigger FBAR, but has proposed changing this. Current 2026 status was not verified.
- Unverified background knowledge: the SEC's 2025 dismissal of exchange cases (Coinbase, Binance, Kraken) and its "Project Crypto" or token taxonomy work. Not verified in this session.

## 7. State-level considerations (e.g., the New York BitLicense)

### Takeaway
State money-transmission and crypto-licensing regimes decide which exchanges a resident can legally use. New York's BitLicense is the most restrictive. Binance.US and Kraken do not serve New York residents, so a New York bot trader is limited to NYDFS-licensed or trust-chartered venues, which may restrict API access, assets and derivatives. State income tax on short-term gains also applies, at the resident's state rate.

### Cited Findings
- Binance (including Binance.US) does not serve New York residents because it lacks a BitLicense or NYDFS approval. Kraken is not authorized in New York, holding neither a BitLicense nor a New York trust charter. — [Koinly: best crypto exchanges in New York 2026](https://koinly.io/blog/best-crypto-exchanges-new-york/)
- The BitLicense covers buying, selling, storing and transferring crypto and is described as "tough to get and even tougher to keep". Many exchanges skip New York, and some instead use a Limited Purpose Trust Charter under NYDFS. — [Koinly: best crypto exchanges in New York 2026](https://koinly.io/blog/best-crypto-exchanges-new-york/)
- Kraken historically suspended New York service rather than apply for a BitLicense (2015). — [Bitcoin Magazine](https://bitcoinmagazine.com/business/kraken-joins-exchanges-refusing-apply-bitlicense-suspends-service-new-york-1439245937-2)

### Inferences
- Before building exchange integrations, a New York resident should confirm the target exchange's state availability and whether API trading and specific pairs are enabled for New York accounts.
- Other states with notable regimes (California's DFAL licensing, Hawaii historically) may also limit availability. These were not researched here.
- State income tax adds to the federal short-term rate. California, for example, taxes capital gains as ordinary income. Bot traders in no-income-tax states (TX, FL, WA (which has a separate capital gains excise on long-term gains), NV, etc.) avoid this layer. These state tax specifics are researcher inferences and were not sourced.

### Gaps
- No verified 2026 list of exchanges available in New York, Hawaii or California.
- California DFAL licensing status and effective date (originally July 2025, reportedly delayed to July 2026) were not verified.
- State tax treatment of crypto gains was not researched with sources.
