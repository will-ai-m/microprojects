"""Quantify what the sharpened agent-theme boundary changed (v2 fuzzy -> v3 sharp).

The two largest themes originally had a blurry border, and where the border was
drawn moved the headline shift substantially. The catalog was tightened and every
company re-classified against it, so v3 is the primary labelling — this script
records the delta so the change is reported as a measured number rather than a
claim.

Reads the preserved v2 labels alongside the current v3 labels; writes
data/derived/boundary_comparison.json.
"""
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data" / "derived"
SEED = 20260725
BASELINE = {"Winter 2022", "Summer 2022", "Winter 2023", "Summer 2023", "Winter 2024"}
PAIR = ("agent-infrastructure", "vertical-agents")
# From the earlier one-off strict probe (data/derived/disambig_sensitivity.json).
# Retained only as evidence the boundary matters; it was never validated and was
# demonstrably over-strict, so it is not treated as a measurement.
STRICT_PROBE = {"agent-infrastructure": 0.002, "vertical-agents": 0.022}

rng = random.Random(SEED)


def load_labels(path):
    out = {}
    for line in pathlib.Path(path).read_text().splitlines():
        if line.strip():
            r = json.loads(line)
            out[r["id"]] = r["matches"]
    return out


def boot(a, b, iters=2000):
    if not a or not b:
        return (None, None)
    d = []
    for _ in range(iters):
        sa = [a[rng.randrange(len(a))] for _ in a]
        sb = [b[rng.randrange(len(b))] for _ in b]
        d.append(sum(sa) / len(sa) - sum(sb) / len(sb))
    d.sort()
    return d[int(0.025 * iters)], d[int(0.975 * iters)]


def shift(labels, tid, scope, active_batches):
    act = [1 if any(m["theme"] == tid and m["confidence"] == "strong" for m in labels.get(i, [])) else 0
           for i in scope if scope[i]["batch"] in active_batches]
    base = [1 if any(m["theme"] == tid and m["confidence"] == "strong" for m in labels.get(i, [])) else 0
            for i in scope if scope[i]["batch"] in BASELINE]
    if not act or not base:
        return None
    pa, pb = sum(act) / len(act), sum(base) / len(base)
    lo, hi = boot(act, base)
    n = sum(1 for i in scope if any(m["theme"] == tid for m in labels.get(i, [])))
    return {"share_baseline": pb, "share_active": pa, "diff": pa - pb, "ci95": [lo, hi], "n_matched": n}


def main():
    scope = {c["id"]: c for c in json.loads((D / "classify_scope.json").read_text())}
    themes = {t["id"]: t for t in json.loads((D / "themes.json").read_text())}
    v3 = load_labels(D / "classifications.jsonl")
    v2_path = D / "classifications_v2_fuzzy_boundary.jsonl"
    v2 = load_labels(v2_path) if v2_path.exists() else None

    out = {
        "description": ("Effect of tightening the boundary between the two largest, most "
                        "overlapping themes. v3 (sharp) is the primary labelling; v2 (fuzzy) "
                        "is retained for comparison."),
        "themes": {},
    }
    for tid in PAIR:
        ab = themes[tid]["active_batches"]
        entry = {"name": themes[tid]["name"], "v3": shift(v3, tid, scope, ab)}
        if v2:
            entry["v2"] = shift(v2, tid, scope, ab)
        entry["strict_probe_diff"] = STRICT_PROBE.get(tid)
        out["themes"][tid] = entry

    ai = out["themes"]["agent-infrastructure"]
    if v2 and ai.get("v2") and ai["v2"]["diff"]:
        out["agent_infra_shift_v2"] = ai["v2"]["diff"]
        out["agent_infra_shift_v3"] = ai["v3"]["diff"]
        out["agent_infra_shift_strict_probe"] = STRICT_PROBE["agent-infrastructure"]
        spread = [abs(x) for x in (ai["v2"]["diff"], ai["v3"]["diff"], STRICT_PROBE["agent-infrastructure"]) if x]
        out["swing_factor"] = round(max(spread) / min(spread)) if min(spread) else None

    (D / "boundary_comparison.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("wrote", D / "boundary_comparison.json")
    for tid, e in out["themes"].items():
        v2s = f"{e['v2']['diff']*100:+.1f}pp (n={e['v2']['n_matched']})" if e.get("v2") else "—"
        v3s = f"{e['v3']['diff']*100:+.1f}pp (n={e['v3']['n_matched']})"
        print(f"  {tid:22} v2 fuzzy {v2s:22} -> v3 sharp {v3s}")
    if out.get("swing_factor"):
        print(f"  boundary choice swings the agent-infrastructure shift by ~{out['swing_factor']}x")


if __name__ == "__main__":
    main()
