"""
Parse the Table of Contents entries — the richest structured data in the document.
Each entry encodes: document number, date, type, participants with roles and departments.
"""
import json, re
from collections import Counter

pages = json.loads(open("full_text.json").read())
all_text = "\n".join(p["text"] for p in pages)

# TOC entries appear as:
# "N - DD-MM-YYYY - [Doc type] between/from [Person (Role, Dept)] and/to [Person (Role, Dept)]"
TOC_ENTRY = re.compile(
    r"(\d+)\s*[-–]\s*(\d{2}-\d{2}-\d{4})\s*[-–]\s*"
    r"(Email[s]?|Letter|Meeting[s]?|Google Chat|WhatsApp|Note[s]?|Briefing|Transcript[s]?)"
    r"(.+?)(?=\n\d+\s*[-–]\s*\d{2}-\d{2}-\d{4}|\Z)",
    re.IGNORECASE | re.DOTALL,
)

PERSON_ROLE_DEPT = re.compile(
    r"([A-Z][a-zA-Z\-\. ]+?)\s*\(([^)]+,\s*(?:CO|FCDO|MoD|HO|No\.10|NCSC|HMT|UKSV|NSV|GSB|SIS|NCA|HMRC|DWP|DHSC|DESNZ|DBT|DSIT|MOJ|CPS|AGO|OAG|FCO|DfT|DfE)[^)]*)\)",
)

entries = []
for m in TOC_ENTRY.finditer(all_text):
    num, date, doc_type, rest = m.groups()
    rest = rest.strip().replace("\n", " ")
    people = [(p.strip(), r.strip()) for p, r in PERSON_ROLE_DEPT.findall(rest)]
    entries.append({
        "doc_num": int(num),
        "date": date,
        "type": doc_type.strip(),
        "description": rest[:120],
        "people": people,
    })

print(f"TOC entries parsed: {len(entries)}")

# Date range of documents
from datetime import datetime
dates = []
for e in entries:
    try: dates.append(datetime.strptime(e["date"], "%d-%m-%Y"))
    except: pass
if dates:
    print(f"Document date range: {min(dates).date()} → {max(dates).date()}")

# Type breakdown
type_counts = Counter(e["type"].lower() for e in entries)
print("\nDocument types in TOC:")
for t, n in type_counts.most_common():
    print(f"  {t:<20} {n:>4}")

# Most mentioned people (with roles) across TOC
all_people = Counter()
for e in entries:
    for name, role in e["people"]:
        all_people[name] += 1

print(f"\nPeople named in TOC entries (with roles): {len(all_people)}")
print("Top 25:")
for name, n in all_people.most_common(25):
    print(f"  {n:>3}x  {name}")

# Show sample entries with full person/role parsing
print("\nSample parsed TOC entries:")
for e in entries[:8]:
    print(f"  [{e['doc_num']}] {e['date']} | {e['type']}")
    print(f"       {e['description'][:100]}")
    for name, role in e["people"]:
        print(f"       → {name}: {role}")
    print()

# Save parsed entries
import json as js
out = "toc_entries.json"
js.dump(entries, open(out, "w"), indent=2)
print(f"Saved to {out}")
