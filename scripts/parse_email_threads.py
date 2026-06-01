"""
Parse units tagged as content_type=email_thread.

Splits each thread into individual messages and extracts structured headers
(from, sent/date, to, cc, subject, classification, body_snippet).
Produces a sender→recipient edge list for the knowledge graph.
"""
import json, re
from pathlib import Path
from datetime import datetime

UNITS_DIR = Path("units")

# ── Date parsing ──────────────────────────────────────────────────────────────

MONTHS = {
    "january":1,"february":2,"march":3,"april":4,"may":5,"june":6,
    "july":7,"august":8,"september":9,"october":10,"november":11,"december":12,
    "jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,
    "sep":9,"sept":9,"oct":10,"nov":11,"dec":12,
}

_MONTH_PAT = (
    r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
    r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
)

# Outlook short:  Mon 19/12/2024 9:46:09 AM (UTC)
_OL_SHORT = re.compile(
    r"(?:\w{3,9}\s+)?(\d{1,2})/(\d{2})/(\d{4})\s+\d{1,2}:\d{2}"
)
# Long date with optional weekday:  15 September 2025  /  Thu, 19 Dec 2024 at 09:58
_LONG = re.compile(
    rf"(?:\w{{3,9}},?\s+)?(\d{{1,2}})\s+({_MONTH_PAT})\s+(\d{{4}})",
    re.I,
)
# Numeric:  02/04/2025, 14:13  or  11/02/25
_NUMERIC = re.compile(r"(\d{1,2})/(\d{2})/(\d{2,4})")


# American format: "Friday, December 20, 2024"  or  "December 20, 2024"
_AMER = re.compile(
    rf"(?:\w+,\s+)?({_MONTH_PAT})\s+(\d{{1,2}}),?\s+(\d{{4}})",
    re.I,
)


def parse_date_iso(raw: str) -> str | None:
    if not raw:
        return None
    raw = raw.strip()
    # Day-first: "19 Dec 2024" / "Thu, 19 Dec 2024"
    m = _LONG.search(raw)
    if m:
        d, mo_str, y = int(m.group(1)), m.group(2).lower()[:3], int(m.group(3))
        mo = MONTHS.get(mo_str)
        if mo:
            return f"{y}-{mo:02d}-{d:02d}"
    # Month-first (US): "Friday, December 20, 2024"
    m = _AMER.search(raw)
    if m:
        mo_str, d, y = m.group(1).lower()[:3], int(m.group(2)), int(m.group(3))
        mo = MONTHS.get(mo_str)
        if mo:
            return f"{y}-{mo:02d}-{d:02d}"
    # Outlook short: "Mon 19/12/2024 9:46"
    m = _OL_SHORT.search(raw)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        return f"{y}-{mo:02d}-{d:02d}"
    # Numeric: "02/04/2025, 14:13"
    m = _NUMERIC.search(raw)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if y < 100:
            y += 2000
        return f"{y}-{mo:02d}-{d:02d}"
    return None


# ── Message splitting ─────────────────────────────────────────────────────────

# Outlook-style: "From: X\nSent: ..." or "From: X\nDate: ..."
# The regex anchors on two consecutive header lines as a reliable signal.
OUTLOOK_BOUNDARY = re.compile(
    r"(?:^[_\-]{10,}[ \t]*\n)?"         # optional horizontal rule
    r"^(?:OFFICIAL[^\n]*\n)?"            # optional classification line
    r"^From:[ \t]+(?P<from_ol>[^\n]+)\n" # From: Name  (must have inline value)
    r"(?:^(?:To|Cc|Subject|Attachments):[^\n]*\n)*"
    r"^(?:Sent|Date):[ \t]+(?P<sent>[^\n]+)",  # Sent/Date: value (must be inline)
    re.MULTILINE,
)

# Stacked OCR format: headers on their own lines, values on next lines
STACKED_BOUNDARY = re.compile(
    r"^From:[ \t]*\n"
    r"(?:Sent:|Date:)[ \t]*\n"
    r"To:[ \t]*\n",
    re.MULTILINE,
)

# Gmail-style: "On <date>, <name> wrote:" (may wrap across two lines)
GMAIL_BOUNDARY = re.compile(
    r"^On\s+(?P<gm_date>.{5,80}?),\s+(?P<gm_from>[^\n]+?)\s+wrote:\s*$",
    re.MULTILINE,
)

# "---------- Forwarded message" or "-----Original Message-----"
FORWARD_BOUNDARY = re.compile(
    r"^[-]{5,}(?:Forwarded message|Original Message)[-]{0,10}\s*$",
    re.MULTILINE,
)

CLASSIFICATION = re.compile(
    r"^(OFFICIAL[\s\-]*SENSITIVE(?:[\s\-]*[-–][\s\-]*[^\n]+)?|OFFICIAL|SECRET|TOP SECRET)\s*$",
    re.MULTILINE | re.I,
)

# ── Header field extraction ───────────────────────────────────────────────────

