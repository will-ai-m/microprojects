# Can we crawl Yelp + Google reviews and rank a restaurant's dishes?

**Date:** 2026-09-06 · **Status:** research complete, nothing built yet
**Question:** crawl Yelp and Google reviews for one restaurant, show the most popular dishes.

---

## 1. Bottom line

The hard part is not extracting dishes from review text. That is a solved,
cheap, ~50-line problem. **The hard part is getting the review text at all.**

Both official APIs are structurally unable to support this product, and this is
the single finding that shapes everything else:

| Source | Reviews per business | Text you get | Verdict |
|---|---|---|---|
| Yelp Fusion `/v3/businesses/{id}/reviews` | **3** (Plus tier), 7 (Enterprise) | **~160-char excerpt**, truncated | Unusable |
| Google Places API (New), `reviews` field | **5**, no pagination, no sort | Full text | Unusable |

Eight truncated reviews cannot rank dishes. You need 200+ to see a dish
mentioned enough times for a count to mean anything. So the real decision is
**which non-API path you take to get review text**, and that decision is mostly
a legal/risk decision, not a technical one.

Second finding worth knowing before you build anything: **Yelp already computes
exactly this feature and sells it.** See §5.

---

## 2. Why the official APIs are dead ends

### Yelp Fusion

The reviews endpoint returns *three review excerpts of roughly 160 characters
each*, chosen by Yelp, in Yelp's own sort order. This is a hard cap, not a
parameter. It has been the documented behavior for years and Yelp's own FAQ
states the API "does not return full review text" and "cannot be configured to
return alternative or hand-picked review excerpts."

