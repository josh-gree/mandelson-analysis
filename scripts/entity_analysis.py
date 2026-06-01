"""
Named entity frequency analysis — people, organisations, key topics.
"""
import json, re
from collections import Counter

pages = json.loads(open("full_text.json").read())
all_text = "\n".join(p["text"] for p in pages)

# ── Known named persons (from TOC and sample reading) ──────────────────────
KNOWN_PEOPLE = [
    "Peter Mandelson", "Lord Mandelson",
    "Vincent Devine", "Michael Roberts", "Gerard McGurk",
    "Vita Maynard", "Tom Bramley", "Ian Collard",
    "Ailsa Terry", "Oliver Robbins", "Sir Oliver Robbins",
    "Caroline Hurndall", "Darren Jones", "Jon Garvie",
    "Pat McFadden", "Lindsey Whyte", "James Roscoe",
    "Nick Thomas-Symonds", "Patrick Vallance", "Lord Vallance",
    "Simon Hoare", "Keir Starmer",
    "Tucker Carlson", "Scott Bessent",
    "Michael Ellam",
]

print("Named person mention counts:")
for name in sorted(KNOWN_PEOPLE, key=lambda n: -all_text.count(n)):
    n = all_text.count(name)
    if n > 0:
        print(f"  {n:>4}x  {name}")

# ── Organisations ──────────────────────────────────────────────────────────
KNOWN_ORGS = [
    "Global Counsel", "Palantir", "Anduril",
    "Cabinet Office", "Foreign Office", "FCDO",
    "No. 10", "No.10", "Prime Minister",
    "House of Lords", "House of Commons", "Parliament",
    "Metropolitan Police", "ISC", "NCSC", "GCHQ",
    "Oxford University", "Treasury", "HMT",
    "White House", "Oval Office",
    "Washington", "British Embassy",
    "Government Security", "UKSV",
]

print("\nOrganisation mention counts:")
for org in sorted(KNOWN_ORGS, key=lambda o: -all_text.count(o)):
    n = all_text.count(org)
    if n > 0:
        print(f"  {n:>4}x  {org}")

# ── Key topics / themes ────────────────────────────────────────────────────
TOPICS = {
    "vetting / NSV":        re.compile(r"\bvetting\b|\bNSV\b|\bnational security vetting\b", re.I),
    "appointment":          re.compile(r"\bappointment\b|\bappointed\b", re.I),
    "withdrawal":           re.compile(r"\bwithdrawal\b|\bwithdrawn\b|\bwithdrew\b", re.I),
    "tariffs / trade":      re.compile(r"\btariff(s)?\b|\btrade\b", re.I),
    "China / Chinese":      re.compile(r"\bChina\b|\bChinese\b", re.I),
    "redaction":            re.compile(r"\bredact(ed|ion)?\b", re.I),
    "Humble Address":       re.compile(r"\bhumble address\b", re.I),
    "Oxford chancellorship":re.compile(r"\boxford\b.*\bchancellor\b|\bchancellor\b.*\boxford\b", re.I),
    "STRAP / classified":   re.compile(r"\bSTRAP\b|\bclassif(ied|ication)\b", re.I),
    "police investigation":  re.compile(r"\bpolice\b.*\binvestigation\b|\binvestigation\b.*\bpolice\b", re.I),
}

print("\nTheme/topic occurrence counts:")
for topic, pat in TOPICS.items():
    n = len(pat.findall(all_text))
    print(f"  {n:>4}x  {topic}")

# ── Communication network: who emails whom ─────────────────────────────────
# Extract From/Subject pairs to find communication clusters
EMAIL_BLOCK = re.compile(
    r"From:\s+([^\n<]+?)(?:\s*<[^>]*>)?\s*\nDate:[^\n]+\nSubject:\s+([^\n]+)",
    re.MULTILINE
)
from_subject = [(m.group(1).strip(), m.group(2).strip()) for m in EMAIL_BLOCK.finditer(all_text)]
from_counts = Counter(f for f, _ in from_subject)
print(f"\nTop email senders (by From: header):")
for sender, n in from_counts.most_common(15):
    print(f"  {n:>3}x  {sender}")
