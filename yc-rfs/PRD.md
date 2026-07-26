# PRD: YC RFS Alignment & Outcomes Dashboard

**Status:** v5 — rebuilt on a sharpened catalog with reliability measurement 2026-07-26. §11 results · §12 build changes · §13 reliability engineering.
**Owner:** Will
**Location:** `microprojects/yc-rfs/`
**Last updated:** 2026-07-25

---

## 1. Problem statement

Since Summer 2024, Y Combinator publishes a "Requests for Startups" (RFS) list for each batch (~13 themes per batch, 8 batches to date: S24 → F26). Two questions:

1. **Alignment (Q1):** How strongly do the companies YC actually admits correlate with the themes YC says it wants?
2. **Outcomes (Q2):** Do admitted companies that match an RFS theme perform better than batchmates that don't?

Deliverable: an **interactive dashboard** backed by a reproducible pipeline, re-runnable as new batches land.

## 2. Scope decisions (settled)

| Decision | Choice |
|---|---|
| RFS eras | Modern per-batch RFS only (S24–F26). Historical 2014/2018/2023 RFS out of scope. |
| Company↔theme matching | LLM classification of company descriptions against RFS theme texts |
| Q1 design | Both: share-of-batch alignment AND before/after admission-share shift per theme, against a pre-RFS baseline (W22–W24) plus within-era contrast |
| Deliverable | Interactive dashboard: repo-local static HTML + precomputed JSON, no server |
| `Acquired` status | Counts as a **positive** outcome in Q2 |
| Composite weights | Survival 41 / stage=Growth 29 / relative team size 24 / isHiring 6 (`top_company` dropped — see §13) |

## 3. Known limitations (accepted up front)

These are inherent to the scope, not fixable by more engineering:

- **Q2 measures early trajectory, not success.** The oldest RFS-era batch (S24) is ~2 years old: 95% of its companies are `Active`/`Early`. Outcome signal is limited to survival (not `Inactive`), `stage=Growth`, relative team size, `top_company`, and `isHiring`. Framed honestly, Q2 = "do RFS-matchers show stronger early traction than their batchmates?"
- **"Years active" is cohort age, not a success input.** Within S24–F26, years active is determined almost entirely by which batch you're in. It's used as the *normalizer* (all comparisons are within-batch), not as a component of the success score. This deviates from the original sketch (stage + status + years active) — deliberately.
- **We observe admits, not applicants.** Alignment between RFS and admitted companies conflates (a) YC selecting for RFS themes, (b) founders responding to RFS by applying, and (c) RFS describing trends already in the pipeline. The before/after shift analysis narrows this but cannot separate the three. All findings are descriptive, not causal.
- **Launched companies only.** The yc-oss dataset covers publicly launched companies (~6,080). Stealth/unlaunched companies in recent batches are invisible, which undercounts recent batches and may bias theme mix.
- **No funding/valuation data.** The dataset has no revenue, funding, or valuation. Success proxies are limited to the fields listed above.

## 4. Data sources

### 4.1 yc-oss API (`https://github.com/yc-oss/api`)
- `companies/all.json` — 6,080 launched companies, refreshed daily from YC's Algolia index.
- Fields used: `id`, `name`, `batch`, `one_liner`, `long_description`, `industry`, `subindustry`, `tags`, `status` (Active/Acquired/Public/Inactive), `stage` (Early/Growth), `team_size`, `launched_at`, `top_company`, `isHiring`, `website`, `url`.
- Snapshot raw JSON into `data/raw/` with fetch date; pipeline runs against the snapshot for reproducibility.

### 4.2 YC RFS page (`https://www.ycombinator.com/rfs`)
- 8 batch tabs (S24, W25, Sp25, Su25, F25, Sp26, Su26, F26), ~13 themes each: title + full description text.
- **Acquisition note:** only the current batch's themes are server-rendered; past tabs load client-side. Plan: extract via browser automation or the page's underlying JSON payload; fallback: Wayback Machine snapshots of the page taken during each batch's application window.
- Store per-batch theme texts in `data/raw/rfs/<batch>.json`, checked into the repo (small, stable, human-reviewable).

### 4.3 Batch windows
- **RFS-era batches (treated):** S24 → the most recent batch with a meaningful number of launched companies.
- **Baseline batches (pre-RFS):** W22, S22, W23, S23, W24 (1,375 launched companies). Every shift is additionally computed against the shorter W23–W24 window, which sits entirely after ChatGPT's launch; both are shown in the dashboard.

## 5. Method

### 5.1 Theme canonicalization
Themes recur across batches with reworded titles (e.g., defense, elder care, stablecoins appear repeatedly). Raw inventory is ~104 (batch, theme) pairs.

- LLM-assisted clustering of the ~104 pairs into **canonical themes**, each with: canonical name, merged description, and the set of batches where it was active.
- Output is a small human-reviewed table (`data/derived/themes.json`) checked into the repo — this is the one step with a manual review gate, because everything downstream keys off it.

