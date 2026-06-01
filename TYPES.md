# Document Unit Types

Each unit in `units/` has a `content_type` field. This document defines each type,
its prevalence, its structural signature, and what parsing it entails.

---

## Type Summary

| Type | Count | % |
|------|-------|---|
| `email_thread` | 160 | 84.2% |
| `letter` | 13 | 6.8% |
| `meeting_note` | 12 | 6.3% |
| `chat` | 2 | 1.1% |
| `certificate` | 1 | 0.5% |
| `briefing` | 1 | 0.5% |
| `transcript` | 1 | 0.5% |
| **Total** | **190** | |

---

## `email_thread`

**Count:** 160

**Structural signature:**
```
From: [Name] <PERSONAL>
Sent: [Day DD/MM/YYYY HH:MM:SS]
To: [Name] <PERSONAL>; [Name] <PERSONAL>
Cc: [Name] <PERSONAL>
Subject: [subject line]

[body text]

-----Original Message-----
From: ...       ← nested prior message
```

Emails in this corpus use two date formats interchangeably:
- Outlook format: `Sent: Mon 19/12/2024 9:46:09 AM (UTC)`
- Gmail format: `Date: Thu, 19 Dec 2024 at 09:58`

All email addresses are redacted to `PERSONAL`. Sender/recipient names are retained.
Classification markings (`OFFICIAL-SENSITIVE`, `OFFICIAL`) appear as first line of body.

**What to parse:**
- Each message in the chain: `From`, `Sent`/`Date`, `To`, `Cc`, `Subject`, body text
- Reply nesting depth (number of quoted layers)
- Classification marking per message
- Sender → recipient directed edges per message
- Subject thread grouping (normalise RE:/Fwd: prefixes)

**Edge types for knowledge graph:**
- `(Person) –[SENT_EMAIL]→ (Person)` with date, subject, classification
- `(Person) –[CC_ON_EMAIL]→ (Person)` with date
- `(Email) –[IN_THREAD]→ (EmailThread)` keyed by normalised subject

---

## `letter`

**Count:** 13

**Structural signature:**
```
[CLASSIFICATION MARKING]
[Sender institution / letterhead]

[Date]

[Addressee name]
[Addressee title/address]

[Subject heading in caps (optional)]

Dear [Title Last Name / Prime Minister / Secretary of State],

[Body paragraphs — formal prose]

Yours sincerely / Yours ever,
[Signatory name]
[Signatory title]
```

Letters include formal diplomatic correspondence (ambassador letters to PM),
ministerial letters, and official notifications. Some are sent as attachments
forwarded through email chains.

**What to parse:**
- Sender: name, title, institution
- Addressee: name, title
- Date
- Subject heading (if present)
- Body paragraphs (often contain key policy statements or requests)
- Signatory block

**Edge types for knowledge graph:**
- `(Person) –[WROTE_LETTER_TO]→ (Person)` with date and subject
- `(Letter) –[CONCERNS]→ (Topic/Event)` from subject line

---

## `meeting_note`

**Count:** 12

**Structural signature:**
Varies considerably — no single rigid format. Common patterns:
```
[Attendees listed at top, sometimes as bullet points]

[Topic / agenda item heading]
[Discussion notes — often bullet-pointed]
- [Point made by Person X]
- [Point made by Person Y]

AP 1: [Action point text] — [Owner]
AP 2: [Action point text] — [Owner]
```

Some meetings have very sparse notes (just attendee list + one-line summary).
Others have full bullet-point readouts with named speakers.

**What to parse:**
- Attendees: name + role (often listed explicitly)
- Date and location (from unit metadata and text)
- Topics / agenda items as structured sections
- Statements attributed to named individuals
- Action points: owner + description

**Edge types for knowledge graph:**
- `(Person) –[ATTENDED_MEETING]→ (Meeting)` with date
- `(Meeting) –[DISCUSSED_TOPIC]→ (Topic)`
- `(Person) –[ACTION_POINT]→ (Task)` from AP records

---

## `chat`

**Count:** 2

**Structural signature:**
```
[DD/MM/YYYY, HH:MM] Sender Name: message text
[DD/MM/YYYY, HH:MM] Sender Name: message text
```

Google Chat and WhatsApp exchanges. Senders are sometimes identified by initials
or role abbreviation (`JCS` = Junior Civil Servant) rather than full name.
Informal, conversational; tend to be candid.

**What to parse:**
- Each message as a tuple: (timestamp, sender, message_text)
- Sender identity resolution (JCS → role, not a name)
- Conversation sequence and reply structure

**Edge types for knowledge graph:**
- `(Person) –[SENT_CHAT]→ (Person)` with timestamp and platform
- `(ChatMessage) –[PART_OF]→ (ChatConversation)`

---

## `certificate`

**Count:** 1 (unit_091 — Peter Mandelson's DV Clearance Certificate)

**Structural signature:**
```
[Issuing organisation letterhead]
[Date]
[Recipient name]
[Certification statement in caps]
```

Very short document (< 400 chars of extractable text). The certificate itself
is an image within the PDF; the OCR captured minimal text — mainly letterhead,
date, and the certificate title.

**What to parse:**
- Issuing body: Foreign, Commonwealth & Development Office
- Recipient: Peter Mandelson
- Date: 29 January 2025
- Certificate type: DV (Developed Vetting) Clearance

**Edge types for knowledge graph:**
- `(Organisation) –[ISSUED_CERTIFICATE]→ (Person)` with date and cert_type

---

## `briefing`

**Count:** 1 (unit_106 — structured briefing note attachment)

**Structural signature:**
```
OFFICIAL SENSITIVE
@ Summary: [text or *** redacted]
@ Lines to use:
  o [bullet]
  o [bullet]
@ Background:
  o [bullet]
```

Section headers prefixed with `@`. Bullet points prefixed with `o`. Heavy
redaction — most content replaced with `***`. This is a government briefing
note format (scene-setter or lines-to-take document).

**What to parse:**
- Section headers as structural anchors
- Bullet content under each section (where not redacted)
- Classification marking
- Note: heavy redaction limits extractable content

**Edge types for knowledge graph:**
- `(Briefing) –[HAS_SECTION]→ (Section)` with section_name
- `(Section) –[CONTAINS_POINT]→ (BulletPoint)` with text

---

## `transcript`

**Count:** 1 (unit_172 — Tucker Carlson interview with Scott Bessent, forwarded to Mandelson)

**Structural signature:**
```
[Email wrapper: From/To/Subject forwarding the transcript]

Tucker Carlson
[speech text — continuous natural language]

[Speaker name]
[speech text]
```

A rough transcript of a US political interview forwarded through the UK
government email chain. Speaker turns are separated by speaker name on its
own line. Contains transcription artefacts (repeated words, incomplete sentences).
56,000+ characters — by far the longest unit.

**What to parse:**
- Email envelope: who forwarded it, to whom, when
- Transcript body: alternating (speaker, speech_text) pairs
- Speaker identity: Tucker Carlson (interviewer), Scott Bessent (US Treasury Secretary)
- Key topics mentioned: tariffs, supply chains, China, economic security

**Edge types for knowledge graph:**
- `(Person) –[FORWARDED_TRANSCRIPT]→ (Person)` via email envelope
- `(Transcript) –[SPEAKER_TURN]→ (SpeechSegment)` with speaker and text
- `(Transcript) –[DISCUSSES_TOPIC]→ (Topic)` from content analysis
