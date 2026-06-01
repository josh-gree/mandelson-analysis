"""
Entity extraction from parsed email messages and letters using Claude Sonnet
via OpenRouter.

Writes results incrementally to entities.json and entities_by_unit.json
after every completed document — safe to interrupt and resume.
"""
import json, os, time, threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from openai import OpenAI

# ── Config ────────────────────────────────────────────────────────────────────

MODEL   = "anthropic/claude-sonnet-4-5"
API_KEY = os.environ["OPENROUTER_API_KEY"]
WORKERS = 25

client = OpenAI(api_key=API_KEY, base_url="https://openrouter.ai/api/v1")

SYSTEM = """You are an expert analyst extracting structured entities and relationships
from declassified UK government communications about Peter Mandelson's appointment
as HM Ambassador to Washington and his work in that role.

Extract ALL of the following from the text provided:

1. PEOPLE — every named individual mentioned
   Fields: name, role (their job title/position), organisation, context (brief note on why mentioned)

2. ORGANISATIONS — every institution, department, or body mentioned
   Fields: name, type (government dept / embassy / private / political / other), country

3. PLACES — countries, cities, buildings, locations
   Fields: name, type (country/city/building/region)

4. EVENTS — specific meetings, calls, visits, decisions mentioned
   Fields: description, date (if given), participants (list of names)

5. RELATIONSHIPS — directed relationship triples
   Fields: subject (name), predicate (e.g. SENT_TO, MET_WITH, REPORTS_TO, DISCUSSED,
           APPOINTED_BY, LOBBIED, CONCERNS, ATTENDED), object (name or topic), date, context

Return ONLY valid JSON with this exact structure:
{
  "people": [...],
  "organisations": [...],
  "places": [...],
  "events": [...],
  "relationships": [...]
}

Be thorough — err on the side of extracting more rather than less.
Redacted content appears as *** — skip those.
"""

# ── Load documents ────────────────────────────────────────────────────────────

emails  = json.load(open("parsed_email_threads.json"))
letters = json.load(open("parsed_letters.json"))

docs = []

for r in emails:
    for i, m in enumerate(r["messages"]):
        body = (m.get("body") or "").strip()
        if not body or len(body) < 50:
            continue
        label = (
            f"Email thread unit {r['unit_id']}, message {i+1}/{r['message_count']}\n"
            f"Subject: {r['thread_subject'] or 'unknown'}\n"
            f"From: {m['from_name'] or 'unknown'}  →  To: {', '.join(m['to'][:3])}\n"
            f"Date: {m['date_iso'] or 'unknown'}\n"
            f"Classification: {m['classification'] or 'none'}\n\n"
            f"{body}"
        )
        docs.append({
            "unit_id":   r["unit_id"],
            "doc_type":  "email",
            "msg_index": i,
            "from":      m["from_name"],
            "date":      m["date_iso"],
            "subject":   r["thread_subject"],
            "text":      label,
        })

for l in letters:
    body = (l.get("body") or "").strip()
    if not body or len(body) < 50:
        continue
    label = (
        f"Letter unit {l['unit_id']}\n"
        f"From: {l['from_name'] or l['from_role'] or 'unknown'}  "
        f"({l['from_institution'] or ''})\n"
        f"To: {', '.join(l['to'][:3])}\n"
        f"Date: {l['date_iso'] or 'unknown'}\n"
        f"Subject: {l['subject'] or 'none'}\n"
        f"Classification: {l['classification'] or 'none'}\n\n"
        f"{body}"
    )
    docs.append({
        "unit_id":   l["unit_id"],
        "doc_type":  "letter",
        "msg_index": 0,
        "from":      l["from_name"] or l["from_role"],
        "date":      l["date_iso"],
        "subject":   l["subject"],
        "text":      label,
    })

print(f"Documents to process: {len(docs)}")

# ── Resume support ────────────────────────────────────────────────────────────

CACHE         = Path("entities_cache.json")
ENTITIES_FILE = Path("entities.json")
BY_UNIT_FILE  = Path("entities_by_unit.json")

cache = json.loads(CACHE.read_text()) if CACHE.exists() else {}
print(f"Already cached: {len(cache)} / {len(docs)}")


def cache_key(doc):
    return f"{doc['unit_id']}_{doc['msg_index']}"


# ── Shared state (written after every completion) ─────────────────────────────

lock    = threading.Lock()
results = {}   # key → {**doc, entities}
errors  = []
done    = 0


def flush():
    """Write entities.json and entities_by_unit.json from current results."""
    flat = sorted(results.values(), key=lambda r: (r["unit_id"], r["msg_index"]))
    ENTITIES_FILE.write_text(json.dumps(flat, indent=2, ensure_ascii=False))

    by_unit = {}
    for r in flat:
        by_unit.setdefault(r["unit_id"], []).append(r)
    BY_UNIT_FILE.write_text(json.dumps(by_unit, indent=2, ensure_ascii=False))


# Pre-populate results from cache so flush() is always complete
for doc in docs:
    k = cache_key(doc)
    if k in cache:
        results[k] = {**doc, "entities": cache[k]}

flush()  # write what we already have

# ── Extraction ────────────────────────────────────────────────────────────────

def process_doc(args):
    global done
    idx, doc = args
    key = cache_key(doc)

    with lock:
        if key in cache:
            done += 1
            return

    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM},
                    {"role": "user",   "content": doc["text"]},
                ],
                temperature=0,
                max_tokens=2000,
            )
            raw = (resp.choices[0].message.content or "").strip()
            if raw.startswith("```"):
                raw = raw.split("```", 2)[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.rsplit("```", 1)[0].strip()
            entities = json.loads(raw)

            with lock:
                cache[key] = entities
                CACHE.write_text(json.dumps(cache, indent=2, ensure_ascii=False))
                results[key] = {**doc, "entities": entities}
                flush()
                done += 1
                counts = {k2: len(v) for k2, v in entities.items()}
                print(f"[{done}/{len(docs)}] unit_{doc['unit_id']:03d} msg{doc['msg_index']} ✓  {counts}", flush=True)
            return

        except Exception as e:
            wait = 2 ** attempt
            print(f"  [{idx+1}] attempt {attempt+1} failed: {e}  (retry in {wait}s)", flush=True)
            time.sleep(wait)

    with lock:
        errors.append(key)
        done += 1
    print(f"  [{idx+1}] FAILED — skipping", flush=True)


with ThreadPoolExecutor(max_workers=WORKERS) as pool:
    futures = [pool.submit(process_doc, (i, doc)) for i, doc in enumerate(docs)]
    for f in as_completed(futures):
        f.result()

# ── Summary ───────────────────────────────────────────────────────────────────

flat = sorted(results.values(), key=lambda r: (r["unit_id"], r["msg_index"]))
all_people = [p for r in flat for p in r["entities"].get("people", [])]
all_orgs   = [o for r in flat for o in r["entities"].get("organisations", [])]
all_rels   = [x for r in flat for x in r["entities"].get("relationships", [])]

print(f"\n{'='*60}")
print(f"Processed:     {len(flat)} documents  ({len(errors)} errors)")
print(f"People:        {len(all_people)}")
print(f"Organisations: {len(all_orgs)}")
print(f"Relationships: {len(all_rels)}")
print(f"Saved → entities.json, entities_by_unit.json")
if errors:
    print(f"Failed keys:   {errors}")
