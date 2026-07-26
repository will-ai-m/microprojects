"""Canonicalize the 96 (batch, theme) RFS pairs into canonical themes.

The MAPPING table below is the human-reviewed clustering decision (PRD 5.1):
merge only clear repeats of the same startup space; keep distinctive one-offs
as their own theme. Reads data/raw/rfs/*.json + data/derived/theme_summaries.json,
writes data/derived/themes.json.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
RFS_DIR = ROOT / "data" / "raw" / "rfs"
DERIVED = ROOT / "data" / "derived"

BATCH_FILES = [
    "summer-2024", "winter-2025", "spring-2025", "summer-2025",
    "fall-2025", "spring-2026", "summer-2026", "fall-2026",
]

# canonical_id -> (display name, [(batch, exact raw title), ...])
MAPPING = {
    "defense-tech": ("Defense technology", [
        ("Summer 2024", "New Defense Technology"),
        ("Summer 2026", "Counter-Swarm Defense"),
        ("Fall 2026", "The Future of American Defense"),
    ]),
    "public-safety": ("Public safety technology", [
        ("Winter 2025", "Public Safety Technology"),
    ]),
    "stablecoins-crypto": ("Stablecoins & crypto financial rails", [
        ("Summer 2024", "Stablecoin Finance"),
        ("Winter 2025", "Stablecoins 2.0"),
        ("Spring 2026", "Stablecoin Financial Services"),
        ("Fall 2026", "The Best Time to Build in Crypto"),
    ]),
    "govtech": ("Government software & AI for government", [
        ("Winter 2025", "Government Software"),
        ("Fall 2025", "Using LLMs Instead of Government Consulting"),
        ("Spring 2026", "AI for Government"),
        ("Spring 2026", "Infra for Government Fraud Hunters"),
    ]),
    "education-tutoring": ("AI tutoring & the future of education", [
        ("Summer 2025", "AI Personal Tutor for Everyone"),
        ("Summer 2025", "The Future of Education"),
        ("Fall 2025", "Retraining Workers for the AI Economy"),
        ("Fall 2026", "The Primer"),
    ]),
    "enterprise-software": ("AI-native enterprise software (ERP/CRM/SaaS replacement)", [
        ("Summer 2024", "New Enterprise Resource Planning Software"),
        ("Summer 2024", "AI to Build Enterprise Software"),
        ("Fall 2025", "AI Native Enterprise Software"),
        ("Summer 2026", "SaaS Challengers"),
        ("Summer 2026", "The AI Operating System for Companies"),
        ("Summer 2026", "Company Brain"),
    ]),
    "back-office-automation": ("LLM automation of back-office processes", [
        ("Summer 2024", "LLMs for Manual Back Office Processes in Legacy Enterprises"),
    ]),
    "compliance": ("AI compliance & audit", [
        ("Spring 2025", "Compliance and Audit"),
        ("Fall 2026", "AI-Native Compliance Infrastructure"),
    ]),
    "open-source": ("Commercial open source", [
        ("Summer 2024", "Commercial Open Source Companies"),
        ("Spring 2025", "AI Commercial Open Source Software (AICOSS)"),
    ]),
    "robotics": ("Robotics & robot software tools", [
        ("Summer 2024", "Applying Machine Learning to Robotics"),
        ("Summer 2025", "Software Tools To Make Robots"),
    ]),
    "physical-world-ops": ("Operating systems for physical work", [
        ("Spring 2026", "AI Guidance for Physical Work"),
        ("Fall 2026", "New Operating Systems for the Physical World"),
    ]),
    "physical-world-data": ("Sensor data for the physical world", [
        ("Fall 2026", "Data for the Real World"),
    ]),
    "healthcare-ai": ("Healthcare AI & diagnostics", [
        ("Summer 2024", "A Way to End Cancer"),
        ("Summer 2025", "Healthcare AI"),
        ("Summer 2026", "AI Personalized Medicine"),
    ]),
    "bio-foundation-models": ("Foundation models for biology", [
        ("Summer 2024", "Foundation Models for Biological Systems"),
    ]),
    "science-ai": ("AI for scientific advancement", [
        ("Summer 2025", "AI for Scientific Advancement"),
    ]),
    "healthcare-services": ("Healthcare delivery models (MSO, middlemen removal)", [
        ("Summer 2024", "The Managed Service Organization Model for Healthcare"),
        ("Summer 2024", "Eliminating Middlemen in Healthcare"),
    ]),
    "space": ("Space companies & space industry", [
        ("Winter 2025", "New Space Companies"),
        ("Summer 2026", "Electronics in Space"),
        ("Summer 2026", "Industrial Capabilities in Space"),
    ]),
    "engineering-tools-ai": ("AI-aided engineering (CAD/CAE) tools", [
        ("Winter 2025", "AI-Aided Engineering Tools"),
    ]),
    "chip-design-ai": ("AI for chip design & hardware code", [
        ("Winter 2025", "LLMs for Chip Design"),
        ("Spring 2025", "AI Coding Agents for Hardware-Optimized Code"),
    ]),
    "compute-infrastructure": ("AI compute infrastructure & datacenters", [
        ("Spring 2025", "Datacenters"),
        ("Spring 2025", "Inference AI Infrastructure in the World of Test-Time Compute"),
        ("Summer 2026", "Inference Chips for Agent Workflows"),
        ("Fall 2026", "Compute at Sea"),
    ]),
    "manufacturing-reshoring": ("Manufacturing, reshoring & hardware supply chain", [
        ("Winter 2025", "Manufacture in the USA"),
        ("Spring 2026", "Modern Metal Mills"),
        ("Summer 2026", "Hardware Supply Chain"),
        ("Summer 2026", "Supply Chain 2.0 for Semiconductors"),
    ]),
    "fintech": ("Fintech & AI financial services", [
        ("Winter 2025", "Fintech 2.0"),
        ("Summer 2025", "AI for Personal Finance"),
        ("Spring 2026", "AI-Native Hedge Funds"),
    ]),
    "agent-infrastructure": ("AI agent infrastructure & devtools", [
        ("Spring 2025", "Devtools for AI Agents"),
        ("Spring 2025", "B2A: Software Where the Customers Will All Be Agents"),
        ("Spring 2025", "Browser & Computer Automation"),
        ("Summer 2025", "Internal Agent Builder"),
        ("Fall 2025", "Infrastructure for Multi-Agent Systems"),
        ("Summer 2026", "Software for Agents"),
        ("Fall 2026", "Multiplayer AI"),
    ]),
    "vertical-agents": ("Vertical AI agents", [
        ("Spring 2025", "Vertical AI Agents"),
    ]),
    "personal-assistants": ("AI personal assistants & staff", [
        ("Spring 2025", "AI Personal Staff for Everyone"),
        ("Summer 2025", "AI Personal Assistant"),
        ("Summer 2025", "AI Voice Assistants for Email"),
    ]),
    "voice-ai": ("Voice AI", [
        ("Summer 2025", "Voice AI"),
    ]),
    "consumer-ai": ("Consumer AI products at billion-user scale", [
        ("Fall 2026", "AI-Powered Consumer Products for 1 Billion People"),
    ]),
    "aging-population": ("AI for the aging population", [
        ("Fall 2026", "AI for the Aging Population"),
    ]),
    "residential-security": ("AI residential security", [
        ("Summer 2025", "AI Residential Security"),
    ]),
    "software-engineering-ai": ("AI-powered software engineering", [
        ("Spring 2025", "The Future of Software Engineering"),
        ("Spring 2026", "Cursor for Product Managers"),
        ("Fall 2026", "Self-Maintaining APIs"),
    ]),
    "devtools-internal": ("Devtools inspired by internal tools", [
        ("Summer 2024", "Developer Tools Inspired by Existing Internal Tools"),
    ]),
    "small-models-training": ("Small/fine-tuned models & training tooling", [
        ("Summer 2024", "Small Fine-tuned Models as an Alternative to Giant Generic Ones"),
        ("Spring 2026", "Make LLMs Easy to Train"),
    ]),
    "explainable-ai": ("Explainable AI", [
        ("Summer 2024", "Explainable AI"),
    ]),
    "ml-simulation": ("ML simulation of the physical world", [
        ("Summer 2024", "Using Machine Learning to Simulate the Physical World"),
    ]),
    "spatial-computing": ("Spatial computing (AR/VR)", [
        ("Summer 2024", "Spatial Computing"),
    ]),
    "large-spatial-models": ("Large spatial models", [
        ("Spring 2026", "Large Spatial Models"),
    ]),
    "video-generation": ("Video generation as a primitive", [
        ("Fall 2025", "Video Generation as a Primitive"),
    ]),
    "discovery-engines": ("AI-native scientific discovery engines (closed design-make-test-analyze loops)", [
        ("Summer 2026", "AI-Native Discovery Engines"),
    ]),
    "ai-native-services": ("Full-stack AI-native service companies", [
        ("Summer 2025", "Full-stack AI Companies"),
        ("Fall 2025", "The First 10-person, $100B Company"),
        ("Spring 2026", "AI-Native Agencies"),
        ("Summer 2026", "AI-Native Service Companies"),
    ]),
    "one-million-jobs": ("One million jobs", [
        ("Winter 2025", "One Million Jobs 2.0"),
    ]),
    "secure-ai-appstore": ("Secure AI app store", [
        ("Spring 2025", "A Secure AI App Store"),
    ]),
    "dynamic-interfaces": ("Dynamic software interfaces", [
        ("Summer 2026", "Dynamic Software Interfaces"),
    ]),
    "cloud-small-software": ("Cloud for small/personal software", [
        ("Fall 2026", "A Cloud for Small Software"),
    ]),
    "agriculture": ("AI for agriculture", [
        ("Summer 2026", "AI for Low-Pesticide Agriculture"),
    ]),
    "enterprise-sales": ("Selling to huge companies", [
        ("Summer 2026", "Startups That Want to Sell to Huge Companies"),
    ]),
    "human-verification": ("Human verification & deepfake defense", [
        ("Fall 2026", "Proving You're Human"),
    ]),
    "ai-research-labs": ("AI research labs", [
        ("Summer 2025", "AI Research Labs"),
    ]),
    "design-founders": ("Design-led founders/products", [
        ("Summer 2025", "More Design Founders"),
    ]),
}


# Scope text that REPLACES the LLM-merged summaries for themes whose boundary
# proved ambiguous in practice. `vertical-agents` and `agent-infrastructure`
# together carried a large share of all matches and the boundary between them
# drove a 30x swing in the headline shift, so it is pinned explicitly here
# rather than left to the merged summaries.
SCOPE_OVERRIDES = {
    "agent-infrastructure": (
        "The CUSTOMER is a developer or an AI agent, and the product is horizontal plumbing that is "
        "domain-agnostic: agent SDKs/frameworks, orchestration, sandboxes and browsers for agents to act in, "
        "agent observability/eval/debugging, memory and context stores, agent auth/payments/identity rails, "
        "control planes for running agents, or software built to be consumed by agents rather than humans. "
        "It would work for any industry. INCLUDE a company selling a platform or toolkit so OTHER teams build "
        "their own agents, even when sold to enterprises. EXCLUDE a finished agent that performs one industry's "
        "work (that is vertical-agents) and EXCLUDE horizontal business software that merely uses agents internally."
    ),
    "vertical-agents": (
        "The CUSTOMER is an end business in a SPECIFIC industry or job function, and the product is a working "
        "agent that performs that industry's actual labour: medical billing, tax prep, insurance claims, "
        "recruiting screens, dental or clinic front desk, freight dispatch, legal intake, audit, construction "
        "scheduling, restaurant ops, and the like. The value is embedded domain knowledge and workflow, not the "
        "plumbing. INCLUDE a finished agent doing one industry's or one function's work even when the underlying "
        "technology is impressive. EXCLUDE developer platforms for building agents (that is agent-infrastructure) "
        "and EXCLUDE generic horizontal software with no industry specialisation."
    ),
}
NEITHER_NOTE = (
    "NOTE on the two agent themes: horizontal business software that merely uses agents under the hood "
    "(a generic CRM, notetaker, or support-deflection tool with no industry specialisation and no developer "
    "surface) matches NEITHER agent theme. Matching both is legitimate only when a company genuinely ships "
    "both a developer platform and its own vertical agents; that should be rare."
)


def main():
    raw = {}  # (batch, title) -> theme dict
    for slug in BATCH_FILES:
        data = json.loads((RFS_DIR / f"{slug}.json").read_text())
        for t in data["themes"]:
            raw[(data["batch"], t["title"])] = t

    summaries = {}
    sfile = DERIVED / "theme_summaries.json"
    if sfile.exists():
        for s in json.loads(sfile.read_text()):
            summaries[(s["batch"], s["title"])] = s["summary"]

    # Coverage check: every raw pair must map to exactly one canonical theme
    mapped = [(b, t) for _, (_, members) in MAPPING.items() for (b, t) in members]
    dupes = {p for p in mapped if mapped.count(p) > 1}
    missing_in_raw = [p for p in mapped if p not in raw]
    unmapped = [p for p in raw if p not in set(mapped)]
    if dupes or missing_in_raw or unmapped:
        print("DUPES:", dupes, file=sys.stderr)
        print("MAPPED-BUT-NOT-IN-RAW:", missing_in_raw, file=sys.stderr)
        print("RAW-BUT-UNMAPPED:", unmapped, file=sys.stderr)
        sys.exit(1)

    themes = []
    for cid, (name, members) in MAPPING.items():
        member_objs = []
        for batch, title in members:
            m = {"batch": batch, "title": title, "author": raw[(batch, title)]["author"]}
            if (batch, title) in summaries:
                m["summary"] = summaries[(batch, title)]
            member_objs.append(m)
        entry = {
            "id": cid,
            "name": name,
            "active_batches": sorted({b for b, _ in members}),
            "members": member_objs,
        }
        if cid in SCOPE_OVERRIDES:
            entry["scope_override"] = SCOPE_OVERRIDES[cid]
        themes.append(entry)

    DERIVED.mkdir(parents=True, exist_ok=True)
    out = DERIVED / "themes.json"
    out.write_text(json.dumps(themes, indent=1, ensure_ascii=False))
    n_members = sum(len(t["members"]) for t in themes)
    n_summ = sum(1 for t in themes for m in t["members"] if "summary" in m)
    print(f"{len(themes)} canonical themes, {n_members} member pairs, {n_summ} with summaries -> {out}")


if __name__ == "__main__":
    main()
