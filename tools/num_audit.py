#!/usr/bin/env python3
"""
Audit every number in src/pages/*.html (including visible <text> inside <svg>,
excluding SVG coordinates/attributes and HTML tags/attributes) and in the
metrics / interpretation / summary / positive / steps fields of atlas/data/tests.yaml
against C:/Users/ahmed/OneDrive/Desktop/cervical_evidence_verified.md and the
Rule 2.10 whitelist.
"""
import html
import pathlib
import re
import sys
import yaml

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = pathlib.Path(__file__).resolve().parent.parent
EVIDENCE_PATHS = [
    pathlib.Path(r"C:\Users\ahmed\OneDrive\Desktop\cervical_evidence_verified.md"),
    pathlib.Path(r"C:\Users\ahmed\OneDrive\Desktop\upgrade_evidence_verified.md"),
]
PAGES_DIR = ROOT / "src" / "pages"
YAML_PATH = ROOT / "atlas" / "data" / "tests.yaml"

WHITELIST_RULES = [
    (
        "Spinal level names (C0-T12, C1-C2, C4-7, C5-T1, etc.)",
        re.compile(r"\b(?:C[0-8]|T(?:1[0-2]|[1-9]))(?:\s*[\-\u2013\u2014/]\s*(?:C[0-8]|T(?:1[0-2]|[1-9])|[0-9]{1,2}))*\b"),
    ),
    (
        "WAD grades 0-IV (Grade 0, grades 0-IV, WAD 0-IV)",
        re.compile(r"\b(?:WAD|grades?|Grades?)\s*[0-4](?:\s*[\-\u2013\u2014/]\s*(?:[0-4]|IV|III|II|I))?\b"),
    ),
    (
        "Calculator scoring rules & item scales (NDI 0-50 / 0-100%, PSFS 0-10, NPRS 0-10, TSK-11)",
        re.compile(
            r"(?<![\d.])(?:NDI\s*\(?0[\-\u2013]50|0[\-\u2013]50\s*or\s*0[\-\u2013]100%|0[\-\u2013]100%|"
            r"PSFS\s*\(?0[\-\u2013]10|NPRS\s*\(?0[\-\u2013]10|0[\-\u2013]10\s*beside|"
            r"0[\-\u2013]10\)|0[\-\u2013]50\)|TSK-11)(?![\d.])"
        ),
    ),
    (
        "Page numbers (1-9, p1-p9) & Visit / week log numbers (1-12)",
        re.compile(
            r"(?<![\d.])(?:\b[pP][1-9](?:/[pP][1-9])*\b|\b[pP]age\s*[1-9]\b|"
            r"\bVisit\s*(?:[1-9]|1[0-2])\b|\bWk\s*(?:[1-9]|1[0-2])\b|"
            r"(?<![A-Za-z\d.])(?:[0-9]|1[0-2])(?![A-Za-z\d.]))"
        ),
    ),
]


