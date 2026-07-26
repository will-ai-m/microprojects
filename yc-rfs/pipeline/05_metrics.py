"""Compute Q1 alignment + Q2 traction metrics (PRD 5.3-5.5).

Inputs:
  data/raw/companies-all.json
  data/derived/themes.json
  data/derived/classifications.jsonl   — one line per company:
      {"id": ..., "matches": [{"theme": "<theme_id>", "confidence": "strong"|"partial"}]}
Output:
  data/derived/metrics.json
"""
import json
import math
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"

# Pre-RFS baselines. `full` spans the ChatGPT-era shift; `late` is the
# post-ChatGPT, pre-RFS sensitivity window (PRD 4.3). A shift that survives
# both is not merely the AI boom.
BASELINES = {
    "full": ["Winter 2022", "Summer 2022", "Winter 2023", "Summer 2023", "Winter 2024"],
    "late": ["Winter 2023", "Summer 2023", "Winter 2024"],
}
BASELINE = BASELINES["full"]
RFS_ERA = [
    "Summer 2024", "Fall 2024", "Winter 2025", "Spring 2025", "Summer 2025",
    "Fall 2025", "Winter 2026", "Spring 2026", "Summer 2026",
]
ALL_BATCHES = BASELINE + RFS_ERA  # chronological
BOOT_N = 2000
SEED = 20260725
MIN_CELL = 5  # below this, rates are not reported as rates (dashboard suppresses)

# Composite traction weights. `top_company` was dropped: it is true for 0 of the
# ~2,900 companies in scope (YC only awards it to older winners), so it added a
# dead 15% to the score. Remaining weights keep their original ratios,
# renormalized to 100.
WEIGHTS = {"survival": 41, "growth": 29, "team": 24, "hiring": 6}

rng = random.Random(SEED)


