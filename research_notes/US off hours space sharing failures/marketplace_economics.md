# US Off-Hours Space-Sharing Marketplaces: Economics and Failure Modes

Research date: 2026-10-25 (coverage through October 2026). Method: 15 tool calls, WebSearch only (standard and extended modes). WebFetch was not used, so every fact below comes from search-result snippets and summaries, not opened pages. Where I could not isolate the exact page behind a fact, the nearest result URL is listed and the attribution is marked. Tags: [single-source] = one source or an aggregator; [unverified] = no primary document tied to the claim; [inference] = my reasoning, not a sourced fact. Many key questions remain largely unanswered; see Gaps under each section and the list at the end.

## 1. Frequency and fragmentation of demand

### Takeaway
No repeat-booking or booking-frequency data for any US space-sharing platform surfaced. The directional evidence is that early players targeted episodic use (meetings, offsites, parties, shoots), while the one clear scale success in the set (SpotHero) sells a high-frequency, standardized product.

### Cited Findings
- Splacer (2015-2017): hosts list unusual venues bookable by the hour; the company said it targeted businesses that would become repeat customers for meetups and parties; ~236 NYC listings by first December 2015 and ~700 listings by March 2017 (2017 is the newest coverage found) — [FarWest Capital](https://www.farwestcapital.com/blog/a-better-place-for-offsites/); [DNAinfo](https://www.dnainfo.com/new-york/20170301/williamsburg/splacer-venues-events-rental)
- Peerspace listed 45,000+ spaces at the time of its August 2026 Chapter 11 filing (2026-08-30) — [WhatNow](https://whatnow.com/news/trending/san-francisco-venue-rental-marketplace-with-45000-spaces-files-for-chapter-11-bankruptcy/) [single-source headline]
- SpotHero announced it had passed $1 billion in parking reservations sold (2022-10) — [SpotHero press release](https://spothero.com/press/spothero-eclipses-1-billion-in-parking-reservations-sold). Cumulative volume only; no per-user frequency given.
- ResortPass sells a standardized day pass; a 2019 company release put the average day-pass reservation at about $250 including food and beverage — [Hospitality Net coverage](https://www.hospitalitynet.org/news/4096098/resortpass-sees-record-growth-fueled-by-experience-economy-and-redefines-guest-revenue-opportunities-for-hotels-resorts) [attribution to the 2019 release came from a search summary; exact page not isolated]

### Inferences
- [inference] Episodic use cases (meeting rooms, photo studios, parties, offsites) imply low purchase frequency per user, so brand habit and repeat use must be built separately in each city and vertical. The only sourced high-frequency SKUs in this set are parking and standardized day passes.
- [inference] Tavel's stage-one logic (win a small, constrained market by a wide margin; see Section 9) cuts against horizontal "any space for any use" positioning, which several space platforms adopted (Splacer, Breather, Peerspace all spanned multiple use cases).

### Gaps
- No repeat rates, purchase-frequency distributions, or cohort retention for Peerspace, Splacer, Breather, Swimply, ResortPass, or any space platform.
- No consumer survey data on how often a typical person books a meeting room, studio, or pool.
- Spacious and Codi returned no results in search; nothing on their use mix.

## 2. Disintermediation and leakage

### Takeaway
No quantitative leakage data (share of repeat bookings taken off-platform) was found for any space marketplace. The structural exposure is clear from commission models, but I found no description of how Peerspace, Swimply, or Splacer enforced on-platform repeat bookings.

### Cited Findings
- Splacer: listing and searching were free to users, and the company kept 15% of each booking — [FarWest Capital](https://www.farwestcapital.com/blog/a-better-place-for-offsites/) (undated coverage, 2015-2017 era)
- Facilitron: the service fee applies only to approved paid rentals; operators may absorb, pass it to renters, or split it; the rate is not published — [FitGap profile](https://us.fitgap.com/products/036750/facilitron) (undated)
- SpotHero: garages agreed to give ~15% of parking fees for bookings made through the network, because the network brought incremental parkers — [Harvard D3 case study](https://d3.harvard.edu/platform-digit/submission/spothero-kicks-parking-frustrations-to-the-curb/index.html) (2017-era data)

### Inferences
- [inference] Free listing plus a commission on each booking is the structure most exposed to leakage: after first contact, owner and renter can transact directly. The platforms that justify a commission per booking (SpotHero, Splacer) must sell incremental demand the owner could not reach alone. That is the test a space platform has to pass, and no leakage data exists to show how often it does.
- [inference] Facilitron's model (software free to operators, fee only on paid rentals) is aligned with on-platform workflow for institutional buyers. It does not show whether leakage was reduced.

### Gaps
- No leakage or repeat-off-platform rates for any space marketplace.
- Platform countermeasures (messaging restrictions, payment-on-platform, guarantees, insurance, SaaS workflow lock-in) were not researched beyond the Facilitron and SpotHero structures above.

## 3. Customer acquisition and AI search

### Takeaway
Several studies (mostly vendor or agency, not peer-reviewed) report large organic click-through-rate declines on informational queries where Google AI Overviews appear, from mid-2024 through December 2025. None measured space, venue, or parking marketplaces specifically, so their exposure is unknown. For a marketplace whose demand arrives via "[venue type] in [city]" searches, these studies point to a shrinking free-acquisition channel.

### Cited Findings
- Seer Interactive (reported 2025-2026; study from mid-2024): organic CTR on informational queries with AI Overviews fell 61%; paid CTR on those queries fell 68%; organic CTR fell 41% even on queries without AI Overviews — [Search Engine Land](https://searchengineland.com/google-ai-overviews-drive-61-drop-organic-paid-ctr-464212)
- Seer, earlier analysis of ~10,000 keywords: organic CTR fell from 1.41% to 0.64% year over year where AI Overviews appeared — [Seer Interactive news page](https://www.seerinteractive.com/news/search-engine-land-shares-aio-impact-on-ctr-cites-latest-seer-interactive-findings) [figures from search summary]
- Ahrefs (data through December 2025): 58% CTR reduction for top-ranking pages across ~300,000 keywords, up from 34.5% in April 2025; position-one CTR on informational keywords fell from 0.076 (Dec 2023) to 0.039 (Dec 2025) — [PPC Land](https://ppc.land/googles-ai-summaries-now-swallow-58-of-clicks-that-once-went-to-websites/) [aggregator; original Ahrefs study not opened]; earlier 34.5% figure — [PPC Land](https://ppc.land/googles-ai-overviews-cut-organic-clicks-by-34-5-despite-company-claims/)
- Authoritas: 47.5% reduction in organic clicks [unverified; no URL tied to this figure in results]
- Agency data reported by Digiday (August 2026, via secondary report): across 54 client accounts, organic sessions fell 10.5% from January 2025 to April 2026, while AI-platform sessions rose 163% from a much smaller base; AI referrals did not replace lost organic sessions one for one but converted at a higher rate — [Relevant Audience](https://www.relevantaudience.com/geo/ai-overviews-organic-traffic-54-advertisers-study/) [single-source secondary report of Digiday]
- Caveat from Seer: organic CTR also fell on queries without AI Overviews, which points to broader causes (AI chatbots, social search). Google maintains AI Overviews improve engagement; this is disputed — [Search Engine Land](https://searchengineland.com/google-ai-overviews-drive-61-drop-organic-paid-ctr-464212)
- Peerspace's 2026 bankruptcy filings, as found, disclose no CAC, LTV, or channel-mix data — [Bondoro case summary](https://app.bondoro.com/preview/cases/Peerspace_Inc/case-summary)

### Inferences
- [inference] The metrics conflict: agency session declines (~10%) and tool-measured CTR declines (~40-60%) measure different things (sessions vs. CTR, different sample and period). Do not average them.
- [inference] Marketplaces relying on informational "best venues in [city]" queries face the largest exposure. Transactional queries for a specific standard product (for example, "parking near X") may be less exposed, but no study in this set splits by query intent.
- [inference] For episodic use, LTV per user is bounded by one to three bookings, so any paid CAC must be recovered in one or two transactions at a 15-20% take. No data here tests whether that works.

### Gaps
- No CAC, LTV, or channel-mix data for any US space marketplace.
- No study of AI Overviews or AI Mode effects on venue, meeting-room, pool, or parking marketplaces. Google AI Mode (2025-2026) was not separately measured in results.

## 4. Take rate vs. value

### Takeaway
Observed commission or host-fee rates in the set cluster around 15-20% (Splacer 15%; SpotHero ~15% in a 2017-era case; Swimply 15% to 20%, depending on source). Swimply's sources conflict. I found no verified take-rate data for Airbnb, Etsy, or current SpotHero terms, so the comparison the question asks for is not answered here.

### Cited Findings
- Splacer: company keeps 15% of each booking — [FarWest Capital](https://www.farwestcapital.com/blog/a-better-place-for-offsites/) (2015-2017 era)
- SpotHero: ~15% of parking fees from garages (2017-era case) — [Harvard D3](https://d3.harvard.edu/platform-digit/submission/spothero-kicks-parking-frustrations-to-the-curb/index.html); commission-based, no owned facilities — [Altss profile](https://altss.com/profile/spothero-inc)
- SpotHero revenue estimate $50M-$75M (third-party estimate, not company disclosure) — [Similarweb](https://www.similarweb.com/company/spothero.com)
- SpotHero acquired by Uber for $617M cash, April 2026, per the summary of Uber's Q2 2026 filing [single-source; no URL in results; unverified]
- Swimply, conflicting disclosures: Wikipedia: 20% host fee and 10% guest fee — [Wikipedia](https://en.wikipedia.org/wiki/Swimply); The College Investor: 15% host service fee and renter fee of 10% (groups of 1-14) or 15% (15+) — [College Investor review](https://thecollegeinvestor.com/34874/swimply-review/); Sidehusl and Startup Savant: 15% — [Sidehusl](https://sidehusl.com/rent-swimming-pools/); [Startup Savant](https://www.startupsavant.com/news/swimply-scoops-10-mil). Revenue range $10M-$50M per Dealroom (undated) — [Dealroom](https://dealroom.co/companies/swimply/). One 2023 piece projecting several hundred million dollars cites no source and is disregarded.
- Facilitron: pay-as-you-go service fee on approved paid rentals; rate undisclosed; vendor claims no upfront operator fees (promotional text quoted on Trustpilot) — [Trustpilot](https://ca.trustpilot.com/review/facilitron.com); [Software Advice](https://www.softwareadvice.com/cafm/facilitron-profile)
- ResortPass: hotel listings described as free, with a subscription for day-access software; a 2019 release describes a pay-per-performance model with no upfront fees — [Skift](https://skift.com/?p=542446) [attribution partly from search summary]
- ResortPass revenue range $1M-$10M and valuation range $100M-$250M (Dealroom, undated, no fiscal year) — [Dealroom](https://dealroom.co/companies/resortpass/)
- Gurley's 2013 "rake" essay, as summarized by secondary sources only: eBay take rate just under 10% (2011: ~$6.6B revenue on ~$68.6B sales); a table of take rates ranging from ~1.9% (OpenTable) to ~70% (Shutterstock); the claim that a winner-take-all marketplace should minimize friction in product and pricing — [Rohit Nuwal](https://rohitnuwal.substack.com/p/take-rates); [KJ Labuz](https://kjlabuz.substack.com/p/takerates); [Rework](https://resources.rework.com/libraries/marketplace-growth/marketplace-take-rate) [primary Above the Crowd essay not opened; figures unverified against the original]

### Inferences
- [inference] Splacer's and Swimply's 15-20% host commissions are charged to hosts who have no pre-existing customer base from the platform. SpotHero's garage commission is accepted because the platform brings incremental parkers. The value test for space owners is the same: is the incremental booking worth the fee?
- [inference] Facilitron's pattern (free software, fee only on paid bookings, institutional customers) reduces the owner's objection to a commission, but it also implies lower take rates tied to volume that is institutional, not consumer.
- [inference] Swimply's conflicting fee disclosures could reflect changes over time or differences between hosts or regions. Unresolved by these sources.

### Gaps
- No verified take-rate data for Airbnb, Etsy, Turo, Peerspace, or current SpotHero terms (not searched).
- No owner-side ROI data (what share of host revenue is incremental vs. cannibalized).

## 5. Supply-side issues

### Takeaway
The supply-side evidence is qualitative and mostly comes from Breather, a leased flex-office operator rather than a marketplace. No data on owner motivation, staffing requirements, cold-start timelines, liquidity thresholds, or quality dispersion surfaced.

### Cited Findings
- Breather (flex operator, Montreal-founded, US locations): laid off 17% of staff in December 2019; hired Moelis to explore a sale or new capital, with little interest reported; announced closure of 400+ sites in December 2020 and a shift to an online-only platform — [Commercial Observer](https://commercialobserver.com/2020/12/breather-flex-space-closing-covid/); [Bisnow](https://bisnow.com/national/news/coworking/breather-closes-400-locations-lays-off-employees-online-only-107142)
- Breather CEO Bryan Murphy blamed the pandemic and said the operator model "doesn't make sense" and "I'm not sure it ever made sense" (December 2020) [single-source quote, from search summary; exact page not isolated]
- Breather faced landlord suits over unpaid rent, including a SoHo building claim of $79,000 — [AllWork.space](https://allwork.space/2020/12/breather-faces-lawsuit-from-manhattan-landlord/) [single-source]
- Breather's status is reported inconsistently: Bisnow reported it would continue as an online platform; a profile site says it shut down operations in 2020 [conflicting; unverified]
- ResortPass partner counts conflict: ~1,300 hotels (Dealroom) vs. ~900 brands (Skift) — [Dealroom](https://dealroom.co/companies/resortpass/); [Skift](https://skift.com/?p=542446)

### Inferences
- [inference] Breather's failure is an operator/lease model problem (fixed property costs, rent liabilities), not evidence about the marketplace model. Commentary that conflates the two should be treated with caution.
- [inference] Owners who must staff or be present face an opportunity-cost problem; no data quantifies it.

### Gaps
- No data on owner motivation, extra revenue as a share of owner income, staffing needs, cold-start city timelines, or liquidity thresholds for any space platform.
- Spacious, Codi, and Splacer supply-side post-mortems not found.

## 6. Trust, safety, and liability

### Takeaway
The most concrete event in the set is Peerspace's Chapter 11 filing (2026-08-30), which the company reportedly used to pause a premises-liability trial brought by a guest paralyzed in a fall at a listed space. It is the one case here linking a space marketplace's failure to liability exposure. Reporting comes from docket aggregators and a news rewrite, not the docket itself, and the outcome of the suit was not found.

### Cited Findings
- Peerspace (San Francisco; hourly venue marketplace) filed for Chapter 11 under Subchapter V on 2026-08-30 in the Northern District of California (Case 3:26-bk-30766, Judge Dennis Montali) — [WhatNow](https://whatnow.com/news/trending/san-francisco-venue-rental-marketplace-with-45000-spaces-files-for-chapter-11-bankruptcy/); [InForuptcy docket](https://www.inforuptcy.com/browse-filings/california-northern-bankruptcy-court/3:26-bk-30766/bankruptcy-case-peerspace-inc) [single-source reporting plus aggregators]
- Stated purpose: to help resolve pending litigation; the company said the filing "does not reflect its operations or platform health" and expects no effect on listings, bookings, or payouts — [WhatNow](https://whatnow.com/news/trending/san-francisco-venue-rental-marketplace-with-45000-spaces-files-for-chapter-11-bankruptcy/) [company statement as relayed by reporting]
- Underlying suit: negligence and premises liability, brought by a guest left paraplegic after a fall at a space listed on the platform; one report says the filing came the day trial was set to begin — [WhatNow](https://whatnow.com/news/trending/san-francisco-venue-rental-marketplace-with-45000-spaces-files-for-chapter-11-bankruptcy/). A jobs-listing site says the trial began the same day, which conflicts with the other wording; timing unconfirmed — [Simplify](https://simplify.jobs/c/Peerspace)
- Docket dates per aggregators (as of October 2026): §341 meeting October 5, 2026; claims deadline November 9, 2026; plan due November 30, 2026; Subchapter V trustee Gina R. Klump; a hearing on tentative approval of a plan and disclosure statement is calendared with no date or ruling shown — [Bondoro case summary](https://app.bondoro.com/preview/cases/Peerspace_Inc/case-summary); [Bondoro filing alert](https://bondoro.com/peerspace-filing-alert/); [court calendar PDF](https://www.canb.uscourts.gov/sites/default/files/judge/calendar/09.25%20at%2010_0.pdf)
- Only Peerspace, Inc. is a debtor; four international subsidiaries (Australia, Canada, Netherlands, UK) are not, and hold separate Stripe accounts — [Bondoro case summary](https://app.bondoro.com/preview/cases/Peerspace_Inc/case-summary)
- Peerspace funding milestones (dates not established in search): $1.5M raise, then a $5M Series A that funded NYC expansion — [TechCrunch](https://techcrunch.com/?p=1235977); [TechCrunch](https://techcrunch.com/?p=1058789)

### Inferences
- [inference] Premises liability is a tail risk that scales with bookings. A marketplace that does not own the premises can still be named in guest claims, and that cost is not captured in a take rate. Peerspace's timing suggests a single claim can dominate a small company's balance sheet. This rests on one case.
- [inference] Insurance for hosted premises is a plausible cost line for every space platform, but no insurance figure was found for any of them.

### Gaps
- No claim frequency, insurance loss ratio, or trust-and-safety cost as a share of revenue for any space platform.
- The outcome of the injury suit and any plan confirmation was not found as of October 2026.
- No founder or investor commentary on the Peerspace filing was found. The only commentary located is a jobs-listing site claiming creditor rejection would end the business; treat as low reliability.

## 7. Venture funding cycle effects

### Takeaway
Only anecdotal funding data surfaced. Capital-heavy space and "Airbnb for X" operators (Breather, Zeus Living, Wimdu) failed or shrank; capital-light platforms (ResortPass, SpotHero) raised and in SpotHero's case exited. The 2015-2019 wave, 2021 boom, and 2022-2025 funding crunch are not quantified here.

### Cited Findings
- Breather: 17% layoff in December 2019; Moelis engaged to find a sale or capital with little interest; closure of 400+ sites in December 2020 — [Commercial Observer](https://commercialobserver.com/2020/12/breather-flex-space-closing-covid/); [Bisnow](https://bisnow.com/national/news/coworking/breather-closes-400-locations-lays-off-employees-online-only-107142)
- Splacer: $1.4M seed round reported July 2015 by an Israeli business outlet (Hebrew) [single-source] — [Calcalist](https://www.calcalist.co.il/articles/0,7340,L-3663331,00.html)
- ResortPass: $26M Series B co-led by Declaration Partners and 14W, with CRV participating; total funding $37M per Skift; company described as six years old, suggesting roughly 2022 [date inferred from company age; not verified] — [Skift](https://skift.com/?p=542446); an earlier round of $8.7M per an SEC filing, with PitchBook lifetime funding of $12.7M — [LA Business Journal](https://labusinessjournal.com/manufacturing/selling-poolside-staycations-resortpass-raises-nea/)
- Swimply: a $10M raise reported (date not found) [unverified] — [Startup Savant](https://www.startupsavant.com/news/swimply-scoops-10-mil)
- Zeus Living (adjacent, furnished corporate housing, Airbnb-backed): reported $150M raised; reported winding down, with one blog citing November 2022 and missed vendor payments [single-source blog] — [The Information headline](https://www.theinformation.com/articles/airbnb-backed-real-estate-startup-zeus-living-to-shut-down); [Tactyqal](https://tactyqal.com/blog/why-zeus-living-is-shutting-down-after-raising-150m/)
- Wimdu (adjacent, Rocket Internet's Airbnb clone, not space-sharing): announced in September 2018 it would shut down "facing significant business challenges"; reported to have raised ~$90M — [TechCrunch, 2018-09-27](https://techcrunch.com/2018/09/27/wimdu-rocket-internets-airbnb-clone-to-shut-down-this-year-facing-significant-business-challenges/)

### Inferences
- [inference] Failures with the most visible capital burn in the set were lease-based or property-heavy (Breather, Zeus Living, Wimdu). Those cost structures are different from a commission-only marketplace.
- [inference] The 2020 shock is the largest documented driver for Breather (the company blamed COVID); it does not explain Peerspace (2026) or the Splacer outcome, which is unknown.

### Gaps
- No funding totals or time series for the 2015-2019, 2021, or 2022-2025 periods for US space marketplaces.
- Shutdown dates for Splacer, Spacious, and Codi were not found.
- Investor commentary on the funding cycle (a16z, NFX, Point Nine, Benchmark) was not searched.

## 8. What winning models did differently

### Takeaway
Among the companies covered, the apparent winners share one or more features: a standardized, high-intent SKU (parking, day pass), institutional customers with recurring demand (Facilitron), or free software with a transaction fee. Fever and Tripleseat/Toast were not researched, so their contrast cannot be sourced here.

### Cited Findings
- SpotHero: commission-based (~15% in the 2017-era case); $1B in parking reservations sold by 2022; Uber acquisition reported April 2026 [single-source, unverified] — [Harvard D3](https://d3.harvard.edu/platform-digit/submission/spothero-kicks-parking-frustrations-to-the-curb/index.html); [SpotHero press](https://spothero.com/press/spothero-eclipses-1-billion-in-parking-reservations-sold); [Altss](https://altss.com/profile/spothero-inc)
- ResortPass: standardized day pass (~$250 average reservation per 2019 release); hotels as supply; $26M Series B (~2022) — [Hospitality Net](https://www.hospitalitynet.org/news/4096098/resortpass-sees-record-growth-fueled-by-experience-economy-and-redefines-guest-revenue-opportunities-for-hotels-resorts); [Skift](https://skift.com/?p=542446)
- Facilitron: pay-as-you-go fee on paid rentals; institutional customers (public agencies); no published fee — [FitGap](https://us.fitgap.com/products/036750/facilitron); [Software Advice](https://www.softwareadvice.com/cafm/facilitron-profile)
- Swimply: 15-20% host and guest fees (sources conflict); revenue range $10M-$50M (Dealroom) — [Dealroom](https://dealroom.co/companies/swimply/)

### Inferences
- [inference] Winners reduced the buyer's decision to a standard product with a clear price and time window (a parking slot, a day pass). Peerspace and Splacer sold open-ended "space," which requires the buyer to evaluate each listing.
- [inference] Facilitron's and SpotHero's models avoid asking owners to pay for demand they could get themselves, a point that bears directly on the take-rate question in Section 4.
- [inference] Whether owners can "earn without being present" is not verified for any winner in this set.

### Gaps
- Fever (events marketplace, ticketing) and Tripleseat/Toast (venue SaaS) were not searched. Their economics and funding are not covered.
- No evidence on how standardized SKUs affect repeat rates, because no repeat data was found (see Section 1).

## 9. Investor and expert commentary

### Takeaway
Tavel's and Gurley's frameworks were located only through secondary summaries; the Tavel Medium page returned only a bio and an introductory fragment. No investor commentary specific to "Airbnb for space" failures, or to Peerspace's 2026 filing, was found. a16z, NFX, Li Jin, Andrew Chen, Lenny Rachitsky, Point Nine, and First Round were not searched.

### Cited Findings
- Sarah Tavel (Benchmark GP; formerly Pinterest product), "Hierarchy of Marketplaces" (Medium series; intro and Level 1 retrieved): stage one is a small, constrained market where you make both sides so much happier that the market tips to you; the satisfied share of volume is "Happy GMV"; stage two is reinforcing feedback loops; stage three is expansion after winning the home market; a summary attributes to her that finishing second in a marketplace often proves fatal — [Tavel Medium](https://sarahtavel.medium.com/the-hierarchy-of-marketplaces-introduction-and-level-1-983995aa218e); [Learn Your Keep summary](https://learnyourkeep.substack.com/p/the-hierarchy-of-marketplaces) [quotes and later levels from secondary summaries; not verified against the full text]
- A skill-directory summary claims DoorDash entered low-competition suburbs while Postmates spread too thin to tip any market [unverified; not cited as fact]
- Bill Gurley (Benchmark), 2013 essay on take rates ("the rake"): secondary summaries report the eBay figure and a range of take rates from OpenTable to Shutterstock, and his view that a long-run winner-take-all marketplace should minimize friction in product and pricing — [KJ Labuz](https://kjlabuz.substack.com/p/takerates); [Rohit Nuwal](https://rohitnuwal.substack.com/p/take-rates) [primary essay not opened]
- Peerspace 2026: the only commentary found is a jobs-listing site stating that creditor rejection of a plan would end the business — [Simplify](https://simplify.jobs/c/Peerspace) [low reliability; commentary, not docket information]

### Inferences
- [inference] Tavel's stage-one logic implies a space platform must dominate one use case in one metro before expanding. Several space platforms spread across meetings, offices, events, and shoots at once, which is the pattern the framework warns against.

### Gaps
- Not searched: Li Jin and a16z Marketplace 100; Andrew Chen on cold start; NFX marketplace essays; Lenny Rachitsky on marketplaces; Point Nine; First Round; Reforge.
- Gurley's primary take-rate essay and Tavel's full series were not opened.
- No founder post-mortems (Medium, Substack, podcasts) about space-sharing companies were found.

## 10. Failed space-sharing companies: what the record shows

### Takeaway
Documented failures in the set are few and heterogeneous. Breather (flex-office operator, closed 2020) is documented; Peerspace (Chapter 11, 2026) is documented in part; Splacer, Spacious, and Codi have no found closure or post-mortem. No source found gives a clean marketplace-economics post-mortem for any of them, so the question "why no US company won" cannot be answered directly from this evidence.

### Cited Findings
- Breather: operator and lease model; pre-COVID layoffs (December 2019); closure of 400+ sites (December 2020); reported online-only continuation, status disputed — [Commercial Observer](https://commercialobserver.com/2020/12/breather-flex-space-closing-covid/); [Bisnow](https://bisnow.com/national/news/coworking/breather-closes-400-locations-lays-off-employees-online-only-107142); [CRETECH](https://discover.cretech.com/news/breather-bloodbath-flex-office-startup-fires-at-least-10-of-staff)
- Peerspace: Chapter 11 Subchapter V (2026-08-30), tied to a premises-liability suit — see Section 6 — [WhatNow](https://whatnow.com/news/trending/san-francisco-venue-rental-marketplace-with-45000-spaces-files-for-chapter-11-bankruptcy/)
- Splacer: launched Tel Aviv 2014, New York 2015, later Chicago and other cities; the newest coverage (March 2017) says nothing about closure — [DNAinfo](https://www.dnainfo.com/new-york/20170301/williamsburg/splacer-venues-events-rental); [REjournals](https://rejournals.com/two-israeli-architects-bring-airbnb-style-event-space-service-to-chicago/)
- Zeus Living and Wimdu (adjacent, not space-sharing): see Section 7
- Stayzilla (adjacent, India, not US): founders arrested for financial fraud in 2017 per a search summary; not verified [unverified; not US]

### Inferences
- [inference] Failures cluster into (a) lease-based or capital-heavy models with fixed costs (Breather, Zeus Living), (b) liability tail risk (Peerspace), and (c) unknown outcomes (Splacer, Spacious, Codi). Only (a) and (b) are documented here, and neither is a pure commission-marketplace failure.

### Gaps
- No Spacious, Codi, or Splacer shutdown details or post-mortems found.
- No founder post-mortems for any US space-sharing company located.
- The Peerspace case outcome and the reasons for filing beyond the litigation trigger are unverified as of October 2026.

## Summary of unanswered key questions (for the report writer)

- Repeat rates, booking frequency, and cohort retention for any US space marketplace: no data found.
- Off-platform leakage rates and anti-leakage countermeasures: no data found.
- CAC and LTV for low-frequency marketplaces: no data found.
- Take rates for Airbnb, Etsy, Turo, Peerspace, and current SpotHero: not searched.
- Owner-side economics, cold start, and liquidity thresholds: no data found.
- Insurance and trust-and-safety costs as a share of revenue: no data found beyond the Peerspace case.
- Venture funding totals for 2015-2019, 2021, and 2022-2025: not found.
- Fever and Tripleseat/Toast economics: not searched.
- Investor commentary (a16z Marketplace 100, Li Jin, NFX, Lenny, Point Nine, Reforge) and founder post-mortems: not searched.
- Peerspace injury-suit outcome and any plan confirmation: not found as of October 2026.

Single most-supported findings: (1) Peerspace filed Chapter 11 on 2026-08-30 with reported litigation trigger (single-source reporting plus docket aggregators); (2) AI Overviews are associated with large CTR declines on informational queries from mid-2024 to December 2025 (vendor studies; correlational; no space-marketplace data); (3) commission rates of ~15% recur across SpotHero, Splacer, and Swimply reporting, though Swimply's disclosures conflict.
