"""
Segment the full page stream into individual document units.

Key challenge: documents can start mid-page (not always at page top).
Strategy: find ALL doc headers anywhere in each page text, split pages at
those boundaries, then assemble runs of text chunks into units.

Output: documents.json
"""
import json, re
from pathlib import Path
from collections import Counter

pages = json.loads(open("full_text.json").read())

# ── Patterns ────────────────────────────────────────────────────────────────

# Matches a doc header anywhere in text
# Handles: "3.-", "3 -", "93 _-", "3 –", OCR underscores as em-dashes
DOC_HEADER_RE = re.compile(
    r"(?<!\d)"                              # not preceded by a digit
    r"(\d{1,3})"                            # doc number (1-3 digits)
    r"[.\s]*\s*[-–_]+\s*"                   # separator (OCR-tolerant)
    r"(\d{2}-\d{2}-\d{4})"                 # date DD-MM-YYYY
    r"\s*[-–_]+\s*"                         # separator
    r"(.{5,80})",                           # description start (5-80 chars on same line)
    re.MULTILINE,
)

TYPE_PATTERNS = [
    ("chat",       re.compile(r"google chat|whatsapp|messenger exchange|chat message", re.I)),
    ("meeting",    re.compile(r"\bmeeting[s]?\b", re.I)),
    ("letter",     re.compile(r"\bletter[s]?\b", re.I)),
    ("transcript", re.compile(r"\btranscript[s]?\b|\binterview\b", re.I)),
    ("note",       re.compile(r"\bnote[s]?\b|\bbriefing[s]?\b|\battachment\b", re.I)),
    ("email",      re.compile(r"\bemail[s]?\b", re.I)),
]

PERSON_ROLE_RE = re.compile(
    r"([A-Z][a-zA-Z'\-\. ]+?)\s*"
    r"\(([^)]*(?:CO|FCDO|MoD|HO|No\.10|NCSC|HMT|UKSV|NSV|GSB|SIS|"
    r"No 10|Treasury|Embassy|Cabinet Office|Global Counsel)[^)]*)\)",
)


def classify_type(desc):
    for doc_type, pat in TYPE_PATTERNS:
        if pat.search(desc):
            return doc_type
    return "document"


def extract_participants(desc):
    result = []
    for name, role_dept in PERSON_ROLE_RE.findall(desc):
        name = name.strip()
        parts = [p.strip() for p in role_dept.strip().rsplit(",", 1)]
        role = parts[0] if len(parts) == 2 else role_dept.strip()
        dept = parts[1] if len(parts) == 2 else ""
        result.append({"name": name, "role": role, "dept": dept})
    return result


def find_headers_in_text(text, valid_range=(1, 200)):
    """
    Return list of (match_start, unit_id, date, desc_snippet) for all doc
    headers found in text, filtered to valid_range of unit IDs.
    """
    results = []
    for m in DOC_HEADER_RE.finditer(text):
        uid = int(m.group(1))
        lo, hi = valid_range
        if lo <= uid <= hi:
            desc = m.group(3).split("\n")[0].strip()
            results.append((m.start(), uid, m.group(2), desc))
    return results


def is_toc_page(text):
    return len(DOC_HEADER_RE.findall(text)) >= 4


# ── Build a stream of (source, page_num, chunk_text, header_or_None) ────────

CONTENT_START = 30

# Each element is either:
#   ("header", pnum, source, unit_id, date, desc)  — starts a new doc
#   ("body",   pnum, source, text)                  — continuation text

stream = []

for page in pages:
    pnum   = page["page"]
    text   = page["text"]
    source = page["source"]

    if pnum < CONTENT_START:
        continue
    if is_toc_page(text):
        continue

    headers = find_headers_in_text(text)

    if not headers:
        stream.append(("body", pnum, source, text))
        continue

    # Sort by position in case of multiple headers on one page
    headers.sort(key=lambda h: h[0])

    prev_pos = 0
    for pos, uid, date, desc in headers:
        # Text before this header → body chunk for current doc
        before = text[prev_pos:pos].strip()
        if before:
            stream.append(("body", pnum, source, before))

        # The header itself (grab up to 300 chars for full description)
        full_desc = text[pos: pos + 300].split("\n\n")[0].replace("\n", " ").strip()
        stream.append(("header", pnum, source, uid, date, full_desc))
        prev_pos = pos

    # Remaining text after last header → body
    remainder = text[prev_pos:].strip()
    # Strip the header line itself from remainder
    lines = remainder.split("\n")
    # Skip the header line(s) at the top of remainder
    body_lines = []
    skip = True
    for line in lines:
        if skip and DOC_HEADER_RE.search(line):
            continue
        skip = False
        body_lines.append(line)
    remainder = "\n".join(body_lines).strip()
    if remainder:
        stream.append(("body", pnum, source, remainder))


