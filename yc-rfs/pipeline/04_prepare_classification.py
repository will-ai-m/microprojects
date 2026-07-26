"""Prepare classification inputs: theme catalog + company chunks.

Reads data/derived/themes.json and data/raw/companies-all.json.
Writes:
  data/derived/theme_catalog.md          — compact 47-theme catalog for the classifier prompt
  data/derived/classify_input/chunk_NN.json — company slices (~CHUNK companies each)
"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cache  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
CHUNK = 100

BASELINE_BATCHES = ["Winter 2022", "Summer 2022", "Winter 2023", "Summer 2023", "Winter 2024"]
RFS_ERA_BATCHES = [
    "Summer 2024", "Fall 2024", "Winter 2025", "Spring 2025", "Summer 2025",
    "Fall 2025", "Winter 2026", "Spring 2026", "Summer 2026",
]  # F26/W27 excluded: essentially no launched companies yet
SCOPE = set(BASELINE_BATCHES + RFS_ERA_BATCHES)


def main():
    themes = json.loads((DERIVED / "themes.json").read_text())
    lines = ["Theme catalog (id | name | what qualifies):", ""]
    for t in themes:
        if t.get("scope_override"):
            scope = t["scope_override"]
        else:
            scope_bits = [m["summary"] for m in t["members"] if m.get("summary")]
            # dedupe near-identical summaries, keep it compact
            seen, kept = set(), []
            for s in scope_bits:
                k = s.lower()[:60]
                if k not in seen:
                    seen.add(k)
                    kept.append(s)
            scope = " ".join(kept) if kept else t["name"]
        titles = "; ".join(m["title"] for m in t["members"])
        lines.append(f"- {t['id']} | {t['name']} | RFS titles: {titles}. Scope: {scope}")
    note_path = ROOT / "pipeline" / "03_canonicalize_themes.py"  # NEITHER_NOTE lives with the overrides
    import re as _re
    note = _re.search(r'NEITHER_NOTE = \(\n(.*?)\n\)', note_path.read_text(), _re.S)
    if note:
        lines.append("")
        lines.append(" ".join(l.strip().strip('"') for l in note.group(1).splitlines()))
    (DERIVED / "theme_catalog.md").write_text("\n".join(lines))
    print(f"theme_catalog.md: {len(themes)} themes, {len((DERIVED / 'theme_catalog.md').read_text())} chars")

    companies = json.loads((ROOT / "data" / "raw" / "companies-all.json").read_text())
    in_scope = [c for c in companies if c["batch"] in SCOPE]
    # Deal companies round-robin across chunks so every chunk (and therefore every
    # classifier worker) sees the same era mix. Classifier leniency varies between
    # workers; if chunks were id-ordered that variance would correlate with batch
    # era and contaminate the baseline-vs-RFS-era comparison.
    in_scope.sort(key=lambda c: (c["batch"], c["id"]))
    n_chunks = (len(in_scope) + CHUNK - 1) // CHUNK
    dealt = [[] for _ in range(n_chunks)]
    for i, c in enumerate(in_scope):
        dealt[i % n_chunks].append(c)
    in_scope = [c for chunk in dealt for c in chunk]
    slim = [
        {
            "id": c["id"],
            "name": c["name"],
            "batch": c["batch"],
            "one_liner": c["one_liner"],
            "description": (c["long_description"] or "")[:600],
            "industry": c["industry"],
            "tags": c["tags"],
        }
        for c in in_scope
    ]
    # Everything in scope is written to classify_scope.json (the metrics stage
    # needs the full list); only cache misses are chunked out for classification.
    (DERIVED / "classify_scope.json").write_text(json.dumps(slim, ensure_ascii=False))
    chash = cache.catalog_hash()
    cached = cache.load()
    todo = [c for c in slim if cache.company_key(c, chash) not in cached]
    hits = len(slim) - len(todo)

    outdir = DERIVED / "classify_input"
    outdir.mkdir(exist_ok=True)
    for f in outdir.glob("chunk_*.json"):
        f.unlink()
    n_chunks = (len(todo) + CHUNK - 1) // CHUNK
    for i in range(0, len(todo), CHUNK):
        (outdir / f"chunk_{i // CHUNK:02d}.json").write_text(json.dumps(todo[i:i + CHUNK], ensure_ascii=False))
    print(f"{len(slim)} companies in scope; cache hits {hits}, to classify {len(todo)} "
          f"-> {n_chunks} chunks of <= {CHUNK}")
    if not todo:
        print("  nothing to classify — run 04b_merge_and_sample.py directly")
        return
    base_shares = []
    for i in range(n_chunks):
        ch = json.loads((outdir / f"chunk_{i:02d}.json").read_text())
        base_shares.append(sum(1 for c in ch if c["batch"] in set(BASELINE_BATCHES)) / len(ch))
    print(f"  baseline share per chunk: min {min(base_shares):.0%} / max {max(base_shares):.0%} (want ~equal)")


if __name__ == "__main__":
    main()
