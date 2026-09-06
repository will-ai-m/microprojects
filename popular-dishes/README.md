# Popular dishes from restaurant reviews

Can we crawl Yelp and Google reviews for a restaurant and show its most popular
dishes? **Research phase — nothing built yet.**

Read [RESEARCH.md](RESEARCH.md) for the full findings.

## The short version

**Extracting dishes from review text is the easy part.** It costs about a nickel
per restaurant with Haiku, the technique is published, and Yelp's own
engineering blog describes how they built the production version.

**Getting the review text is the hard part, and both official APIs are dead ends:**

| Source | Reviews per business | Text |
|---|---|---|
| Yelp Fusion reviews endpoint | 3 | ~160-char excerpt, truncated |
| Google Places API (New) | 5, no pagination | full |

Eight truncated reviews cannot rank dishes. Everything interesting about this
project follows from that constraint.

**Yelp already sells this exact feature.** Its Food & Drinks Insights endpoint
returns dishes ranked by frequency of mention in reviews — enterprise-only,
custom pricing, and licensed for internal analytics rather than public display.
Worth deciding what this project does that Yelp's version doesn't before
building.

## Where to start

Build the extractor against the **Yelp Open Dataset** (7M full-text reviews,
free, academic licence). It settles every extraction and ranking question with
no scraping, no cost, and no legal ambiguity. Only then pick a live data path.

Store `{dish, count, sentiment}` and discard review text after extraction. Dish
names and counts are facts; review text is protected expression. That one design
choice does most of the compliance work.