# ── Assemble stream into document units ──────────────────────────────────────

units = []
current = None
last_uid = 0

for item in stream:
    if item[0] == "header":
        _, pnum, source, uid, date, desc = item

        # Monotonicity guard (allow small OCR-induced jumps)
        if uid < last_uid - 3:
            # Treat as body text, not a real header
            if current:
                current["texts"].append(desc)
                current["sources"].append(source)
                current["pages"].append(pnum)
            continue

        last_uid = max(last_uid, uid)

        if current:
            units.append(current)

        current = {
            "unit_id":      uid,
            "date":         date,
            "type":         classify_type(desc),
            "description":  desc[:200],
            "participants": extract_participants(desc),
            "pages":        [pnum],
            "texts":        [],
            "sources":      [source],
        }

    else:  # body
        _, pnum, source, text = item
        if current:
            if text.strip():
                current["texts"].append(text)
            if pnum not in current["pages"]:
                current["pages"].append(pnum)
            current["sources"].append(source)

if current:
    units.append(current)

# ── Post-process ─────────────────────────────────────────────────────────────

def source_mix(sources):
    s = set(sources)
    if s == {"pdf"}:  return "pdf"
    if s == {"ocr"}:  return "ocr"
    return "mixed"

output = []
for u in units:
    combined = "\n\n".join(t for t in u["texts"] if t.strip())
    output.append({
        "unit_id":      u["unit_id"],
        "date":         u["date"],
        "type":         u["type"],
        "description":  u["description"],
        "participants": u["participants"],
        "page_count":   len(set(u["pages"])),
        "pages":        sorted(set(u["pages"])),
        "source_mix":   source_mix(u["sources"]),
        "text":         combined,
        "char_count":   len(combined),
    })

output.sort(key=lambda x: x["unit_id"])

# ── Stats ─────────────────────────────────────────────────────────────────────

print(f"Total document units: {len(output)}")
print(f"Unit ID range: {output[0]['unit_id']} → {output[-1]['unit_id']}")

seen = {u["unit_id"] for u in output}
missing = [i for i in range(1, output[-1]["unit_id"] + 1) if i not in seen]
print(f"Missing IDs:  {len(missing)} → {missing[:20]}")

type_counts = Counter(u["type"] for u in output)
print("\nType breakdown:")
for t, n in type_counts.most_common():
    print(f"  {t:<15} {n:>4}")

page_dist = Counter(u["page_count"] for u in output)
print("\nPages-per-unit distribution:")
for n in sorted(page_dist):
    bar = "█" * min(page_dist[n], 40)
    print(f"  {n:>3}p: {page_dist[n]:>4}  {bar}")

char_dist = [u["char_count"] for u in output]
print(f"\nChar count stats:")
print(f"  min={min(char_dist)}  max={max(char_dist)}  "
      f"mean={sum(char_dist)//len(char_dist)}  "
      f"total={sum(char_dist):,}")

mix = Counter(u["source_mix"] for u in output)
print(f"\nSource mix: {dict(mix)}")

print("\nSample units:")
for u in output[:5]:
    print(f"  [{u['unit_id']}] {u['date']} | {u['type']} | {u['page_count']}p | "
          f"{u['char_count']}c | {u['source_mix']}")
    print(f"       {u['description'][:100]}")
    for p in u["participants"]:
        print(f"         → {p['name']} ({p['role']}, {p['dept']})")
    print()

Path("documents.json").write_text(json.dumps(output, indent=2, ensure_ascii=False))
print(f"Saved {len(output)} units → documents.json")
