# YC RFS: what they ask for vs. what they fund

Does YC actually admit the companies its Requests for Startups ask for — and do
theme-matching companies do better than their batchmates?

**Deliverable:** [`dashboard/index.html`](dashboard/index.html) — a self-contained
static page (no server, no network). Open it directly in a browser.

See [PRD.md](PRD.md) for the full design, scope decisions, and limitations.

## Running the pipeline

Each stage reads and writes files, so any stage can be re-run on its own.

```bash
python3 pipeline/01_fetch_companies.py          # snapshot yc-oss company data
```

```bash
playwright-cli open https://www.ycombinator.com/rfs
playwright-cli --raw run-code --filename=pipeline/02_fetch_rfs.js > data/raw/rfs/_all.json
playwright-cli close
python3 pipeline/02_split_rfs.py                # -> data/raw/rfs/<batch>.json
```

```bash
python3 pipeline/03_canonicalize_themes.py      # 96 RFS entries -> 48 canonical themes
python3 pipeline/04_prepare_classification.py   # theme catalog + era-balanced company chunks
# classification itself runs as parallel Haiku subagents over data/derived/classify_input/,
# writing data/derived/classifications/chunk_NN.jsonl
python3 pipeline/04b_merge_and_sample.py        # merge + draw the validation sample
# blind relabelling of validation/sample_blind.json runs as Sonnet subagents
python3 pipeline/04c_score_validation.py        # agreement scores + calibration check
python3 pipeline/05_metrics.py                  # Q1 alignment + Q2 traction
python3 pipeline/06_build_dashboard.py          # render dashboard/index.html
```

## Layout

| Path | What |
|---|---|
| `data/raw/` | yc-oss company snapshot; RFS text per batch |
| `data/derived/themes.json` | the 48 canonical themes and their source RFS entries |
| `data/derived/theme_catalog.md` | the catalog handed to the classifier |
| `data/derived/classify_input/` | era-balanced company chunks |
| `data/derived/classifications/` | per-chunk classifier output |
| `data/derived/classifications.jsonl` | merged, one line per company |
| `data/derived/metrics.json` | all computed statistics |
| `validation/` | blind sample, independent labels, agreement scores |
| `pipeline/dashboard_template.html` | dashboard source (data is inlined at build) |

## Headline findings

> **Reliability floor.** Two independent runs of this pipeline over the same 372 companies agree only **69%** on whether a company matches any theme, with mean Jaccard **0.34** on which themes. Aggregates over ~1,200 companies survive that noise; individual theme shifts do not.

**Q1 — alignment: 24.1%** of RFS-era companies match a theme from their own batch's RFS. The RFS describes a minority of each batch. This is the Q1 number worth quoting.

**Q1 — shifts: not established.** Seven themes clear FDR correction and both baselines, but (a) the era gap shrinks from +14.1pp to ~+3.7pp inside the fixed slice of AI-tagged companies — companies redescribe themselves faster than the portfolio changes — and (b) the largest shift reads +6.2 / +11.0 / +0.2pp under three defensible theme boundaries. Below the noise floor either way.

**Q2 — outcomes: no meaningful effect.** +1.4 composite points (0–100 scale) for RFS-matchers vs. batchmates, +0.9 under looser matching. With 0–2 year old companies, ~95% still Active/Early, and a 69% test-retest floor, this test cannot resolve an effect — which is not the same as there being none.

## Two design decisions worth knowing

**Chunks are era-balanced on purpose.** Classifier workers vary in leniency. An
earlier run chunked companies by id — and since YC ids run chronologically, each
worker saw a single era, so worker leniency was confounded with the
baseline-vs-RFS-era contrast that Q1 rests on. Chunks are now dealt round-robin
across batches (every chunk is 47–56% baseline), which turns that variance into
noise instead of bias. The id-ordered run is kept at
`data/derived/classifications_v1_idordered/` for comparison.

**Diagnostics are first-class outputs.** `07_drift_bound.py`, `leak_test.json`, and `disambig_sensitivity.json` exist to attack the headline rather than support it, and the dashboard surfaces what they found. Two of the three materially weakened the Q1 result.

**"Strong" vs "partial" is noisier than match-vs-no-match.** Blind relabelling
agrees ~90% on whether a company matches a theme at all (precision 83%, recall
100% — errors are one-sided, the classifier over-calls), but only ~75% on the
exact three-way label. Treat the strong-only view as the strict variant and the
strong+partial view as the sensitivity check — neither alone is the truth.
