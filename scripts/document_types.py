"""
Classify each page by document type and report distribution.
"""
import json, re
from collections import Counter
from pathlib import Path

pages = json.loads(open("full_text.json").read())

DOC_HEADER = re.compile(
    r"^\s*(\d+)\s*[-–]\s*(\d{2}-\d{2}-\d{4})\s*[-–]\s*(.+?)(?:\n|$)",
    re.MULTILINE,
)

TYPE_KEYWORDS = {
    "email":        re.compile(r"\bemail(s)?\b", re.I),
    "chat":         re.compile(r"\bgoogle chat\b|\bmessenger exchange\b|\bwhatsapp\b", re.I),
    "meeting":      re.compile(r"\bmeeting(s)?\b", re.I),
    "letter":       re.compile(r"\bletter\b", re.I),
    "transcript":   re.compile(r"\btranscript\b|\binterview\b", re.I),
    "note":         re.compile(r"\bnote(s)?\b|\bbriefing\b", re.I),
}

EMAIL_HEADER = re.compile(r"^From:\s+.+$", re.MULTILINE)
CHAT_MSG     = re.compile(r"\[\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}\]")
TRANSCRIPT   = re.compile(r"^(Tucker Carlson|Interviewer|Q:|A:)\s+", re.MULTILINE)
METHODOLOGY  = re.compile(r"humble address|commissioning|redaction|methodology", re.I)

def classify(page):
    t = page["text"]
    if CHAT_MSG.search(t):        return "chat"
    if EMAIL_HEADER.search(t):    return "email"
    if TRANSCRIPT.search(t):      return "transcript"
    if METHODOLOGY.search(t):     return "methodology"
    if len(t.strip()) < 50:       return "blank/image"
    return "other"

counts = Counter(classify(p) for p in pages)
print("Document type distribution across all pages:")
for dtype, n in counts.most_common():
    pct = 100 * n / len(pages)
    print(f"  {dtype:<20} {n:>4}  ({pct:.1f}%)")

# Count TOC entries
all_text = "\n".join(p["text"] for p in pages)
toc_entries = DOC_HEADER.findall(all_text)
print(f"\nTOC-style document headers found: {len(toc_entries)}")

# Show doc type breakdown from TOC descriptions
toc_types = Counter()
for _, _, desc in toc_entries:
    for dtype, pat in TYPE_KEYWORDS.items():
        if pat.search(desc):
            toc_types[dtype] += 1
            break
    else:
        toc_types["other"] += 1

print("Document types mentioned in TOC entries:")
for dtype, n in toc_types.most_common():
    print(f"  {dtype:<15} {n:>4}")
