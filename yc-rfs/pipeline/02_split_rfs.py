"""Split data/raw/rfs/_all.json (output of 02_fetch_rfs.js) into per-batch files."""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
RFS_DIR = ROOT / "data" / "raw" / "rfs"

batches = json.loads((RFS_DIR / "_all.json").read_text())
if isinstance(batches, str):  # playwright-cli --raw double-encodes the returned string
    batches = json.loads(batches)
for b in batches:
    slug = b["batch"].lower().replace(" ", "-")
    (RFS_DIR / f"{slug}.json").write_text(json.dumps(b, indent=1, ensure_ascii=False))
    n = len(b["themes"])
    authors = sum(1 for t in b["themes"] if t["author"])
    leaks = sum(1 for t in b["themes"] if t["description"].startswith("By "))
    print(f"{slug}: {n} themes, {authors} authors, {leaks} byline-leaks")
