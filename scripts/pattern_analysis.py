"""
Extract and count key structural patterns for knowledge graph extraction.
"""
import json, re
from collections import Counter, defaultdict

pages = json.loads(open("full_text.json").read())
all_text = "\n".join(p["text"] for p in pages)

# ── 1. Document section header ─────────────────────────────────────────────
# e.g. "1 - 19-12-2024 - Emails between Vincent Devine (...) and others"
DOC_HEADER = re.compile(
    r"(\d+)\s*[-–]\s*(\d{2}-\d{2}-\d{4})\s*[-–]\s*(.+?)(?=\n\d+\s*[-–]|\Z)",
    re.DOTALL,
)

doc_headers = DOC_HEADER.findall(all_text)
print(f"Document section headers: {len(doc_headers)}")
print("  Samples:")
for num, date, desc in doc_headers[:6]:
    print(f"    [{num}] {date} — {desc[:80].strip()}")

# ── 2. Email From/To/Date/Subject/Cc ──────────────────────────────────────
FROM    = re.compile(r"^From:\s+(.+)$", re.MULTILINE)
TO      = re.compile(r"^To:\s+(.+)$", re.MULTILINE)
CC      = re.compile(r"^Cc:\s+(.+)$", re.MULTILINE)
SUBJECT = re.compile(r"^Subject:\s+(.+)$", re.MULTILINE)
DATE_H  = re.compile(r"^Date:\s+(.+)$", re.MULTILINE)

print(f"\nEmail header occurrences:")
print(f"  From:    {len(FROM.findall(all_text))}")
print(f"  To:      {len(TO.findall(all_text))}")
print(f"  Cc:      {len(CC.findall(all_text))}")
print(f"  Subject: {len(SUBJECT.findall(all_text))}")
print(f"  Date:    {len(DATE_H.findall(all_text))}")

subjects = Counter(s.strip() for s in SUBJECT.findall(all_text))
print(f"\n  Top 15 email subjects:")
for subj, n in subjects.most_common(15):
    print(f"    {n:>3}x  {subj[:80]}")

# ── 3. Person + Role + Department ─────────────────────────────────────────
# e.g. "Vincent Devine (Government Chief Security Officer, CO)"
PERSON_ROLE = re.compile(
    r"([A-Z][a-z]+(?: [A-Z][a-z]+){1,3})\s*\(([^)]{10,80})\)"
)
person_roles = Counter()
for match in PERSON_ROLE.finditer(all_text):
    name, role = match.group(1), match.group(2)
    if any(c.islower() for c in role):
        person_roles[(name, role)] += 1

print(f"\nPerson+Role pairs (person mentioned with role in parens): {len(person_roles)}")
print("  Top 20:")
for (name, role), n in person_roles.most_common(20):
    print(f"    {n:>3}x  {name} — {role}")

# ── 4. Chat message timestamps ─────────────────────────────────────────────
CHAT_TS = re.compile(r"\[(\d{2}/\d{2}/\d{4}),\s*(\d{2}:\d{2})\]\s*([^:]+):")
chat_msgs = CHAT_TS.findall(all_text)
chat_senders = Counter(sender.strip() for _, _, sender in chat_msgs)
print(f"\nChat messages found: {len(chat_msgs)}")
print("  Senders:")
for sender, n in chat_senders.most_common(10):
    print(f"    {n:>3}x  {sender}")

# ── 5. Redaction patterns ──────────────────────────────────────────────────
REDACT = re.compile(r"\bPERSONAL\b|< PERSONAL >|\[REDACTED\]|\[redacted\]|\[withheld\]", re.I)
redactions = REDACT.findall(all_text)
print(f"\nRedaction markers: {len(redactions)}")

# ── 6. Department abbreviations ────────────────────────────────────────────
DEPTS = re.compile(r"\b(CO|FCDO|MoD|HO|No\.10|NCSC|NSV|UKSV|HMT|GCHQ|MI5|MI6|ISC|GSB|SIS)\b")
dept_counts = Counter(DEPTS.findall(all_text))
print("\nDepartment/org abbreviation frequencies:")
for dept, n in dept_counts.most_common():
    print(f"  {dept:<8} {n:>4}")

# ── 7. Date formats ────────────────────────────────────────────────────────
DATE_LONG  = re.compile(r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b", re.I)
DATE_SHORT = re.compile(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b")
DATE_EMAIL = re.compile(r"\b(?:Mon|Tue|Wed|Thu|Fri|Sat|Sun),\s+\d{1,2}\s+\w+\s+\d{4}\b")

print(f"\nDate format occurrences:")
print(f"  Long  (1 Jan 2025):         {len(DATE_LONG.findall(all_text))}")
print(f"  Short (01-01-2025):         {len(DATE_SHORT.findall(all_text))}")
print(f"  Email (Thu, 19 Dec 2024):   {len(DATE_EMAIL.findall(all_text))}")

# Date range
all_dates = DATE_SHORT.findall(all_text)
if all_dates:
    from datetime import datetime
    parsed = []
    for d in all_dates:
        for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
            try: parsed.append(datetime.strptime(d, fmt)); break
            except: pass
    if parsed:
        print(f"  Date range: {min(parsed).date()} → {max(parsed).date()}")
