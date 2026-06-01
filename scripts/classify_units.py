"""
Classify each unit into a content type and add parsing_notes.

Types defined:
  email_thread   — single email or nested reply/forward chain
  letter         — formal official letter with address block + salutation
  meeting_note   — meeting record: attendees, topics, action points
  chat           — timestamped instant-message exchange (Google Chat / WhatsApp)
  certificate    — minimal official document / clearance certificate
  briefing       — structured government briefing note with section headers
  transcript     — long-form speech or interview transcript with speaker turns
"""
import json, re
from pathlib import Path

UNITS_DIR = Path("units")

# ── Detection patterns ────────────────────────────────────────────────────────

CHAT_TS      = re.compile(r"\[\d{2}/\d{2}/\d{4},\s*\d{2}:\d{2}\]")
EMAIL_HEADER = re.compile(r"^(From|Sent|To|Subject):\s+", re.MULTILINE)
SALUTATION   = re.compile(r"\bDear\s+(Prime Minister|Sir|Lord|Minister|Secretary|Ambassador|Mr|Ms|Mrs|Dr)\b", re.I)
SPEAKER_TURN = re.compile(r"^(Tucker Carlson|Interviewer|[A-Z][a-z]+ [A-Z][a-z]+)\s*\n", re.MULTILINE)
ACTION_POINT = re.compile(r"\bAP\s*\d+[:\.]|\baction\s+point\b", re.I)
SECTION_HDR  = re.compile(r"^[@•]\s*(Summary|Background|Lines to use|Context|Recommendation|Key points)", re.MULTILINE | re.I)
BULLET_DENSE = re.compile(r"(^[•\-\*o]\s+.+\n){3,}", re.MULTILINE)
ATTENDEES    = re.compile(r"\battendee[s]?\b|\bpresent[:\s]|\bparticipant[s]?\b", re.I)
CERT_WORD    = re.compile(r"\bcertificate\b|\bclearance\b|\bdv\s+clearance\b", re.I)


PARSING_NOTES = {
    "email_thread": (
        "Extract structured email headers (From, To, Cc, Subject, Date/Sent) for each message "
        "in the chain. Identify reply/forward nesting depth. Parse each message body separately. "
        "Redacted addresses appear as 'PERSONAL' — names are retained. Build sender→recipient "
        "edges per message for communication graph."
    ),
    "letter": (
        "Extract sender institution + signatory, addressee name + title, date, subject heading "
        "(if present), body paragraphs, and closing salutation/sign-off. Classification marking "
        "(OFFICIAL-SENSITIVE etc.) at top. Sender/recipient relationship is a directed WROTE_TO edge."
    ),
    "meeting_note": (
        "Extract meeting date/time, list of attendees (name + role), agenda/discussion topics as "
        "bullet items, any action points (AP 1:, AP 2: patterns). Attendees yield ATTENDED edges "
        "with date. Topics/APs are content nodes linked to the meeting event."
    ),
    "chat": (
        "Parse '[DD/MM/YYYY, HH:MM] Sender: message' tuples. Each tuple is a SENT_MESSAGE edge "
        "with timestamp. Sender names are often abbreviated (JCS = Junior Civil Servant). "
        "Build chronological message sequence within the conversation."
    ),
    "certificate": (
        "Extract issuing organisation, recipient name, date, and core certification statement. "
        "Very short documents — most content is institutional letterhead. "
        "Yields a single ISSUED_TO edge between institution and person with date and cert type."
    ),
    "briefing": (
        "Parse section headers (@ Summary, @ Background, @ Lines to use etc.) as structural anchors. "
        "Extract bullet-point content under each header. Classification markings (OFFICIAL-SENSITIVE) "
        "at top. Heavy redaction ('***') common. Yields a structured document with named sections "
        "and their content lists."
    ),
    "transcript": (
        "Parse speaker-attributed turns: 'Speaker Name\\n[speech text]' or 'Speaker: [text]'. "
        "Transcripts here are typically forwarded via email wrapper — extract the email envelope "
        "first, then the transcript body. Build a sequence of (speaker, text) tuples. "
        "Often includes rough transcription artefacts (repeated words, incomplete sentences)."
    ),
}


def classify(unit):
    text = unit.get("text", "")
    desc = unit.get("description", "").lower()
    chars = len(text.strip())
    src = unit.get("source_mix", "")

    # ── Certificate: very short + certificate language ─────────────────────
    if chars < 400 and CERT_WORD.search(text + desc):
        return "certificate"

    # ── Chat: has timestamped message format ──────────────────────────────
    if CHAT_TS.search(text) or "google chat" in desc or "whatsapp" in desc or "messenger exchange" in desc:
        return "chat"

    # ── Transcript: only the Tucker Carlson interview (forwarded via email) ──
    if "tucker carlson" in text.lower() and chars > 10000:
        return "transcript"

    # ── Briefing: section header markers ──────────────────────────────────
    if SECTION_HDR.search(text):
        return "briefing"

    # ── Meeting note: meeting in description + meeting content signals ─────
    if "meeting" in desc:
        if ATTENDEES.search(text) or ACTION_POINT.search(text) or BULLET_DENSE.search(text):
            return "meeting_note"
        # Even without those, meetings are meeting_notes
        return "meeting_note"

    # ── Letter: formal salutation ─────────────────────────────────────────
    if SALUTATION.search(text) or "letter" in desc:
        return "letter"

    # ── Email thread: has email headers ──────────────────────────────────
    if EMAIL_HEADER.search(text):
        return "email_thread"

    # ── Fallback ──────────────────────────────────────────────────────────
    return "email_thread"


# ── Classify and update all units ─────────────────────────────────────────────

type_counts = {}
for path in sorted(UNITS_DIR.glob("unit_*.json")):
    unit = json.loads(path.read_text())
    ct = classify(unit)
    unit["content_type"] = ct
    unit["parsing_notes"] = PARSING_NOTES[ct]
    path.write_text(json.dumps(unit, indent=2, ensure_ascii=False))
    type_counts[ct] = type_counts.get(ct, 0) + 1

print("Classification complete:")
for t, n in sorted(type_counts.items(), key=lambda x: -x[1]):
    print(f"  {t:<20} {n:>4}")
print(f"  {'TOTAL':<20} {sum(type_counts.values()):>4}")