### 5.2 Company ↔ theme classification
- For each company in scope (RFS-era **and** baseline batches — baseline companies must be classified too, so pre-RFS theme shares are computable), **one LLM call per company** with the full canonical-theme catalog in the prompt; returns the list of matching theme IDs with `strong | partial` confidence and a one-line rationale.
- Input per company: `one_liner`, `long_description`, `tags`, `industry`.
- Model: `claude-haiku-4-5` (narrow classification task). Estimated volume: ~3,000–4,000 companies × 1 call — trivial cost.
- **Caching:** implemented in `pipeline/cache.py`, keyed on `(company payload, prompt version, model, catalog hash)`; re-runs only classify genuinely changed inputs.
- **Validation:** hand-label ~100 (company, theme) pairs stratified across themes; report precision/recall of the classifier against them; iterate the prompt until agreement ≥ 0.85. Validation set and score ship with the repo.
- Headline metrics use **strong** matches; **strong+partial** reported as a sensitivity band.

### 5.3 Q1 — Alignment analyses
1. **Share-of-batch:** for each RFS-era batch B: % of B's companies matching ≥1 theme from B's own RFS; plus per-theme company counts. Also a batch × theme heatmap.
2. **Before/after shift:** for each canonical theme, the primary contrast is admission share in RFS-era batches where the theme was active vs. the pre-RFS baseline (W22–W24), with difference/ratio and bootstrap confidence intervals. Secondary contrast: within-era batches where the theme was *not* listed (themes rotate in and out across the 8 RFS batches). Plot each theme's admission share as a time series across all batches (W22 → present) with markers for the batches where it appeared in the RFS — the trend view is what distinguishes "RFS moved admissions" from "RFS chased an existing trend."

### 5.4 Q2 — Outcome analyses
All comparisons are **within-batch** (matcher vs. non-matcher batchmates), then aggregated across batches with batch-size weights.

Report raw components separately (these are the honest numbers):
- Survival rate (`status != Inactive`; `Acquired` and `Public` count as **positive**)
- % `stage = Growth`
- Median `team_size` relative to batch median
- % `isHiring`
- Status breakdown (Active/Acquired/Public/Inactive) still shown per group so acquisitions remain visible as their own slice.

Plus one **composite early-traction score** (0–100) for the dashboard headline: **survival 41, stage=Growth 29, relative team size 24, isHiring 6**. (`top_company` was in the original weighting but is true for 0 companies in scope; it was dropped and the remaining weights renormalized — §13.) The composite exists for glanceability; every view links back to components.

Cut the comparison two ways: matcher of *own batch's* RFS, and matcher of *any* RFS-era theme.

### 5.5 Statistical care
- Wilson/bootstrap intervals on all shares; batch sizes are small (~250), theme-level Ns will be tiny (often < 20) — the dashboard must show Ns and suppress/grey out cells below a floor (e.g., N < 5).
- No cross-batch pooling of outcome rates without within-batch normalization.

## 6. Deliverable: dashboard

Static single-page HTML reading precomputed `data/dashboard.json`. No server, no live API calls. Views:

1. **Overview** — headline stats: overall alignment % per batch, biggest before/after shifts, matcher vs. non-matcher traction deltas.
2. **Theme explorer** — select a canonical theme → active batches, admission-share time series with RFS-introduction marker, matched company list (linked to YC pages), outcome comparison.
3. **Batch view** — select a batch → that batch's RFS themes with per-theme alignment and company lists.
4. **Methodology** — caveats from §3, classifier validation score, Ns everywhere.

Hosting: repo-local static file, opened directly in the browser. No publishing step.

## 7. Pipeline & repo layout

```
yc-rfs/
  PRD.md
  data/
    raw/            # yc-oss snapshot, rfs/<batch>.json
    derived/        # themes.json, classifications.jsonl, metrics.json, dashboard.json
  pipeline/
    01_fetch_companies.py
    02_fetch_rfs.py          # browser-assisted, run rarely
    03_canonicalize_themes.py # LLM-assisted, human-reviewed output
    04_classify.py            # Haiku batch classification, cached
    05_metrics.py             # Q1 + Q2 computations
    06_build_dashboard.py     # emits dashboard.json + index.html
  dashboard/
    index.html
  validation/
    labels.csv               # hand-labeled pairs
```

Python, no framework; LLM calls via Anthropic SDK. Every stage reads/writes files so any stage can be re-run in isolation.

## 8. Non-goals