# Stacked OCR: all header names first with no inline values, then all values below
_STACKED_HDRS = re.compile(
    r"^From:[ \t]*\n"
    r"(?:Sent:|Date:)[ \t]*\n"
    r"To:[ \t]*\n"
    r"(?:Subject:[ \t]*\n)?"
    r"([^\n]+)\n"   # From value
    r"([^\n]+)\n"   # Sent value
    r"([^\n]+)\n"   # To value
    r"(?:([^\n]+))?",  # Subject value (optional)
    re.MULTILINE,
)


def _field(text: str, name: str) -> str | None:
    # Normal inline format: "Field: value"  (no newline crossing)
    m = re.search(rf"^{name}:[ \t]*([^\n]+)", text, re.MULTILINE | re.I)
    return m.group(1).strip() if m else None


def _stacked_headers(text: str) -> dict:
    """Parse OCR-stacked format: header labels first, values on following lines."""
    m = _STACKED_HDRS.search(text)
    if not m:
        return {}
    return {
        "from":    m.group(1).strip() if m.group(1) else None,
        "sent":    m.group(2).strip() if m.group(2) else None,
        "to":      m.group(3).strip() if m.group(3) else None,
        "subject": m.group(4).strip() if m.group(4) else None,
    }


def _recipients(raw: str | None) -> list[str]:
    if not raw:
        return []
    # Strip email placeholders and split on ; or ,
    raw = re.sub(r"<\s*PERSONAL\s*>|\[PERSONAL\]|Personal", "", raw)
    parts = re.split(r"[;,]", raw)
    return [p.strip() for p in parts if p.strip() and len(p.strip()) > 1]


_PERSONAL_LINE = re.compile(r"^\s*<?\s*PERSONAL\s*>?\s*$", re.I)
_GMAIL_INTRO   = re.compile(r"^On\s+.+wrote:\s*$|^wrote:\s*$", re.I)


def _clean_name(raw: str) -> str:
    name = re.sub(r"<\s*PERSONAL\s*>|\[PERSONAL\]|\bPersonal\b", "", raw, flags=re.I)
    name = re.sub(r"\s{2,}", " ", name).strip().strip("*>").strip()
    return name


def _body_snippet(text: str, max_len: int = 400) -> str:
    lines = text.strip().splitlines()
    out = []
    for ln in lines:
        stripped = ln.strip()
        if (CLASSIFICATION.match(stripped)
                or _PERSONAL_LINE.match(stripped)
                or _GMAIL_INTRO.match(stripped)):
            continue
        out.append(ln)
    return "\n".join(out).strip()[:max_len]


# ── Parse a single message chunk ─────────────────────────────────────────────

def parse_message(chunk: str, depth: int, gm_from: str = None, gm_date: str = None) -> dict:
    msg = {
        "depth":          depth,
        "from_name":      None,
        "date_raw":       None,
        "date_iso":       None,
        "to":             [],
        "cc":             [],
        "subject":        None,
        "classification": None,
        "body_snippet":   None,
    }

    # For Gmail-style: from/date come from the "On X wrote:" line
    if gm_from:
        msg["from_name"] = _clean_name(gm_from)
    if gm_date:
        msg["date_raw"] = gm_date
        msg["date_iso"] = parse_date_iso(gm_date)

    from_raw  = _field(chunk, "From")
    sent_raw  = _field(chunk, "Sent") or _field(chunk, "Date")
    to_raw    = _field(chunk, "To")
    subj_raw  = _field(chunk, "Subject")

    # Fallback: stacked OCR format where field values are on next line
    if not from_raw or not sent_raw:
        stacked = _stacked_headers(chunk)
        from_raw  = from_raw  or stacked.get("from")
        sent_raw  = sent_raw  or stacked.get("sent")
        to_raw    = to_raw    or stacked.get("to")
        subj_raw  = subj_raw  or stacked.get("subject")

    if from_raw and not gm_from:
        msg["from_name"] = _clean_name(from_raw)
    if sent_raw and not gm_date:
        msg["date_raw"] = sent_raw
        msg["date_iso"] = parse_date_iso(sent_raw)

    msg["to"]      = _recipients(to_raw)
    msg["cc"]      = _recipients(_field(chunk, "Cc") or _field(chunk, "CC"))
    msg["subject"] = subj_raw

    # Normalise RE:/FW: prefix from subject
    if msg["subject"]:
        msg["subject"] = re.sub(r"^(?:RE|FW|FWD|Fwd|Re|Fw):\s*", "", msg["subject"],
                                 flags=re.I).strip()

    # Classification: first classification line in the chunk
    cm = CLASSIFICATION.search(chunk)
    if cm:
        msg["classification"] = cm.group(1).strip()

    # Body: text after the last recognised header line
    header_end = 0
    for hdr in ("Subject", "Attachments", "Cc", "CC", "To", "Sent", "Date", "From"):
        m = re.search(rf"^{hdr}:[^\n]*\n", chunk, re.MULTILINE | re.I)
        if m:
            header_end = max(header_end, m.end())
    body = chunk[header_end:] if header_end else chunk
    msg["body_snippet"] = _body_snippet(body)

    return msg


# ── Split thread into messages ────────────────────────────────────────────────

