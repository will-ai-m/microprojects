"""Snapshot the yc-oss companies dataset into data/raw/."""
import json
import pathlib
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)

for name in ("companies/all.json", "meta.json"):
    url = f"https://yc-oss.github.io/api/{name}"
    dest = RAW / name.split("/")[-1].replace("all.json", "companies-all.json")
    with urllib.request.urlopen(url) as r:
        dest.write_bytes(r.read())
    print(f"{url} -> {dest}")

companies = json.loads((RAW / "companies-all.json").read_text())
print(f"{len(companies)} companies")
