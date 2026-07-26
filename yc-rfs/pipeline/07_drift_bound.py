#!/usr/bin/env python3
"""
Drift analysis: distinguish vocabulary shifts from substantive YC funding shifts.

Computes match rates (baseline vs RFS-era) across slices:
- Overall
- AI-tagged companies only
- Non-AI-tagged companies only
- By vocabulary intensity terciles
"""

import json
import re
from collections import defaultdict
from pathlib import Path
import statistics

# Load data
def load_companies():
    """Load the full in-scope company list (written by 04_prepare_classification)."""
    root = Path(__file__).resolve().parent.parent
    with open(root / "data/derived/classify_scope.json") as f:
        return {c['id']: c for c in json.load(f)}

def load_classifications():
    """Load classifications from JSONL."""
    classifications = {}
    with open("data/derived/classifications.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            classifications[rec['id']] = rec.get('matches', [])
    return classifications

# Define baseline and RFS-era
BASELINE_BATCHES = {"Winter 2022", "Summer 2022", "Winter 2023", "Summer 2023", "Winter 2024"}
AI_TAGS = {"Artificial Intelligence", "AI", "Generative AI", "Machine Learning",
           "AI Assistant", "Conversational AI", "AIOps", "AI-powered Drug Discovery"}

# AI-ish keywords for vocabulary intensity
AI_KEYWORDS = {"agent", "llm", "gpt", "ai-", "ai ", "copilot",
               "foundation model", "autonomous", "machine learning", "neural"}

def count_ai_keywords(text):
    """Count AI-ish keywords in lowercased text."""
    if not text:
        return 0
    text_lower = text.lower()
    count = 0
    for kw in AI_KEYWORDS:
        count += text_lower.count(kw)
    return count

def is_baseline(batch):
    return batch in BASELINE_BATCHES

def has_ai_tag(company):
    """Check if company has any AI tag."""
    return any(tag in AI_TAGS for tag in company.get('tags', []))

def has_any_match(matches):
    """Check if classification has any match."""
    return len(matches) > 0

def has_strong_match(matches):
    """Check if classification has any strong match."""
    return any(m.get('confidence') == 'strong' for m in matches)

def main():
    print("Loading data...")
    companies_by_id = load_companies()
    classifications = load_classifications()

    # Merge and filter to companies with classifications
    companies = []
    for cid, company in companies_by_id.items():
        if cid in classifications:
            company['matches'] = classifications[cid]
            companies.append(company)

    print(f"Total companies with classifications: {len(companies)}")

    # Split into eras
    baseline_cos = [c for c in companies if is_baseline(c['batch'])]
    rfs_cos = [c for c in companies if not is_baseline(c['batch'])]

    baseline_ai_cos = [c for c in baseline_cos if has_ai_tag(c)]
    baseline_non_ai_cos = [c for c in baseline_cos if not has_ai_tag(c)]
    rfs_ai_cos = [c for c in rfs_cos if has_ai_tag(c)]
    rfs_non_ai_cos = [c for c in rfs_cos if not has_ai_tag(c)]

    print(f"Baseline: {len(baseline_cos)} ({len(baseline_ai_cos)} AI-tagged, {len(baseline_non_ai_cos)} non-AI)")
    print(f"RFS-era: {len(rfs_cos)} ({len(rfs_ai_cos)} AI-tagged, {len(rfs_non_ai_cos)} non-AI)")

    # === 1. OVERALL MATCH RATES ===
    def match_rate(cos, any_or_strong='any'):
        if not cos:
            return 0.0
        if any_or_strong == 'any':
            matched = sum(1 for c in cos if has_any_match(c['matches']))
        else:  # strong
            matched = sum(1 for c in cos if has_strong_match(c['matches']))
        return matched / len(cos)

    baseline_any = match_rate(baseline_cos, 'any')
    baseline_strong = match_rate(baseline_cos, 'strong')
    rfs_any = match_rate(rfs_cos, 'any')
    rfs_strong = match_rate(rfs_cos, 'strong')

    print("\n" + "="*70)
    print("1. OVERALL MATCH RATES")
    print("="*70)
    print(f"Any-match:    Baseline {baseline_any:.3f} → RFS-era {rfs_any:.3f}  (gap: {rfs_any - baseline_any:+.3f})")
    print(f"Strong-match: Baseline {baseline_strong:.3f} → RFS-era {rfs_strong:.3f}  (gap: {rfs_strong - baseline_strong:+.3f})")

    # === 2. AI-TAGGED SLICE ===
    baseline_ai_any = match_rate(baseline_ai_cos, 'any')
    baseline_ai_strong = match_rate(baseline_ai_cos, 'strong')
    rfs_ai_any = match_rate(rfs_ai_cos, 'any')
    rfs_ai_strong = match_rate(rfs_ai_cos, 'strong')

    print("\n" + "="*70)
    print("2. AI-TAGGED COMPANIES ONLY")
    print("="*70)
    print(f"Baseline: {len(baseline_ai_cos)} companies")
    print(f"RFS-era: {len(rfs_ai_cos)} companies")
    print(f"Any-match:    Baseline {baseline_ai_any:.3f} → RFS-era {rfs_ai_any:.3f}  (gap: {rfs_ai_any - baseline_ai_any:+.3f})")
    print(f"Strong-match: Baseline {baseline_ai_strong:.3f} → RFS-era {rfs_ai_strong:.3f}  (gap: {rfs_ai_strong - baseline_ai_strong:+.3f})")

    # === 3. NON-AI-TAGGED SLICE ===
    baseline_non_any = match_rate(baseline_non_ai_cos, 'any')
    baseline_non_strong = match_rate(baseline_non_ai_cos, 'strong')
    rfs_non_any = match_rate(rfs_non_ai_cos, 'any')
    rfs_non_strong = match_rate(rfs_non_ai_cos, 'strong')

    print("\n" + "="*70)
    print("3. NON-AI-TAGGED COMPANIES ONLY")
    print("="*70)
    print(f"Baseline: {len(baseline_non_ai_cos)} companies")
    print(f"RFS-era: {len(rfs_non_ai_cos)} companies")
    print(f"Any-match:    Baseline {baseline_non_any:.3f} → RFS-era {rfs_non_any:.3f}  (gap: {rfs_non_any - baseline_non_any:+.3f})")
    print(f"Strong-match: Baseline {baseline_non_strong:.3f} → RFS-era {rfs_non_strong:.3f}  (gap: {rfs_non_strong - baseline_non_strong:+.3f})")

    # === 4. VOCABULARY INTENSITY CONTROL ===
    # Compute keyword count for all companies
    for c in companies:
        text = (c.get('one_liner', '') or '') + " " + (c.get('description', '') or '')
        c['ai_keyword_count'] = count_ai_keywords(text)

    # Compute tercile boundaries pooled across all eras
    all_keyword_counts = [c['ai_keyword_count'] for c in companies]
    tercile_33 = sorted(all_keyword_counts)[len(all_keyword_counts) // 3]
    tercile_67 = sorted(all_keyword_counts)[2 * len(all_keyword_counts) // 3]

    def get_tercile(count):
        if count <= tercile_33:
            return 'Low'
        elif count <= tercile_67:
            return 'Mid'
        else:
            return 'High'

    for c in companies:
        c['tercile'] = get_tercile(c['ai_keyword_count'])

    # Compute match rates by (era, tercile)
    terciles = ['Low', 'Mid', 'High']
    match_by_tercile = {}

    for tercile in terciles:
        baseline_tercile = [c for c in baseline_cos if c['tercile'] == tercile]
        rfs_tercile = [c for c in rfs_cos if c['tercile'] == tercile]

        b_any = match_rate(baseline_tercile, 'any')
        b_strong = match_rate(baseline_tercile, 'strong')
        r_any = match_rate(rfs_tercile, 'any')
        r_strong = match_rate(rfs_tercile, 'strong')

        match_by_tercile[tercile] = {
            'baseline': {'n': len(baseline_tercile), 'any': b_any, 'strong': b_strong},
            'rfs_era': {'n': len(rfs_tercile), 'any': r_any, 'strong': r_strong},
            'gap_any': r_any - b_any,
            'gap_strong': r_strong - b_strong,
        }

    print("\n" + "="*70)
    print("4. MATCH RATES BY AI VOCABULARY INTENSITY TERCILE")
    print("="*70)
    print(f"Tercile boundaries: Low ≤ {tercile_33} | Mid ≤ {tercile_67} | High > {tercile_67} keywords")
    print()

    for tercile in terciles:
        m = match_by_tercile[tercile]
        print(f"{tercile} vocabulary intensity:")
        print(f"  Baseline: n={m['baseline']['n']}, any={m['baseline']['any']:.3f}, strong={m['baseline']['strong']:.3f}")
        print(f"  RFS-era:  n={m['rfs_era']['n']}, any={m['rfs_era']['any']:.3f}, strong={m['rfs_era']['strong']:.3f}")
        print(f"  Gap:      any={m['gap_any']:+.3f}, strong={m['gap_strong']:+.3f}")

    # === 5. VOCABULARY DRIFT ===
    baseline_ai_tag_share = len(baseline_ai_cos) / len(baseline_cos)
    rfs_ai_tag_share = len(rfs_ai_cos) / len(rfs_cos)

    baseline_keyword_mean = statistics.mean(c['ai_keyword_count'] for c in baseline_cos)
    rfs_keyword_mean = statistics.mean(c['ai_keyword_count'] for c in rfs_cos)

    print("\n" + "="*70)
    print("5. VOCABULARY DRIFT ACROSS ERAS")
    print("="*70)
    print(f"Share with ≥1 AI tag: Baseline {baseline_ai_tag_share:.1%} → RFS-era {rfs_ai_tag_share:.1%}")
    print(f"Mean AI keyword count: Baseline {baseline_keyword_mean:.2f} → RFS-era {rfs_keyword_mean:.2f}")

    # === OUTPUT JSON ===
    output = {
        'overall': {
            'baseline': {'n': len(baseline_cos), 'any_match': baseline_any, 'strong_match': baseline_strong},
            'rfs_era': {'n': len(rfs_cos), 'any_match': rfs_any, 'strong_match': rfs_strong},
            'gap_any_match': rfs_any - baseline_any,
            'gap_strong_match': rfs_strong - baseline_strong,
        },
        'ai_tagged': {
            'baseline': {'n': len(baseline_ai_cos), 'any_match': baseline_ai_any, 'strong_match': baseline_ai_strong},
            'rfs_era': {'n': len(rfs_ai_cos), 'any_match': rfs_ai_any, 'strong_match': rfs_ai_strong},
            'gap_any_match': rfs_ai_any - baseline_ai_any,
            'gap_strong_match': rfs_ai_strong - baseline_ai_strong,
        },
        'non_ai_tagged': {
            'baseline': {'n': len(baseline_non_ai_cos), 'any_match': baseline_non_any, 'strong_match': baseline_non_strong},
            'rfs_era': {'n': len(rfs_non_ai_cos), 'any_match': rfs_non_any, 'strong_match': rfs_non_strong},
            'gap_any_match': rfs_non_any - baseline_non_any,
            'gap_strong_match': rfs_non_strong - baseline_non_strong,
        },
        'vocabulary_intensity': match_by_tercile,
        'vocabulary_drift': {
            'ai_tag_share_baseline': baseline_ai_tag_share,
            'ai_tag_share_rfs_era': rfs_ai_tag_share,
            'ai_tag_share_change': rfs_ai_tag_share - baseline_ai_tag_share,
            'mean_keyword_count_baseline': baseline_keyword_mean,
            'mean_keyword_count_rfs_era': rfs_keyword_mean,
            'mean_keyword_count_change': rfs_keyword_mean - baseline_keyword_mean,
        },
        'tercile_boundaries': {
            'low_max': tercile_33,
            'mid_max': tercile_67,
        },
    }

    with open("data/derived/drift_bound.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nJSON output written to data/derived/drift_bound.json")

    # === INTERPRETATION ===
    print("\n" + "="*70)
    print("INTERPRETATION")
    print("="*70)

    # If gap persists in AI-tagged slice, likely substantive
    ai_gap_any = rfs_ai_any - baseline_ai_any
    non_ai_gap_any = rfs_non_any - baseline_non_any

    # If gap collapses within terciles, likely vocabulary
    tercile_gaps = [m['gap_any'] for m in match_by_tercile.values()]
    tercile_gap_range = max(tercile_gaps) - min(tercile_gaps)

    print()
    print(f"The overall any-match gap is {rfs_any - baseline_any:+.3f}.")
    print(f"Within AI-tagged companies: {ai_gap_any:+.3f}")
    print(f"Within non-AI-tagged companies: {non_ai_gap_any:+.3f}")
    print()

    print(f"Vocabulary did shift: AI tag share increased {rfs_ai_tag_share - baseline_ai_tag_share:+.1%},")
    print(f"and mean AI keyword count increased {rfs_keyword_mean - baseline_keyword_mean:+.2f}.")
    print()

    # Interpret
    if abs(ai_gap_any) > 0.1 and abs(non_ai_gap_any) < 0.05:
        assessment = "MOSTLY SUBSTANTIVE"
        reason = "Gap is large within AI-tagged companies but small in non-AI; real shift in AI focus."
    elif abs(ai_gap_any) < 0.05 and abs(non_ai_gap_any) < 0.05:
        assessment = "MOSTLY VOCABULARY"
        reason = "Gap disappears within fixed AI-tag slices; the change is tagging/description vocabulary, not funding priorities."
    elif max(abs(g) for g in tercile_gaps) < 0.05:
        assessment = "MOSTLY VOCABULARY"
        reason = "Within vocabulary-intensity terciles, the gap collapses; companies are using more AI language but YC's funding patterns for them haven't shifted."
    else:
        assessment = "MIXED"
        reason = "Evidence splits: some slices show substantive shift (AI-focused cohorts), others show vocabulary drift."

    print(f"VERDICT: {assessment}")
    print(f"Reasoning: {reason}")

if __name__ == '__main__':
    main()
