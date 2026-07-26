"""Fold classifier output into the cache, emit classifications.jsonl, draw the
validation sample.

Chunk files hold only cache misses, so the merged output is assembled from the
cache against the full in-scope list (data/derived/classify_scope.json).
"""
import json
import pathlib
import random
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cache  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
SEED = 20260725


VALID_CONF = ("strong", "partial")
# How far below the median chunk match rate is treated as a failed chunk rather
# than legitimate classifier variance.
#
# Calibrated against observed runs rather than picked: catastrophic failures came
# in at 1% and 25% against a ~90% median, while chunks re-classified independently
# landed anywhere from 48% to 81% — and test-retest measurement (see
# data/derived/test_retest.json) shows two independent passes over the SAME
# companies agree only ~69% on whether a company matches anything at all. Chunk
# rates therefore carry a lot of legitimate run-to-run noise, and a tight gate
# would just cause re-rolling until a chunk happens to clear the bar, which is
# selection on noise. 0.50 catches only genuine collapses.
GATE_TOLERANCE = 0.50


def normalize_matches(raw, ctx, valid_themes):
    """Coerce classifier output into the canonical schema, or fail loudly.

    Agents occasionally emit `[[]]` for "no matches"; that is accepted and
    flattened. Anything else that does not fit the schema is an error — the
    merge stage validates rather than trusting the classifier.
    """
    if not isinstance(raw, list):
        raise SystemExit(f"{ctx}: 'matches' is {type(raw).__name__}, expected list")
    out = []
    for m in raw:
        if isinstance(m, list):
            if m:  # a non-empty nested list is a real schema violation
                raise SystemExit(f"{ctx}: nested non-empty list in matches: {m!r}")
            continue  # [[]] -> no matches
        if not isinstance(m, dict):
            raise SystemExit(f"{ctx}: match is {type(m).__name__}, expected object")
        theme, conf = m.get("theme"), m.get("confidence")
        if theme not in valid_themes:
            raise SystemExit(f"{ctx}: unknown theme {theme!r}")
        if conf not in VALID_CONF:
            raise SystemExit(f"{ctx}: bad confidence {conf!r}")
        entry = {"theme": theme, "confidence": conf}
        if m.get("why"):
            entry["why"] = str(m["why"]).strip()
        out.append(entry)
    # a company matching the same theme twice is a classifier slip, not data
    seen = set()
    deduped = []
    for e in out:
        if e["theme"] in seen:
            continue
        seen.add(e["theme"])
        deduped.append(e)
    return deduped


