#!/usr/bin/env bash
# Cold-start rehearsal: run the whole pipeline from an empty data/derived into a
# scratch copy of the repo, then diff the headline numbers against the live run.
#
# The classification stage needs LLM agents, so the existing cache is copied in
# first: every other stage still executes in order from nothing, which is what
# this is testing (hidden ordering dependencies), without paying to re-classify.
#
# Usage: bash pipeline/08_coldstart_check.sh [scratch_dir]
set -euo pipefail

SRC="$(cd "$(dirname "$0")/.." && pwd)"
SCRATCH="${1:-/private/tmp/claude-501/-Users-willyu-microprojects/1fcf44c3-90eb-4d07-8744-e9d79aeef379/scratchpad/yc-rfs-coldstart}"

echo "== cold-start rehearsal =="
echo "source:  $SRC"
echo "scratch: $SCRATCH"

rm -rf "$SCRATCH"
mkdir -p "$SCRATCH"
cp -R "$SRC/pipeline" "$SCRATCH/pipeline"
mkdir -p "$SCRATCH/data/raw" "$SCRATCH/data/derived" "$SCRATCH/validation"

# raw inputs are fetched artefacts, not derived — a cold start keeps them
cp -R "$SRC/data/raw/." "$SCRATCH/data/raw/"
# hand-labelled validation data is an input too (a human produced it)
cp "$SRC/validation/labels_0_49.jsonl" "$SRC/validation/labels_50_99.jsonl" "$SCRATCH/validation/" 2>/dev/null || true
# the classification cache stands in for the LLM stage
cp "$SRC/data/derived/classification_cache.jsonl" "$SCRATCH/data/derived/"
# diagnostics produced by one-off agent runs are inputs to the dashboard build
for f in drift_bound.json leak_test.json theme_summaries.json; do
  [ -f "$SRC/data/derived/$f" ] && cp "$SRC/data/derived/$f" "$SCRATCH/data/derived/"
done

cd "$SCRATCH"
echo; echo "-- 03 canonicalize themes --"; python3 pipeline/03_canonicalize_themes.py
echo; echo "-- 04 prepare classification --"; python3 pipeline/04_prepare_classification.py
echo; echo "-- 04b merge + sample --"; python3 pipeline/04b_merge_and_sample.py
echo; echo "-- 04c score validation --"; python3 pipeline/04c_score_validation.py | head -5
echo; echo "-- 05 metrics --"; python3 pipeline/05_metrics.py
echo; echo "-- 07 drift bound --"; python3 pipeline/07_drift_bound.py > /dev/null && echo "ok"
echo; echo "-- 06 build dashboard --"; python3 pipeline/06_build_dashboard.py

echo; echo "== headline comparison (scratch vs live) =="
python3 - "$SRC" "$SCRATCH" <<'PY'
import json, sys, pathlib
src, scratch = (pathlib.Path(p) / "data/derived/metrics.json" for p in sys.argv[1:3])
a, b = json.loads(src.read_text()), json.loads(scratch.read_text())
def headline(m):
    v = m["variants"]["strong"]
    tot = sum(r["n"] for r in v["q1a"].values())
    mat = sum(r["n_matched"] for r in v["q1a"].values())
    return {
        "alignment": round(mat / tot, 4),
        "robust_shifts": m["fdr"]["strong"]["n_robust_both_baselines"],
        "traction_gap": round(v["q2"]["own_rfs"]["pooled_weighted_diffs"]["mean_traction_diff"], 3),
    }
ha, hb = headline(a), headline(b)
ok = ha == hb
for k in ha:
    flag = "OK " if ha[k] == hb[k] else "DIFF"
    print(f"  {flag} {k}: live={ha[k]}  scratch={hb[k]}")
print("\nRESULT:", "cold start reproduces the live numbers" if ok else "MISMATCH — investigate")
sys.exit(0 if ok else 1)
PY
