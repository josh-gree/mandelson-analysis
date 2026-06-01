"""
Parse units tagged as content_type=letter.

Genuine letters (~5) follow British Embassy / official government letterhead format.
Misclassified units (~7) are email threads that happen to contain "Dear X" — flagged
but not deeply parsed. One unit (046) is unreadable OCR.
"""
import json, re
from pathlib import Path
from datetime import datetime

UNITS_DIR = Path("units")

# ── Date parsing ─────────────────────────────────────────────────────────────

MONTHS = {
    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,
    "sep":9,"sept":9,"oct":10,"nov":11,"dec":12,
}

DATE_LONG = re.compile(
    r"\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)\s+(\d{4})\b", re.I
)

def parse_date_iso(text):
    m = DATE_LONG.search(text)
    if m:
        day, month, year = int(m.group(1)), MONTHS[m.group(2).lower()], int(m.group(3))
        return f"{year}-{month:02d}-{day:02d}", m.group(0)
    return None, None


# ── Structural patterns ───────────────────────────────────────────────────────

FROM_ROLE    = re.compile(r"From the (Ambassador|Permanent Under-Secretary|[A-Z][a-z]+ [A-Z][a-z]+)", re.I)
SENDER_NAME  = re.compile(r"The Rt Hon\.?\s+((?:Lord|Sir|Dame)?\s*[A-Z][a-zA-Z\s\-]+?(?:PC|KCB|KC|MP|CBE|OBE)?)\b")
INSTITUTION  = re.compile(r"(British Embassy Washington|Foreign, Commonwealth.*?Office|Cabinet Office|Ministry of Defence)", re.I)
ADDRESSEE    = re.compile(
    r"(The Rt Hon\.?\s+[\w\s\-]+(?:PC|KCB|KC|MP|CBE|OBE)?|"
    r"(?:Secretary of State|Prime Minister|Foreign Secretary|Minister)\s+(?:for\s+[\w\s]+)?)"
)
SALUTATION   = re.compile(r"\bDear\s+([\w\s\-]+?)[\s,\.]+\n", re.I)
SUBJECT_HDR  = re.compile(r"\n([A-Z][A-Z\s\-:&/]+(?:\d{4})?)\n")
CLASSIFICATION = re.compile(
    r"(OFFICIAL[\s\-]*SENSITIVE(?:\s*[-–]\s*[\w\s]+)?|OFFICIAL|SECRET|TOP SECRET)",
    re.I
)
SIGNATORY    = re.compile(
    r"((?:LORD|OLIVER|SIR|DAME)\s+[A-Z][A-Z\s]+)\s*\n\s*(\d{1,2}\s+\w+ \d{4})",
    re.I
)
CC_LINE      = re.compile(r"(?:Copy to|cc:|c\.c\.):?\s*(.+?)(?:\n\n|\Z)", re.I | re.DOTALL)

# Signals it's really an email thread, not a standalone letter
EMAIL_SIGNALS = re.compile(r"^(From|Sent|Subject):\s+", re.MULTILINE)


# ── Classify letter subtype ───────────────────────────────────────────────────

def is_genuine_letter(text):
    """Heuristic: has letterhead-style sender block, not primarily an email thread."""
    email_headers = len(EMAIL_SIGNALS.findall(text[:500]))
    has_letterhead = bool(FROM_ROLE.search(text[:400]) or
                          re.search(r"From the (Ambassador|Permanent Under-Secretary)", text[:300], re.I))
    # If lots of email headers in the first 500 chars → email thread
    if email_headers >= 2 and not has_letterhead:
        return False
    return has_letterhead