def load_verified_numbers(md_path: pathlib.Path) -> set[str]:
    text = md_path.read_text(encoding="utf-8")
    # Exclude the Rejected section and anything below it
    if "## ❌ Rejected" in text:
        text = text.split("## ❌ Rejected", 1)[0]
    nums = set(re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", text))
    # Also include comma-stripped numbers (e.g., 1,246 -> 1246)
    for m in re.findall(r"\d{1,3}(?:,\d{3})+(?:\.\d+)?", text):
        nums.add(m)
        nums.add(m.replace(",", ""))
    return nums


def extract_svg_visible_text(svg_block: str) -> str:
    texts = re.findall(r"<text\b[^>]*>(.*?)</text>", svg_block, flags=re.DOTALL | re.IGNORECASE)
    cleaned = [re.sub(r"<[^>]+>", " ", t) for t in texts]
    return " ".join(cleaned)


def extract_html_visible_text(html_text: str) -> str:
    # Remove HTML comments
    s = re.sub(r"<!--.*?-->", " ", html_text, flags=re.DOTALL)
    # Replace <svg>...</svg> with only its visible <text> contents
    s = re.sub(
        r"<svg\b[^>]*>.*?</svg>",
        lambda m: " " + extract_svg_visible_text(m.group(0)) + " ",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # Strip remaining HTML tags
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return s


def apply_whitelist(text: str, counts: dict[str, int]) -> str:
    s = text
    for label, pattern in WHITELIST_RULES:
        matches = pattern.findall(s)
        if matches:
            counts[label] = counts.get(label, 0) + len(matches)
            s = pattern.sub(" ", s)
    return s


def collect_yaml_strings(obj) -> list[str]:
    out = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            out.extend(collect_yaml_strings(item))
    elif isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("url", "id", "free_full_text", "video"):
                continue
            out.extend(collect_yaml_strings(v))
    return out


def main() -> int:
    verified_nums = set()
    for ep in EVIDENCE_PATHS:
        verified_nums |= load_verified_numbers(ep)
    whitelist_counts: dict[str, int] = {label: 0 for label, _ in WHITELIST_RULES}
    unverified: list[tuple[str, str, str]] = []

    # 1. Audit src/pages/*.html
    page_files = sorted(PAGES_DIR.glob("p*.html"))
    total_html_nums = 0
    for pf in page_files:
        raw = pf.read_text(encoding="utf-8")
        vis = extract_html_visible_text(raw)
        vis = re.sub(r"(\d),(\d{3})\b", r"\1\2", vis)
        all_nums_in_page = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", vis)
        total_html_nums += len(all_nums_in_page)

        scrubbed = apply_whitelist(vis, whitelist_counts)
        for m in re.finditer(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", scrubbed):
            num = m.group(0)
            if num not in verified_nums:
                start = max(0, m.start() - 35)
                end = min(len(scrubbed), m.end() + 35)
                ctx = " ".join(scrubbed[start:end].split())
                unverified.append((pf.name, num, ctx))

    # 2. Audit atlas/data/tests.yaml (metrics, interpretation, summary, positive, steps)
    data = yaml.safe_load(YAML_PATH.read_text(encoding="utf-8"))
    cards = data if isinstance(data, list) else data.get("tests", [])
    target_fields = ("metrics", "interpretation", "summary", "positive", "steps")
    total_yaml_nums = 0
    for card in cards:
        cid = card.get("id", "<unknown>")
        for field in target_fields:
            if field not in card:
                continue
            strs = collect_yaml_strings(card[field])
            joined = " | ".join(strs)
            joined = re.sub(r"(\d),(\d{3})\b", r"\1\2", joined)
            all_nums_in_field = re.findall(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", joined)
            total_yaml_nums += len(all_nums_in_field)

            scrubbed = apply_whitelist(joined, whitelist_counts)
            for m in re.finditer(r"(?<![\d.])\d+(?:\.\d+)?(?![\d.])", scrubbed):
                num = m.group(0)
                if num not in verified_nums:
                    start = max(0, m.start() - 35)
                    end = min(len(scrubbed), m.end() + 35)
                    ctx = " ".join(scrubbed[start:end].split())
                    unverified.append((f"tests.yaml:{cid}.{field}", num, ctx))

    print("=" * 72)
    print("CERVICAL DOSSIER + ATLAS NUMBER AUDIT (Rule 2.10 & Section 6.3)")
    print("=" * 72)
    print("Evidence sources:")
    for ep in EVIDENCE_PATHS:
        print(f"  - {ep}")
    print(f"Verified tokens : {len(verified_nums)} distinct numeric values across 2 evidence files")
    print(f"Pages audited   : {len(page_files)} files ({total_html_nums} numeric tokens extracted incl. SVG <text>)")
    print(f"YAML audited    : {len(cards)} cards across {list(target_fields)} ({total_yaml_nums} numeric tokens)")
    print("-" * 72)
    print("Rule 2.10 Whitelist Applied:")
    for label, count in whitelist_counts.items():
        print(f"  - {label}: {count} matches")
    print("-" * 72)
    if unverified:
        print(f"UNVERIFIED NUMBERS FOUND: {len(unverified)}")
        for loc, num, ctx in unverified:
            print(f"  [!] {loc}: '{num}' in ...{ctx}...")
        return 1
    else:
        print("Unverified numbers count: 0")
        print("STATUS: PASS (0 unverified numbers)")
        return 0


if __name__ == "__main__":
    sys.exit(main())
