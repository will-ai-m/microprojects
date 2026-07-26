"""Classification cache keyed on (company payload, prompt version, model).

Re-running the pipeline should only re-classify companies whose input text or
classifier prompt actually changed. Re-chunking, re-ordering, or re-running
metrics must cost nothing.

Bump PROMPT_VERSION whenever the classification instructions or the theme
catalog change in a way that should invalidate existing labels.
"""
import hashlib
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
DERIVED = ROOT / "data" / "derived"
CACHE_PATH = DERIVED / "classification_cache.jsonl"

PROMPT_VERSION = "v3-sharp-agent-boundary-with-rationale"
MODEL = "claude-haiku-4-5"


def company_key(company, catalog_hash):
    """Stable hash of everything the classifier actually sees.

    Note: the key is content-based, not id-based. Two companies with byte-identical
    descriptions, tags and industry share one cache entry and therefore one label —
    which is correct (identical input, identical output), but means the cache can
    hold slightly fewer entries than there are companies in scope.
    """
    payload = {
        "one_liner": company.get("one_liner"),
        "description": company.get("description"),
        "industry": company.get("industry"),
        "tags": company.get("tags"),
    }
    blob = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    h = hashlib.sha256(f"{PROMPT_VERSION}|{MODEL}|{catalog_hash}|{blob}".encode()).hexdigest()
    return h[:16]


def catalog_hash():
    p = DERIVED / "theme_catalog.md"
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16] if p.exists() else "nocatalog"


def load():
    """key -> record"""
    if not CACHE_PATH.exists():
        return {}
    out = {}
    for line in CACHE_PATH.read_text().splitlines():
        if line.strip():
            rec = json.loads(line)
            out[rec["key"]] = rec
    return out


def write(entries):
    """entries: list of {key, id, matches, prompt_version, model}"""
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CACHE_PATH, "a") as f:
        for e in entries:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")


def rewrite(records):
    """Replace the cache wholesale (used to compact duplicates)."""
    with open(CACHE_PATH, "w") as f:
        for r in records.values():
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
