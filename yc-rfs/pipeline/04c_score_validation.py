"""Score the classifier against the blind human-surrogate labels (PRD 5.2).

Agreement is measured two ways:
  binary  — match (strong|partial) vs none; this is what the headline metrics depend on
  strict  — exact 3-way label agreement
Also reports per-agent (chunk-group) match rates, to catch calibration drift.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
V = ROOT / "validation"
D = ROOT / "data" / "derived"


def main():
    sample = json.loads((V / "sample.json").read_text())
    labels = {}
    for f in ("labels_0_49.jsonl", "labels_50_99.jsonl"):
        for line in (V / f).read_text().splitlines():
            if line.strip():
                rec = json.loads(line)
                labels[rec["i"]] = rec["label"]
    assert len(labels) == len(sample), (len(labels), len(sample))

    rows = []
    for i, s in enumerate(sample):
        rows.append({**s, "claimed": s["claimed"], "truth": labels[i]})

    def binary(x):
        return "match" if x in ("strong", "partial") else "none"

    n = len(rows)
    strict = sum(1 for r in rows if r["claimed"] == r["truth"]) / n
    bin_agree = sum(1 for r in rows if binary(r["claimed"]) == binary(r["truth"])) / n

    # precision/recall of the classifier's positive calls, binary sense
    tp = sum(1 for r in rows if binary(r["claimed"]) == "match" and binary(r["truth"]) == "match")
    fp = sum(1 for r in rows if binary(r["claimed"]) == "match" and binary(r["truth"]) == "none")
    fn = sum(1 for r in rows if binary(r["claimed"]) == "none" and binary(r["truth"]) == "match")
    prec = tp / (tp + fp) if tp + fp else None
    rec = tp / (tp + fn) if tp + fn else None

    # strong-only precision: of claimed-strong, how many the validator judged strong
    cs = [r for r in rows if r["claimed"] == "strong"]
    strong_prec = sum(1 for r in cs if r["truth"] == "strong") / len(cs) if cs else None
    strong_prec_loose = sum(1 for r in cs if r["truth"] in ("strong", "partial")) / len(cs) if cs else None

    conf = {}
    for r in rows:
        conf[(r["claimed"], r["truth"])] = conf.get((r["claimed"], r["truth"]), 0) + 1

    out = {
        "n_pairs": n,
        "binary_agreement": bin_agree,
        "strict_agreement": strict,
        "precision_binary": prec,
        "recall_binary": rec,
        "strong_precision_exact": strong_prec,
        "strong_precision_loose": strong_prec_loose,
        "confusion": {f"claimed={k[0]}|truth={k[1]}": v for k, v in sorted(conf.items())},
        "disagreements": [
            {"name": r["name"], "theme": r["theme"], "claimed": r["claimed"], "truth": r["truth"],
             "one_liner": r["one_liner"]}
            for r in rows if binary(r["claimed"]) != binary(r["truth"])
        ],
    }
    (V / "score.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))

    print(f"n={n}  binary agreement={bin_agree:.0%}  strict={strict:.0%}")
    print(f"precision={prec:.0%}  recall={rec:.0%}" if prec is not None and rec is not None else "")
    print(f"claimed-strong precision: exact={strong_prec:.0%} loose={strong_prec_loose:.0%}"
          if strong_prec is not None else "")
    print("confusion:")
    for k, v in sorted(conf.items()):
        print(f"  claimed={k[0]:8} truth={k[1]:8} {v}")
    print(f"\n{len(out['disagreements'])} binary disagreements -> {V / 'score.json'}")

    # per-agent calibration (3 chunks per agent, 100 companies per chunk)
    recs = [json.loads(l) for l in (D / "classifications.jsonl").read_text().splitlines()]
    by_id = {r["id"]: r for r in recs}
    print("\nper-agent strong-match rate (calibration check):")
    for a in range(10):
        chunks = range(a * 3, min(a * 3 + 3, 29))
        ids = []
        for ci in chunks:
            p = D / "classify_input" / f"chunk_{ci:02d}.json"
            if p.exists():
                ids += [c["id"] for c in json.loads(p.read_text())]
        if not ids:
            continue
        strong = sum(1 for i in ids if any(m["confidence"] == "strong" for m in by_id[i]["matches"]))
        print(f"  agent {a}: chunks {list(chunks)} n={len(ids):4} strong-rate={strong / len(ids):.0%}")


if __name__ == "__main__":
    main()