def main():
    scope = json.loads((DERIVED / "classify_scope.json").read_text())
    companies = {c["id"]: c for c in scope}
    chash = cache.catalog_hash()

    valid_themes = {t["id"] for t in json.loads((DERIVED / "themes.json").read_text())}

    # Completeness: every chunk handed out must come back. An agent that stops
    # early leaves a hole that would otherwise surface only as a cache miss later.
    expected = {p.stem for p in (DERIVED / "classify_input").glob("chunk_*.json")}
    produced = {p.stem for p in (DERIVED / "classifications").glob("chunk_*.jsonl")}
    if expected - produced:
        raise SystemExit(f"missing classifier output for: {sorted(expected - produced)}")

    # 1. read + validate every chunk. Nothing is written to the cache until all
    #    gates pass — a rejected run must not leave bad labels cached, because the
    #    cache would then serve them silently on the retry.
    staged = []  # (key, id, matches)
    rates = []
    for f in sorted((DERIVED / "classifications").glob("chunk_*.jsonl")):
        inp_path = DERIVED / "classify_input" / f"{f.stem}.json"
        if not inp_path.exists():
            continue
        inp = json.loads(inp_path.read_text())
        lines = [json.loads(l) for l in f.read_text().splitlines() if l.strip()]
        if len(lines) != len(inp):
            raise SystemExit(f"{f.name}: {len(lines)} results for {len(inp)} companies")
        matched = 0
        for c, rec in zip(inp, lines):
            if rec["id"] != c["id"]:
                raise SystemExit(f"{f.name}: id order mismatch at {c['id']}")
            matches = normalize_matches(rec.get("matches"), f"{f.name}:{c['id']}", valid_themes)
            matched += bool(matches)
            staged.append((cache.company_key(c, chash), c["id"], matches))
        rates.append((f.stem, matched / len(lines)))

    # Quality gate. Chunks are era-balanced and randomly dealt, so their match
    # rates should be similar. A chunk far below the median means the classifier
    # was miscalibrated or degraded on that chunk — re-run it rather than ingest it.
    if len(rates) >= 5:
        med = sorted(r for _, r in rates)[len(rates) // 2]
        bad = [(s, r) for s, r in rates if r < med - GATE_TOLERANCE]
        if bad:
            detail = ", ".join(f"{s} {r:.0%}" for s, r in bad)
            raise SystemExit(
                f"quality gate: {len(bad)} chunk(s) more than {GATE_TOLERANCE:.0%} below the median "
                f"match rate of {med:.0%} — {detail}. Re-run those chunks before merging. "
                f"(Nothing was written to the cache.)"
            )

    # 2. gates passed — now fold into the cache
    cached = cache.load()
    fresh = []
    for key, cid, matches in staged:
        if key not in cached:
            entry = {"key": key, "id": cid, "matches": matches,
                     "prompt_version": cache.PROMPT_VERSION, "model": cache.MODEL}
            cached[key] = entry
            fresh.append(entry)
    if fresh:
        cache.write(fresh)
    print(f"cache: {len(cached)} entries ({len(fresh)} new this run)")

    # 2. assemble the merged file for every in-scope company
    records, missing = [], []
    for c in scope:
        key = cache.company_key(c, chash)
        hit = cached.get(key)
        if hit is None:
            missing.append(c["id"])
        else:
            records.append({"id": c["id"], "matches": hit["matches"]})
    if missing:
        raise SystemExit(f"{len(missing)} companies have no classification "
                         f"(e.g. {missing[:5]}) — run the classifier on the current chunks")

    out = DERIVED / "classifications.jsonl"
    with open(out, "w") as fh:
        for rec in sorted(records, key=lambda r: r["id"]):
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    n_matched = sum(1 for r in records if r["matches"])
    n_strong = sum(1 for r in records for m in r["matches"] if m["confidence"] == "strong")
    n_partial = sum(1 for r in records for m in r["matches"] if m["confidence"] == "partial")
    print(f"{len(records)} companies -> {out}")
    print(f"  {n_matched} with >=1 match ({n_matched/len(records):.1%}); "
          f"{n_strong} strong + {n_partial} partial labels")

    # 3. validation sample
    rng = random.Random(SEED)
    themes = json.loads((DERIVED / "themes.json").read_text())
    theme_ids = [t["id"] for t in themes]
    strong_pairs = [(r["id"], m["theme"]) for r in records for m in r["matches"] if m["confidence"] == "strong"]
    partial_pairs = [(r["id"], m["theme"]) for r in records for m in r["matches"] if m["confidence"] == "partial"]
    claimed = {(r["id"], m["theme"]) for r in records for m in r["matches"]}
    none_pairs = []
    ids = list(companies)
    while len(none_pairs) < 40:
        p = (rng.choice(ids), rng.choice(theme_ids))
        if p not in claimed and p not in none_pairs:
            none_pairs.append(p)

    sample = (
        [("strong", *p) for p in rng.sample(strong_pairs, min(40, len(strong_pairs)))]
        + [("partial", *p) for p in rng.sample(partial_pairs, min(20, len(partial_pairs)))]
        + [("none", *p) for p in none_pairs]
    )
    rng.shuffle(sample)
    rows = []
    for claimed_label, cid, tid in sample:
        c = companies[cid]
        rows.append({
            "company_id": cid, "name": c["name"], "batch": c["batch"],
            "one_liner": c["one_liner"], "description": c["description"],
            "industry": c["industry"], "tags": c["tags"],
            "theme": tid, "claimed": claimed_label,
        })
    vdir = ROOT / "validation"
    vdir.mkdir(exist_ok=True)
    (vdir / "sample.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False))
    (vdir / "sample_blind.json").write_text(json.dumps(
        [{k: v for k, v in r.items() if k != "claimed"} for r in rows], indent=1, ensure_ascii=False))
    print(f"validation sample: {len(rows)} pairs -> {vdir / 'sample.json'}")


if __name__ == "__main__":
    main()