def parse_letter(unit):
    text = unit["text"]
    result = {
        "unit_id":          unit["unit_id"],
        "date":             unit["date"],
        "source_mix":       unit["source_mix"],
        "is_genuine_letter": is_genuine_letter(text),
        "classification":   None,
        "from_role":        None,
        "from_name":        None,
        "from_institution": None,
        "to":               [],
        "cc":               [],
        "date_raw":         None,
        "date_iso":         None,
        "subject":          None,
        "salutation":       None,
        "body_snippet":     None,
        "signatory":        None,
        "notes":            [],
    }

    # OCR garbage — skip deep parse
    alpha_ratio = sum(c.isalpha() for c in text) / max(len(text), 1)
    if alpha_ratio < 0.4 and len(text) < 600:
        result["notes"].append("OCR_GARBAGE: text unreadable")
        return result

    # Classification
    cm = CLASSIFICATION.search(text[:200])
    if cm:
        result["classification"] = cm.group(0).strip()

    # Sender role and name
    rm = FROM_ROLE.search(text[:400])
    if rm:
        result["from_role"] = rm.group(1)
    nm = SENDER_NAME.search(text[:400])
    if nm:
        result["from_name"] = nm.group(1).strip()
    im = INSTITUTION.search(text[:500])
    if im:
        result["from_institution"] = im.group(0).strip()

    # Date
    iso, raw = parse_date_iso(text[:600])
    result["date_iso"] = iso
    result["date_raw"] = raw

    # Addressee lines — look for "The Rt Hon" or ministerial titles
    for m in ADDRESSEE.finditer(text[200:700]):
        cand = m.group(0).strip()
        if cand and cand not in result["to"]:
            result["to"].append(cand)

    # Salutation
    sm = SALUTATION.search(text)
    if sm:
        result["salutation"] = "Dear " + sm.group(1).strip()

    # Subject heading (all-caps line after addressee / before body)
    sal_pos = sm.start() if sm else 0
    if sal_pos > 0:
        after_sal = text[sal_pos:]
        shm = SUBJECT_HDR.search(after_sal[:300])
        if shm:
            candidate = shm.group(1).strip()
            if len(candidate) > 8:
                result["subject"] = candidate

    # Body snippet — text after salutation
    if sm:
        body_start = sm.end()
        result["body_snippet"] = text[body_start:body_start + 500].strip()

    # Signatory
    sgm = SIGNATORY.search(text)
    if sgm:
        result["signatory"] = sgm.group(1).strip()

    # CC list
    ccm = CC_LINE.search(text)
    if ccm:
        cc_raw = ccm.group(1).replace("\n", " ").strip()
        result["cc"] = [c.strip() for c in re.split(r",|;", cc_raw) if c.strip()]

    return result


# ── Run ───────────────────────────────────────────────────────────────────────

results = []
for path in sorted(UNITS_DIR.glob("unit_*.json")):
    unit = json.loads(path.read_text())
    if unit["content_type"] != "letter":
        continue
    parsed = parse_letter(unit)
    results.append(parsed)

    # Write parsed field back into unit file
    unit["parsed"] = parsed
    path.write_text(json.dumps(unit, indent=2, ensure_ascii=False))

# ── Report ────────────────────────────────────────────────────────────────────

genuine = [r for r in results if r["is_genuine_letter"]]
print(f"Letter units: {len(results)} total | {len(genuine)} genuine | {len(results)-len(genuine)} misclassified/garbled")
print()

for r in results:
    flag = "✓ LETTER" if r["is_genuine_letter"] else "~ EMAIL/OTHER"
    print(f"[{r['unit_id']:03d}] {flag}")
    print(f"  classification: {r['classification']}")
    print(f"  from_role:      {r['from_role']}")
    print(f"  from_name:      {r['from_name']}")
    print(f"  from_inst:      {r['from_institution']}")
    print(f"  date:           {r['date_raw']} → {r['date_iso']}")
    print(f"  to:             {r['to'][:2]}")
    print(f"  salutation:     {r['salutation']}")
    print(f"  subject:        {r['subject']}")
    print(f"  signatory:      {r['signatory']}")
    if r['body_snippet']:
        print(f"  body[:100]:     {r['body_snippet'][:100]}")
    if r['notes']:
        print(f"  notes:          {r['notes']}")
    print()

Path("parsed_letters.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
print(f"Saved → parsed_letters.json")
