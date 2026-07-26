"""Render dashboard/index.html from pipeline/dashboard_template.html + metrics.json.

The data is inlined rather than loaded as a sibling file: browsers block
cross-file script loads over file://, and the dashboard is meant to be opened
straight from disk with no server.
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
DASH = ROOT / "dashboard"


def main():
    m = json.loads((DERIVED / "metrics.json").read_text())
    themes = json.loads((DERIVED / "themes.json").read_text())
    score = {}
    sp = ROOT / "validation" / "score.json"
    if sp.exists():
        s = json.loads(sp.read_text())
        score = {k: s[k] for k in
                 ("n_pairs", "binary_agreement", "strict_agreement", "precision_binary",
                  "recall_binary", "strong_precision_loose") if k in s}

    drift = None
    dp = DERIVED / "drift_bound.json"
    if dp.exists():
        d = json.loads(dp.read_text())
        drift = {
            "overall_gap_any": d["overall"]["gap_any_match"],
            "ai_tagged_gap_any": d["ai_tagged"]["gap_any_match"],
            "non_ai_tagged_gap_any": d["non_ai_tagged"]["gap_any_match"],
            "ai_tag_share_baseline": d["vocabulary_drift"]["ai_tag_share_baseline"],
            "ai_tag_share_rfs": d["vocabulary_drift"]["ai_tag_share_rfs_era"],
            "keyword_growth_pct": 100 * (d["vocabulary_drift"]["mean_keyword_count_rfs_era"]
                                         / d["vocabulary_drift"]["mean_keyword_count_baseline"] - 1),
            "terciles": d["vocabulary_intensity"],
        }

    leak = None
    lp = DERIVED / "leak_test.json"
    if lp.exists():
        leak = json.loads(lp.read_text())

    boundary = None
    bp = DERIVED / "boundary_comparison.json"
    if bp.exists():
        boundary = json.loads(bp.read_text())

    retest = None
    rp = DERIVED / "test_retest.json"
    if rp.exists():
        retest = json.loads(rp.read_text())

    payload = {
        "batches": m["batches"],
        "baseline": m["baseline"],
        "baselines": m["baselines"],
        "rfs_era": m["rfs_era"],
        "no_rfs_batches": m["no_rfs_batches"],
        "weights": m["weights"],
        "min_cell": m["min_cell"],
        "fdr": m["fdr"],
        "drift": drift,
        "leak_test": leak,
        "boundary": boundary,
        "test_retest": retest,
        "variants": m["variants"],
        "themes": [{"id": t["id"], "name": t["name"], "active_batches": t["active_batches"],
                    "members": [{"batch": x["batch"], "title": x["title"], "author": x["author"],
                                 "summary": x.get("summary", "")} for x in t["members"]]}
                   for t in themes],
        "validation": score,
    }
    DASH.mkdir(exist_ok=True)
    template = (ROOT / "pipeline" / "dashboard_template.html").read_text()
    assert "/*__RFS_DATA__*/" in template, "template placeholder missing"
    # </script> inside the JSON would close the tag early
    blob = json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__RFS_DATA__*/", "window.RFS_DATA = " + blob + ";")
    out = DASH / "index.html"
    out.write_text(html)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB, self-contained)")


if __name__ == "__main__":
    main()