- Causal claims about YC selection behavior
- Historical RFS eras (2014/2018/2023)
- Funding, valuation, or revenue data
- Application-pool analysis (data doesn't exist publicly)
- Live-updating dashboard (re-run pipeline to refresh)

## 9. Resolved questions

1. **Acquired:** counts as a positive outcome (in survival and the composite). Status breakdown still displayed so acquisitions are visible as a distinct slice.
2. **Dashboard hosting:** repo-local static HTML only.
3. **Composite score weights:** approved as survival 35 / Growth 25 / team 20 / top_company 15 / hiring 5; later renormalized to 41 / 29 / 24 / 6 after `top_company` proved dead in this window (§13).
4. **Baseline window:** W22–W24 (five batches: W22, S22, W23, S23, W24) as the pre-RFS baseline, with a W23–W24 sensitivity check. Within-era contrast retained as a secondary view (§5.3).

## 10. Milestones

1. **M1 — Data in hand:** company snapshot + all 8 batches' RFS texts extracted and reviewed.
2. **M2 — Themes canonicalized:** `themes.json` reviewed and frozen.
3. **M3 — Classifier validated:** ≥0.85 agreement on hand-labeled set; full classification run cached.
4. **M4 — Metrics:** Q1 + Q2 tables computed with intervals.
5. **M5 — Dashboard:** all four views working against `dashboard.json`.

## 11. Results (v3 — sharpened catalog, rationales collected)

Scope: 2,872 companies (1,375 baseline W22–W24, 1,497 RFS-era S24–Su26); 96 published RFS entries clustered into 48 canonical themes.

> **Reliability floor — read first.** 372 companies were classified twice by independent runs of the identical pipeline. They agree **69%** of the time on whether a company matches any theme at all, with a mean Jaccard overlap of **0.34** on which themes. Roughly a third of companies land differently on a re-run. Batch-level aggregates over ~1,200 companies survive this; single-theme shifts of a point or two do not. The 89% blind-validation figure below is measured on a stratified sample that oversamples clear-cut cases — it is the optimistic bound, not the typical one.

### Q1 — Do they admit what they ask for?
- **Own-RFS alignment: 24.1%** of RFS-era companies match ≥1 theme from their own batch's RFS. Range 11%–39% by batch. A minority of any batch reflects its RFS. **This is the one Q1 number worth quoting.**
- 7 of 37 tested themes show a shift surviving FDR correction and both baselines. But two independent diagnostics say the shifts are largely artefact:
  - **Vocabulary drift.** The raw era gap is +14.1pp overall, but only ~+3.7pp inside the fixed slice YC's own tags call AI-related, and smaller still among companies already using heavy AI language. Mean AI-keyword count per blurb rose ~61% between eras while YC's AI tagging moved ~1.6pp.
  - **Definition dependence.** The largest shift (agent infrastructure) reads +6.2pp / +11.0pp / +0.2pp under three defensible theme boundaries — a ~55x spread from wording alone.
- Combined with the 0.34 test-retest Jaccard, **no individual theme shift in this dataset is established.**

### Q2 — Does matching an RFS predict better early traction?
- **No meaningful effect.** Composite gap between own-RFS matchers and their batchmates: **+1.4 points on a 0–100 scale** (strong) and **+0.9** (strong+partial). Survival +0.7pp, reached-Growth +0.0pp.
- These are 0–2 year old companies, ~95% still Active/Early, measured through a classifier with a 69% test-retest floor. Both facts push any true effect toward zero. **The null means the test cannot resolve an effect, not that none exists.**

## 12. Changes made during the build

1. **Era-balanced chunking.** Classifier leniency varies widely between workers; id-ordered chunks gave each worker a single era, confounding leniency with the baseline-vs-RFS-era contrast Q1 rests on. Chunks are dealt round-robin (every chunk 47–56% baseline).
2. **Canonical theme renamed.** "AI-Native Discovery Engines" is closed-loop *scientific* discovery, not search.
3. **Dashboard data inlined.** Browsers block sibling-script loads over `file://`.
4. **Sharpened agent-theme boundary** written permanently into the catalog generator, with a catalog-level note on what matches neither theme; `PROMPT_VERSION` bumped and every company re-classified against it.
5. **Rationales collected.** Every match carries a one-line "why", surfaced in the dashboard, so disputed matches can be adjudicated against the classifier's stated reason.

## 13. Pipeline reliability engineering

Seven distinct classifier-reliability failures surfaced during this build. Each was caught by something downstream noticing, so gates were added to catch them automatically:

| Failure | Gate |
|---|---|
| Worker leniency correlated with era | Era-balanced round-robin chunking |
| Malformed output (`matches: [[]]`) | Schema normalization + hard fail in merge |
| Agent silently stopped early | Completeness check across expected chunks |
| Mid-run degradation (1% match rate) | Quality gate vs. median chunk rate |
| Bad labels cached before gate ran | Gates moved ahead of all cache writes |
| Stale validation labels vs. regenerated sample | Alignment assertion in scoring |
| Unvalidated relabel used to overturn a result | Every classification pass now gets blind validation |

The gate threshold is calibrated against observed data (failures at 1% and 25%; legitimate variance 48–81%) rather than chosen, because a tight gate combined with re-running until it passes is selection on noise.

**Cold-start rehearsal** (`pipeline/08_coldstart_check.sh`) runs every stage from an empty `data/derived` into a scratch copy and diffs the headline numbers. Verified reproducing alignment, robust-shift count, and traction gap exactly.