def load():
    companies = {c["id"]: c for c in json.loads((ROOT / "data/raw/companies-all.json").read_text())
                 if c["batch"] in set(ALL_BATCHES)}
    themes = json.loads((DERIVED / "themes.json").read_text())
    matches = {}
    with open(DERIVED / "classifications.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            matches[rec["id"]] = rec.get("matches", [])
    return companies, themes, matches


def match_sets(matches, strong_only=True):
    """company id -> set of matched theme ids"""
    out = {}
    for cid, ms in matches.items():
        out[cid] = {m["theme"] for m in ms if (m["confidence"] == "strong" or not strong_only)}
    return out


def wilson(p, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / denom
    return (max(0.0, center - half), min(1.0, center + half))


def boot_diff_ci(a, b, iters=BOOT_N):
    """95% CI for mean(a) - mean(b) of binary/numeric lists."""
    if not a or not b:
        return (None, None)
    diffs = []
    for _ in range(iters):
        sa = [a[rng.randrange(len(a))] for _ in range(len(a))]
        sb = [b[rng.randrange(len(b))] for _ in range(len(b))]
        diffs.append(sum(sa) / len(sa) - sum(sb) / len(sb))
    diffs.sort()
    return (diffs[int(0.025 * iters)], diffs[int(0.975 * iters)])


def two_prop_p(k1, n1, k2, n2):
    """Two-sided p-value for a difference in proportions (normal approximation).

    Used only to rank themes for FDR control; the reported uncertainty is the
    bootstrap CI. Returns None when the normal approximation is unusable.
    """
    if n1 == 0 or n2 == 0:
        return None
    p = (k1 + k2) / (n1 + n2)
    if p in (0.0, 1.0):
        return None
    se = math.sqrt(p * (1 - p) * (1 / n1 + 1 / n2))
    if se == 0:
        return None
    z = (k1 / n1 - k2 / n2) / se
    return math.erfc(abs(z) / math.sqrt(2))


def benjamini_hochberg(pvals):
    """{key: p} -> {key: q}. Standard BH step-up, monotonicity enforced."""
    items = [(k, p) for k, p in pvals.items() if p is not None]
    if not items:
        return {}
    items.sort(key=lambda kp: kp[1])
    m = len(items)
    q = {}
    prev = 1.0
    for i in range(m - 1, -1, -1):
        k, p = items[i]
        val = min(prev, p * m / (i + 1))
        q[k] = val
        prev = val
    return q


def median(xs):
    if not xs:
        return None
    s = sorted(xs)
    n = len(s)
    return s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2


def traction_score(c, batch_team_sizes):
    """Composite 0-100; see WEIGHTS."""
    score = 0.0
    if c["status"] != "Inactive":
        score += WEIGHTS["survival"]
    if c["stage"] == "Growth":
        score += WEIGHTS["growth"]
    ts = c.get("team_size") or 0
    peers = batch_team_sizes[c["batch"]]
    if peers:
        score += WEIGHTS["team"] * (sum(1 for p in peers if p < ts) / len(peers))
    if c.get("isHiring"):
        score += WEIGHTS["hiring"]
    return score


def group_stats(cs, batch_team_sizes):
    n = len(cs)
    if n == 0:
        return {"n": 0}
    surv = [1 if c["status"] != "Inactive" else 0 for c in cs]
    growth = [1 if c["stage"] == "Growth" else 0 for c in cs]
    hiring = [1 if c.get("isHiring") else 0 for c in cs]
    scores = [traction_score(c, batch_team_sizes) for c in cs]
    status_counts = {}
    for c in cs:
        status_counts[c["status"]] = status_counts.get(c["status"], 0) + 1
    return {
        "n": n,
        "survival": sum(surv) / n,
        "pct_growth": sum(growth) / n,
        "median_team_size": median([c.get("team_size") or 0 for c in cs]),
        "pct_hiring": sum(hiring) / n,
        "mean_traction": sum(scores) / n,
        "status_counts": status_counts,
    }


def main():
    companies, themes, matches = load()
    by_batch = {}
    for c in companies.values():
        by_batch.setdefault(c["batch"], []).append(c)
    batch_team_sizes = {b: [c.get("team_size") or 0 for c in cs] for b, cs in by_batch.items()}

    # batch -> theme ids in that batch's own RFS
    own_rfs = {}
    for t in themes:
        for b in t["active_batches"]:
            own_rfs.setdefault(b, set()).add(t["id"])
    # Fall 2024 and Winter 2026 sit inside the RFS era but YC published no RFS
    # for them. They stay in the time series and the any-theme cut, but must not
    # act as "theme was absent" evidence in the within-era contrast.
    no_rfs_batches = [b for b in RFS_ERA if b not in own_rfs]

    results = {
        "generated_from": "05_metrics.py",
        "batches": ALL_BATCHES,
        "baseline": BASELINE,
        "baselines": BASELINES,
        "rfs_era": RFS_ERA,
        "no_rfs_batches": no_rfs_batches,
        "weights": WEIGHTS,
        "min_cell": MIN_CELL,
        "variants": {},
    }

    for variant, strong_only in (("strong", True), ("strong_plus_partial", False)):
        msets = match_sets(matches, strong_only)

        # ---- Q1a: share-of-batch own-RFS alignment ----
        q1a = {}
        for b in RFS_ERA:
            if b not in own_rfs or b not in by_batch:
                continue
            cs = by_batch[b]
            hits = [c for c in cs if msets.get(c["id"], set()) & own_rfs[b]]
            p = len(hits) / len(cs)
            q1a[b] = {
                "n": len(cs), "n_matched": len(hits), "share": p, "wilson_ci": wilson(p, len(cs)),
                "per_theme": {
                    tid: sum(1 for c in cs if tid in msets.get(c["id"], set()))
                    for tid in sorted(own_rfs[b])
                },
            }

        # ---- Q1b: per-theme time series + before/after shift ----
        q1b = {}
        pvals = {}
        for t in themes:
            tid = t["id"]
            series = {}
            for b in ALL_BATCHES:
                cs = by_batch.get(b, [])
                if not cs:
                    continue
                k = sum(1 for c in cs if tid in msets.get(c["id"], set()))
                series[b] = {"n": len(cs), "k": k, "share": k / len(cs)}

            active_ids = [c["id"] for b in t["active_batches"] for c in by_batch.get(b, [])]
            act = [1 if tid in msets.get(cid, set()) else 0 for cid in active_ids]
            p_act = sum(act) / len(act) if act else None

            entry = {
                "name": t["name"], "active_batches": t["active_batches"], "series": series,
                "share_active": p_act, "n_active": len(act),
                "baselines": {},
            }

            for bname, bbatches in BASELINES.items():
                bids = [c["id"] for b in bbatches for c in by_batch.get(b, [])]
                base = [1 if tid in msets.get(cid, set()) else 0 for cid in bids]
                p_base = sum(base) / len(base) if base else None
                lo, hi = boot_diff_ci(act, base) if act and base else (None, None)
                diff = (p_act - p_base) if p_act is not None and p_base is not None else None
                entry["baselines"][bname] = {
                    "batches": bbatches,
                    "share_baseline": p_base,
                    "n_baseline": len(base),
                    "diff": diff,
                    "ratio": (p_act / p_base) if p_act and p_base else None,
                    "diff_ci95": [lo, hi],
                    "p_value": two_prop_p(sum(act), len(act), sum(base), len(base)),
                }
                if bname == "full":
                    pvals[tid] = entry["baselines"][bname]["p_value"]

            # secondary: within-era batches where the theme was NOT listed,
            # excluding batches that had no RFS at all
            inact_ids = [c["id"] for b in RFS_ERA
                         if b not in t["active_batches"] and b not in no_rfs_batches
                         for c in by_batch.get(b, [])]
            ina = [1 if tid in msets.get(cid, set()) else 0 for cid in inact_ids]
            entry["share_era_inactive"] = (sum(ina) / len(ina)) if ina else None
            entry["n_era_inactive"] = len(ina)

            # convenience mirrors of the primary baseline (dashboard reads these)
            prim = entry["baselines"]["full"]
            entry.update({k: prim[k] for k in ("share_baseline", "n_baseline", "diff", "ratio", "diff_ci95")})
            q1b[tid] = entry

        # FDR across themes (primary baseline only)
        qvals = benjamini_hochberg(pvals)
        for tid, entry in q1b.items():
            q = qvals.get(tid)
            entry["p_value"] = pvals.get(tid)
            entry["q_value"] = q
            entry["survives_fdr"] = (q is not None and q < 0.05)
            lo_l, hi_l = entry["baselines"]["late"]["diff_ci95"]
            entry["robust_both_baselines"] = bool(
                entry["survives_fdr"]
                and lo_l is not None
                and (lo_l > 0 or hi_l < 0)
                and entry["baselines"]["late"]["diff"] is not None
                and entry["diff"] is not None
                and (entry["baselines"]["late"]["diff"] > 0) == (entry["diff"] > 0)
            )
        results.setdefault("fdr", {})[variant] = {
            "n_tested": sum(1 for p in pvals.values() if p is not None),
            "n_survive": sum(1 for e in q1b.values() if e["survives_fdr"]),
            "n_robust_both_baselines": sum(1 for e in q1b.values() if e["robust_both_baselines"]),
        }

        # ---- Q2: within-batch matcher vs non-matcher ----
        q2 = {}
        era_theme_ids = {t["id"] for t in themes}
        for defn, pick in (
            ("own_rfs", lambda c: msets.get(c["id"], set()) & own_rfs.get(c["batch"], set())),
            ("any_era_theme", lambda c: msets.get(c["id"], set()) & era_theme_ids),
        ):
            per_batch = {}
            pooled_m, pooled_nm = [], []
            for b in RFS_ERA:
                cs = by_batch.get(b, [])
                if not cs or (defn == "own_rfs" and b not in own_rfs):
                    continue
                m = [c for c in cs if pick(c)]
                nm = [c for c in cs if not pick(c)]
                sm, snm = group_stats(m, batch_team_sizes), group_stats(nm, batch_team_sizes)
                delta = None
                if sm["n"] >= MIN_CELL and snm["n"] >= MIN_CELL:
                    a = [traction_score(c, batch_team_sizes) for c in m]
                    bb = [traction_score(c, batch_team_sizes) for c in nm]
                    lo, hi = boot_diff_ci(a, bb)
                    delta = {"traction_diff": sm["mean_traction"] - snm["mean_traction"], "ci95": [lo, hi]}
                per_batch[b] = {"matchers": sm, "non_matchers": snm, "delta": delta}
                pooled_m.extend(m)
                pooled_nm.extend(nm)
            comp_keys = ["survival", "pct_growth", "pct_hiring", "mean_traction"]
            pooled = {}
            for key in comp_keys:
                num, den = 0.0, 0
                for b, r in per_batch.items():
                    if r["matchers"]["n"] >= MIN_CELL and r["non_matchers"]["n"] >= MIN_CELL:
                        w = r["matchers"]["n"] + r["non_matchers"]["n"]
                        num += w * (r["matchers"][key] - r["non_matchers"][key])
                        den += w
                pooled[key + "_diff"] = num / den if den else None
            q2[defn] = {"per_batch": per_batch, "pooled_weighted_diffs": pooled,
                        "pooled_n_matchers": len(pooled_m), "pooled_n_non_matchers": len(pooled_nm)}

        # ---- per-variant company listings (must track the strictness toggle) ----
        listings = {}
        why = {}  # (company_id, theme) -> classifier rationale
        for cid, ms in matches.items():
            for m in ms:
                if m.get("why"):
                    why[(cid, m["theme"])] = m["why"]
        for t in themes:
            tid = t["id"]
            rows = [
                {"id": c["id"], "name": c["name"], "batch": c["batch"], "one_liner": c["one_liner"],
                 "status": c["status"], "stage": c["stage"], "team_size": c.get("team_size"),
                 "url": c["url"], "why": why.get((c["id"], tid), "")}
                for c in companies.values() if tid in msets.get(c["id"], set())
            ]
            rows.sort(key=lambda r: (ALL_BATCHES.index(r["batch"]), r["name"]))
            listings[tid] = rows

        results["variants"][variant] = {"q1a": q1a, "q1b": q1b, "q2": q2, "theme_companies": listings}

    out = DERIVED / "metrics.json"
    out.write_text(json.dumps(results, ensure_ascii=False))
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")
    v = results["variants"]["strong"]
    tot = sum(r["n"] for r in v["q1a"].values())
    mat = sum(r["n_matched"] for r in v["q1a"].values())
    print(f"  own-RFS alignment: {mat}/{tot} = {mat/tot:.1%}")
    f = results["fdr"]["strong"]
    print(f"  themes tested {f['n_tested']}, survive FDR {f['n_survive']}, "
          f"robust across both baselines {f['n_robust_both_baselines']}")
    print(f"  no-RFS batches excluded from within-era contrast: {no_rfs_batches}")


if __name__ == "__main__":
    main()