def split_thread(text: str) -> list[dict]:
    """
    Returns list of (depth, chunk, gm_from, gm_date) tuples in chronological
    order (outermost/newest first as they appear in the document).
    """
    # Collect all boundary positions
    boundaries = []  # (start_pos, depth_delta, kind, extra)

    for m in OUTLOOK_BOUNDARY.finditer(text):
        boundaries.append((m.start(), 1, "outlook", {}))

    for m in STACKED_BOUNDARY.finditer(text):
        boundaries.append((m.start(), 1, "stacked", {}))

    for m in GMAIL_BOUNDARY.finditer(text):
        boundaries.append((m.start(), 1, "gmail",
                           {"gm_from": m.group("gm_from"),
                            "gm_date": m.group("gm_date")}))

    for m in FORWARD_BOUNDARY.finditer(text):
        boundaries.append((m.start(), 1, "forward", {}))

    if not boundaries:
        # Single-message thread
        return [parse_message(text, 0)]

    boundaries.sort(key=lambda x: x[0])

    chunks = []
    depth = 0

    # Pre-boundary text: only keep if it has From + a date field (real message, not preamble)
    first_chunk = text[:boundaries[0][0]].strip()
    if (first_chunk
            and re.search(r"^From:[ \t]+\S", first_chunk, re.M)
            and re.search(r"^(?:Sent|Date):[ \t]+\S", first_chunk, re.M)):
        chunks.append(parse_message(first_chunk, depth))

    for i, (start, _, kind, extra) in enumerate(boundaries):
        depth += 1
        end = boundaries[i + 1][0] if i + 1 < len(boundaries) else len(text)
        chunk = text[start:end].strip()
        if kind == "gmail":
            chunks.append(parse_message(chunk, depth,
                                         gm_from=extra.get("gm_from"),
                                         gm_date=extra.get("gm_date")))
        else:
            chunks.append(parse_message(chunk, depth))

    return chunks


# ── Parse a full thread unit ──────────────────────────────────────────────────

def parse_thread(unit: dict) -> dict:
    text = unit["text"]
    messages = split_thread(text)

    # Normalise subject across messages: use most common non-empty value
    subjects = [m["subject"] for m in messages if m["subject"]]
    thread_subject = max(set(subjects), key=subjects.count) if subjects else None

    # Collect unique participants
    people = set()
    for m in messages:
        if m["from_name"]:
            people.add(m["from_name"])
        people.update(m["to"])
        people.update(m["cc"])
    people.discard("")

    # Date range
    dates = sorted(d for m in messages for d in [m["date_iso"]] if d)

    # Sender → recipient edges
    edges = []
    for m in messages:
        if m["from_name"] and m["date_iso"]:
            for tgt in m["to"]:
                edges.append({
                    "from": m["from_name"],
                    "to": tgt,
                    "type": "SENT_EMAIL",
                    "date": m["date_iso"],
                    "subject": thread_subject,
                    "classification": m["classification"],
                })
            for tgt in m["cc"]:
                edges.append({
                    "from": m["from_name"],
                    "to": tgt,
                    "type": "CC_ON_EMAIL",
                    "date": m["date_iso"],
                    "subject": thread_subject,
                    "classification": m["classification"],
                })

    return {
        "unit_id":       unit["unit_id"],
        "date":          unit["date"],
        "source_mix":    unit["source_mix"],
        "thread_subject": thread_subject,
        "message_count": len(messages),
        "date_range":    [dates[0], dates[-1]] if len(dates) >= 2 else dates,
        "participants":  sorted(people),
        "messages":      messages,
        "edges":         edges,
    }


# ── Run ───────────────────────────────────────────────────────────────────────

results = []
for path in sorted(UNITS_DIR.glob("unit_*.json")):
    unit = json.loads(path.read_text())
    if unit["content_type"] != "email_thread":
        continue
    parsed = parse_thread(unit)
    results.append(parsed)

    unit["parsed"] = parsed
    path.write_text(json.dumps(unit, indent=2, ensure_ascii=False))

# ── Report ────────────────────────────────────────────────────────────────────

total_msgs = sum(r["message_count"] for r in results)
total_edges = sum(len(r["edges"]) for r in results)
single = sum(1 for r in results if r["message_count"] == 1)
multi  = len(results) - single

print(f"Email thread units:  {len(results)}")
print(f"Total messages:      {total_msgs}  (avg {total_msgs/len(results):.1f}/thread)")
print(f"Single-message:      {single}  |  Multi-message: {multi}")
print(f"Total edges:         {total_edges}")
print()

# Sample output for a few threads
for r in results[:3]:
    print(f"[{r['unit_id']:03d}] \"{r['thread_subject']}\"  {r['message_count']} msgs  {r['date_range']}")
    for m in r["messages"][:2]:
        print(f"  depth={m['depth']}  from={m['from_name']}  date={m['date_iso']}")
        print(f"         to={m['to'][:2]}  class={m['classification']}")
        if m["body_snippet"]:
            print(f"         body: {m['body_snippet'][:80]}")
    print()

Path("parsed_email_threads.json").write_text(
    json.dumps(results, indent=2, ensure_ascii=False)
)
print(f"Saved → parsed_email_threads.json")