- Docs: [Reviews endpoint](https://docs.developer.yelp.com/reference/v3_business_reviews) · [Places FAQ](https://docs.developer.yelp.com/docs/places-faq)
- Long-standing developer complaints: [yelp-fusion#163](https://github.com/Yelp/yelp-fusion/issues/163), [yelp-fusion#466](https://github.com/Yelp/yelp-fusion/issues/466)

Pricing is not the obstacle — roughly $8–15 per 1,000 calls with a 30-day free
trial. The obstacle is that **the data is not there at any price on this tier**.

Yelp's terms also add two restrictions that bite this specific project:
- Cached Yelp content must be **refreshed or deleted within 24 hours** (business IDs excepted).
- The developer terms restrict **semantic analysis of reviews** and **training models on them** without written approval from Yelp.

That second point is not incidental. Counting dish mentions across review text
*is* semantic analysis of reviews. Building this on Fusion data without
approval runs against the agreement you clicked to get the key.

### Google Places API (New)

The `reviews` field returns **at most 5 reviews**, with no pagination, no
`pageToken`, and no sort parameter. Developers have asked since 2015; the
[public issue](https://issuetracker.google.com/issues/35825957) is still open.

Cost is also structured against you: Google bills each request at the **highest
tier of any field in the field mask**, and `reviews` sits in the top
**Enterprise + Atmosphere** tier at **$40 per 1,000 calls**. One `reviews` field
re-prices an otherwise-cheap call. Since March 2025 the pooled $200 credit is
gone, replaced by per-SKU monthly free caps — **1,000 calls/month** at the
Enterprise tier.

So: $40 per 1,000 calls, 5 reviews each, and you cannot ask for review 6.

Google's Maps Platform terms allow caching place content for **30 days**, require
attribution, and prohibit scraping Maps.

### What each API *does* offer that is tempting

Google now returns AI review summaries (`reviewSummary` / `generativeSummary`,
Gemini-generated free text). It is prose about the restaurant, not a structured
dish list with counts, so it cannot be ranked or aggregated. Useful as a
cross-check, not as the product.

---

## 3. Yelp already built this feature — and sells it

Yelp's **Food & Drinks Insights** endpoint
([docs](https://docs.developer.yelp.com/reference/v3_get_business_food_and_drinks_insights))
returns, per location, the dishes and drinks offered with **popularity and
frequency of mention in reviews**, derived from menu data plus Yelp's own AI.

That is, almost exactly, the product described in this request — already
computed, by the party with the full review corpus.

Two catches:
1. It is **Enterprise / Yelp Insights API only**, custom per-location pricing, sales contact required.
2. Yelp positions the Insights API for **"internal, non-public/back-end purposes"** — B2B analytics. So even with access, a public-facing dish ranking is outside its intended use.

The same is true of the "Popular Dishes" panel on a Yelp business page: it
exists, it is visible on the web page, and it is not in the public API.

**Why this matters for scoping:** if the goal is *"I personally want to know what
to order"*, Yelp's own page already answers it for free in a browser. The
project is only interesting if it does something Yelp's version does not —
merging Yelp **and** Google, showing sentiment rather than just frequency,
covering restaurants Yelp's feature skips, or ranking across many restaurants.
Worth deciding which before building.

---

## 4. The four ways to actually get review text

Ranked by how defensible they are, not by how easy.

### A. Yelp Open Dataset — free, full text, **development only**

Yelp publishes a static research dataset: **~7.0M reviews** across ~150k
businesses in 11 metros, with **complete review text** and star ratings. Roughly
4.4 GB compressed. Free, account required.
[Download](https://business.yelp.com/data/resources/open-dataset/)

The licence is **academic / non-commercial**. It cannot back a production
product, and it is a static snapshot, so it will never tell you about the
restaurant you are standing outside of.

What it *is* good for is decisive: it lets you build and validate the entire
dish-extraction pipeline against thousands of real restaurant reviews with zero
scraping, zero cost, and zero legal ambiguity. **Every extraction and ranking
decision in this project can be settled on this dataset before a single live
request is made.** That is the right place to start.

### B. Commercial review providers — the pragmatic production path

These companies scrape and resell, and they carry the operational burden
(proxies, fingerprinting, breakage). You buy review text by the thousand.

| Provider | Sources | Model | Rough cost | Notes |
|---|---|---|---|---|
| Apify (actor marketplace) | Google + Yelp | pay per result | cents per 100s of reviews | Cheapest entry, per-actor quality varies |
| Outscraper | Google (Yelp too) | pay as you go | ~$3 / 1,000 records | No subscription, simple API |
| SerpApi | Google Maps reviews | $25 / 1,000 searches | higher per review | Most stable API surface, ~250 free/month |
| DataForSEO | Google | async vs live tiers | ~$0.60–2 / 1,000 | Cheap async mode |
| Bright Data / Oxylabs | Both | subscription | $500+/month floors | Enterprise, compliance posture, overkill here |

For one restaurant at a few hundred reviews this is **well under a dollar**, and
often under ten cents. Cost is genuinely not the constraint.

**The caveat nobody advertises:** buying from a provider moves the scraping
risk, it does not delete it. Their terms generally push responsibility for
lawful use back onto you. You are still the one holding review text that Yelp's
terms say may not be cached beyond 24 hours.

### C. Google Business Profile API — clean, but only for the owner

If you own the restaurant, or partner with one, `accounts.locations.reviews`
returns **all** of that location's Google reviews with real pagination (~50 per
page), full text, free. OAuth as the verified owner.

This is the only path in this entire document that gives you complete review
text with unambiguous permission. It does not scale to "any restaurant I feel
like", but if the product is ever aimed at restaurant operators, this is the
front door.

### D. Rolling your own scraper — technically possible, strategically bad

Yelp sits behind Cloudflare bot management; Google Maps requires JS rendering
and runs proprietary in-house detection. Both use IP reputation, TLS/JA3
fingerprinting, canvas and behavioral signals. Datacenter IPs get roughly
30–70% success; residential proxies push it to 70–90% at $100–500/month.

That cost and maintenance load is precisely what providers in (B) are selling.
Building it yourself to save money is a bad trade for one developer, and the
failure mode is not a clean error — Cloudflare can serve deliberately poisoned
content to suspected scrapers, so you can silently rank dishes from fake text.

---

## 5. Extracting dishes: the part that actually works

Good news: this is a well-trodden problem and Yelp published how they did it.

### How Yelp built the real thing

Yelp's engineering blog, *Discovering Popular Dishes with Deep Learning* (Oct
2019), describes the production approach:

- Treat it as **token-level sequence tagging** with a **BIESO** scheme (Begin / Inside / End / Single / Outside) so multi-word dish names come out as spans.
- **Bootstrap gold labels from menu data** — the menu tells you what the dish names are, so you can auto-label reviews without hand annotation.
- Rank by **mention frequency**.

And the limitation Yelp itself concedes: **there is no sentiment weighting**.
"Avoid the appetizer platter, it was cold and stale" increments the appetizer
platter's popularity. The shipped feature at Yelp measures *talked about*, not
*liked*. That is a real opening — see §6.

### The three approaches, and which to pick

**1. Menu-anchored fuzzy matching — highest precision, needs a menu.**
Get the restaurant's menu, then match review text against it with
`rapidfuzz.fuzz.token_set_ratio` around 85. Cannot hallucinate a dish that
isn't on the menu, which is its whole appeal. Fails on off-menu names and
specials, and requires you to have the menu — itself a scraping problem.

**2. LLM open extraction — works everywhere, small hallucination risk.**
Batch 15–20 reviews per call, ask for structured JSON of
`(dish, sentiment, quote)`. Recent work puts generative LLM aspect extraction
at **F1 ≈ 0.91**, comfortably above the 0.85–0.90 that fine-tuned BERT-class
models reach on the SemEval-2016 restaurant benchmark. Hallucinations mostly
wash out because a fabricated dish appears once and never clears a mention
threshold.

**3. Classical NLP — spaCy noun chunks, YAKE, KeyBERT, TF-IDF.**
No API cost, but it surfaces "the food", "the service", "great portions" and
needs heavy filtering. There are food NER models on HuggingFace
(FoodBaseBERT-NER, InstaFoodRoBERTa-NER) but they target ingredients and food
entities generally, not restaurant dish names, and generalization is unproven.

**Recommendation: LLM extraction as the primary path, menu-anchored matching as
a precision boost when a menu is available.** The menu is the harder input to
obtain, so it should not be a hard dependency.

### Canonicalization is the step people underestimate

"birria taco", "birria tacos", "the birria", "birria" must collapse to one
entity or every count is wrong. Normalize and lemmatize, embed with
`all-MiniLM-L6-v2`, then agglomerative clustering with a distance threshold
around 0.25 and take a cluster representative. This catches "fries" ≈ "fried
potatoes" without hand-written rules. An LLM pass can adjudicate the ambiguous
clusters.

Watch the failure mode in the other direction: embeddings will happily merge
"chicken tacos" and "steak tacos", which are different dishes. This threshold
needs to be tuned against labelled data, not guessed.

---

## 6. Ranking: "popular" is ambiguous, and that is the product decision

Yelp ranks by raw frequency and admits it. You can do better cheaply, because
the LLM extraction pass can return sentiment per mention at no extra call.

Four defensible definitions of "most popular", which give different answers:

1. **Most mentioned** — raw count. Yelp's definition. Rewards controversy.
2. **Most loved** — count of positive mentions only. Usually what a diner means by "what should I order".
3. **Most distinctive** — mention rate here versus a background corpus of all restaurant reviews. Surfaces the thing this place is known for rather than the thing every restaurant serves.
4. **Recency-weighted** — decays old mentions. Catches menu changes and chef turnover, at the cost of noise.

**Pick one as the headline and show the others.** I would make *most loved* the
headline and expose the count so a user can see that a dish is both frequent
and well-liked.

One caution, given how this repo treats numbers: a composite score with
hand-tuned weights (`+ frequency*10 - negative*30 ...`) invents precision it
has not earned. Report the components. If a composite is needed for
glanceability, derive its weights against a labelled sample rather than
choosing them.

---

## 7. Legal reality

*Not legal advice — this is a summary of published terms and case law.*

**What the terms say.** Both platforms prohibit scraping outright. Yelp caps
caching of review content at **24 hours** and requires attribution; its
developer terms additionally restrict **semantic analysis of reviews** and
**model training** on them without written approval. Google allows **30-day**
caching of place data (place IDs indefinitely), requires attribution, and
forbids scraping Maps.

**What the case law says.** The picture is more settled than most blog posts
suggest, and the headline is that the criminal statute is not the risk:

- **Van Buren v. United States** (SCOTUS 2021) narrowed the Computer Fraud and Abuse Act. Violating terms of service is not, by itself, "unauthorized access".
- **hiQ Labs v. LinkedIn** (9th Cir. 2022) — hiQ **won** the CFAA question for public data, then **lost on breach of contract** and settled. This is the case to internalize: scraping public pages is usually not a crime, and is still a contract violation you can lose on.
- **Meta v. Bright Data** (N.D. Cal. 2024) — Bright Data prevailed on claims about scraping public pages without logging in. Narrow, and does not override another platform's terms.
- **Facebook v. Power Ventures** (9th Cir. 2016) — continuing after a cease-and-desist crosses into CFAA liability. This is the bright line: **if you are told to stop, stop.**
- **Feist** (SCOTUS 1991) — facts are not copyrightable. **A dish name and a count are facts.** The review text you extracted them from is expressive and is protected.

That last point is the most useful thing in this section for shaping the build.

**Enforcement reality.** Neither company is suing hobbyists; they block them
technically. Enforcement attention goes to commercial competitors and data
brokers. Small scale is not immunity, but the realistic worst case for a
personal tool is an IP ban, not a lawsuit.

**The design consequence.** Store **dish names, counts, and sentiment. Discard
review text and author identity after extraction.** This is not a formality:

- It keeps you on the facts side of the Feist line rather than redistributing protected expression.
- It naturally satisfies Yelp's 24-hour caching rule, since you are not retaining the content at all.
- It removes reviewer names, which are personal data under GDPR and CCPA, from your system entirely.

A pipeline that reduces reviews to `{dish, count, sentiment}` and throws the
text away is dramatically more defensible than one that keeps a review corpus,
and it loses nothing the product needs.

**Where the lines fall:**

| Approach | Exposure |
|---|---|
| Official APIs within terms | Clean, but cannot deliver the product (§2) |
| Yelp Open Dataset for development | Clean for non-commercial work; not for production |
| Owner-authorized Google Business Profile | Clean, limited to locations you have rights to |
| Provider-sourced text, discard after extraction, personal use | Grey, low realistic risk |
| Public product, at-scale scraping, republished review text | Materially riskier — hiQ's losing side |

A private tool you run for restaurants you are choosing between is a different
risk posture from a public site, and the difference is large. Scope accordingly.

---

## 8. What it costs

**Extraction is nearly free.** For one restaurant at 400 reviews averaging 80
words, batching 20 reviews per call:

| | calls | input tokens | output tokens |
|---|---|---|---|
| One restaurant | 20 | 50,200 | 12,000 |

| Model | Per restaurant | With Batch API (50% off) | 100 restaurants |
|---|---|---|---|
| Haiku 4.5 | $0.110 | $0.055 | $11.02 |
| Sonnet 5 | $0.220 | $0.110 | $22.04 |
| Opus 5 | $0.551 | $0.275 | $55.10 |

Roughly **a nickel to a dime per restaurant** on Haiku. Extraction is a
classification-shaped task, so Haiku is the right default; spot-check a sample
against Sonnet rather than paying for the upgrade everywhere.

**Data acquisition costs about the same or less** — well under a dollar per
restaurant from a provider. So the entire per-restaurant cost is somewhere
around **10–50 cents**, and the total cost of a working prototype is dominated
by nothing at all. No part of this project is gated on budget.

Note this repo already has a precedent worth reusing: `yc-rfs` runs its LLM
classification as **parallel Haiku subagents** rather than through the Anthropic
SDK, because no API key is configured here. The same trick applies to dish
extraction and makes the API cost above $0.

---

## 9. Recommended build

The sequencing matters more than the components, because it front-loads the
part that can be validated for free and defers the part that carries risk.

**Step 1 — Build and validate the whole extractor offline.**
Pull the Yelp Open Dataset. Pick 20 restaurants with 200+ reviews each. Build
extraction, canonicalization, and ranking against them. Hand-label the dishes
for 3–5 of those restaurants and measure precision and recall of the extractor
against your own labels. This costs nothing, touches no live service, and
answers the only question that matters: *does the dish list look right to a
human who read the reviews?*

Nothing else should be built until this is measured. This mirrors how `yc-rfs`
handles its classifier, and the reason is the same — every number downstream
inherits the extractor's error rate, so quantify it first.

**Step 2 — Decide the sourcing path deliberately.**
- Personal tool for restaurants you're choosing between → a provider like Outscraper or Apify, a few cents per restaurant.
- Aimed at restaurant operators → Google Business Profile API, clean and free.
- Public product → the honest answer is that no cheap path is clearly compliant; this is where the risk actually lives (§7).

**Step 3 — Store facts, not text.** Reviews come in, `{dish, count, sentiment,
first_seen}` goes to disk, text is discarded in the same pass. This is the §7
design consequence and it should be structural, not a cleanup step.

**Step 4 — Ship the narrow thing.** One restaurant in, ranked dish list out,
static HTML like `yc-rfs/dashboard/`. Show mention count and positive share
side by side and let the user see both.

**Suggested stack:** Python, `rapidfuzz` for menu matching,
`sentence-transformers` (`all-MiniLM-L6-v2`) plus scikit-learn
`AgglomerativeClustering` for canonicalization, Haiku for extraction and
per-mention sentiment, numbered pipeline stages reading and writing files so
each can re-run in isolation.

**Proposed layout**

```
popular-dishes/
  data/raw/           # provider pulls / open-dataset slice (gitignored)
  data/derived/       # dishes.jsonl {dish, count, pos, neg}, dashboard.json
  pipeline/
    01_fetch_reviews.py       # provider adapter; Open Dataset adapter for dev
    02_extract_mentions.py    # batched LLM -> (dish, sentiment, quote)
    03_canonicalize.py        # normalize + embed + cluster
    04_rank.py                # the four rankings from §6
    05_build_dashboard.py
  validation/         # hand-labelled dish lists + agreement score
  dashboard/index.html
```

---

## 10. Open questions worth settling before writing code

1. **What does this do that Yelp's own Popular Dishes panel doesn't?** (§3) Merging Google with Yelp, and ranking by *loved* rather than *mentioned*, are both real answers. Worth picking one deliberately.
2. **Private tool or public site?** This is the single biggest determinant of legal exposure and it changes the sourcing decision (§7).
3. **Which "popular"?** (§6) Headline ranking is a product decision, not a technical one.
4. **How good is good enough?** Set the precision bar before measuring, so the validation in Step 1 has something to pass or fail against.

---

## Confidence and caveats

- **High confidence:** Yelp's 3-excerpt/160-char cap and Google's 5-review cap. Both independently corroborated across multiple sources and long-standing developer issue threads.
- **High confidence:** Google's `reviews` field re-pricing calls to the Enterprise + Atmosphere tier at $40/1,000, and the March 2025 shift from the pooled $200 credit to per-SKU free caps.
- **Medium confidence:** exact Yelp Fusion tier pricing and current trial terms. Yelp restructured its plans and the old free tier is gone; treat the $8–15/1,000 figures as indicative and confirm on signup.
- **Medium confidence:** third-party provider pricing. It moves, and several providers changed pricing during 2026. Confirm before committing.
- **Lower confidence:** provider success rates against Cloudflare and Google's bot detection. These are vendor-reported or benchmark numbers and they change continuously.
- **Not verified directly:** `developers.google.com`, `docs.developer.yelp.com`, and Yelp's engineering blog are all blocked by this environment's network policy. Their content here comes from search results and secondary sources rather than fetched pages. The primary-source claims above should be re-checked from an unrestricted network before any of them is load-bearing for a purchase.
