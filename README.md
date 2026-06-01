# Mandelson Analysis

## Goal

Generate a knowledge graph from data contained in the published PDF release relating to Peter Mandelson.

## Background: Peter Mandelson

Peter Mandelson (born 21 July 1953) is a British Labour politician widely regarded as one of the principal architects of New Labour alongside Tony Blair and Alastair Campbell. He served as MP for Hartlepool from 1992 to 2004 and held several senior Cabinet positions.

### Key Roles

- **Minister without Portfolio** (1997–1998) — Blair's first Cabinet
- **Secretary of State for Trade and Industry** (1998) — first resignation
- **Secretary of State for Northern Ireland** (1999–2001) — second resignation
- **EU Trade Commissioner** (2004–2008)
- **Secretary of State for Business** and First Secretary of State (2008–2010) — returned under Gordon Brown
- **UK Ambassador to the United States** (2024–present) — appointed by Keir Starmer

He was made a life peer in 2008 as **Baron Mandelson of Foy and Hartlepool**.

### Past Controversies and Resignations

**First resignation (1998):** Mandelson failed to declare a £373,000 home loan from fellow minister Geoffrey Robinson while his department was investigating Robinson's business affairs. He resigned as Trade Secretary in December 1998.

**Second resignation (2001):** Allegations that he improperly fast-tracked a UK passport application for Indian businessman Srichand Hinduja. He resigned as Northern Ireland Secretary in January 2001. A subsequent inquiry found the allegations were not fully substantiated, but the political damage was done.

**Lobbying and Global Counsel:** After leaving frontline politics, Mandelson founded Global Counsel, a strategic advisory and lobbying firm. He faced persistent criticism over the firm's clients, which included foreign governments and state-linked entities, raising questions about conflicts of interest.

**Links to China:** Mandelson attracted significant scrutiny over his connections to Chinese businesses and institutions, including relationships with figures linked to the Chinese state. Critics questioned whether these relationships were compatible with his subsequent role as US Ambassador.

### Current Issues (as US Ambassador)

Mandelson's appointment as UK Ambassador to the United States in 2024 proved immediately controversial:

- His past business relationships — particularly with Chinese-linked entities — were raised as a concern given the geopolitical sensitivity of the Washington role during the Trump administration.
- Questions were asked in Parliament about whether he had fully divested from Global Counsel and resolved potential conflicts of interest.
- His confrontational style and history of political controversy made him a polarising choice, with critics arguing he was unsuited to the diplomatic demands of the post.
- He attracted attention for public comments on trade and tariffs that were seen as unhelpful to UK–US negotiations.

## Data Source

The primary data source is the published government PDF: `HA_Volume_II_part_I.pdf`, downloaded from `assets.publishing.service.gov.uk`.

---

## Key Findings from Document Analysis

The corpus covers 190 document units — email threads, letters, meeting notes, and chat messages — spanning December 2024 to September 2025. Entity extraction using Claude Sonnet across all 418 parsed messages surfaces several striking findings.

---

### 1. The security clearance chaos

The very first documents (23–27 December 2024) reveal that officials did not know whether Mandelson needed DV (Developed Vetting) clearance at all. Ian Collard at FCDO wrote to the Cabinet Office asking:

> *"The specific question was whether Lord M is exempt from a UKV process (specifically for DV clearance) as a member of the House of Lords? We think CO say he is exempt. But we want to double check given the policy around public appointments."*
> — Ian Collard, unit_010, 23 Dec 2024

Cabinet Office initially agreed he was exempt. Then they reversed themselves over the Christmas weekend:

> *"Although Gerard McGurk had been in touch with GSG late last week, and GSG had stated that the 'fit and proper person' clearance exemption for Lords and MPs should apply, CO had reflected over the weekend, and judged that the exemptions policy had not envisaged the unusual situation of MPs/Lords being appointed to Ambassadorial positions."*
> — unit_012, 23 Dec 2024

The reason for pushing ahead with full DV was partly American: *"We all recognise that the US are strict about clearance matters, and will likely check Lord Mandelson's clearance with ESND ahead of any sensitive discussions."* A fast-tracked DV was completed by 29 January 2025.

---

### 2. Mandelson's foreign contacts were a real headache for vetting

During the DV process in January 2025, UKSV wrote to Mandelson asking for specificity on which foreign nationals to declare — his Global Counsel network meant the standard questionnaire was unworkable. His reply is notable:

> *"I have a large number of personal acquaintances with foreign nationals but I would not describe these as current friendships or personal business connections. I have no family members who are not listed previously."*
> — Peter Mandelson, unit_028, 21 Jan 2025

UKSV had written to him: *"UKSV appreciates that under the circumstances of your previous roles, you will have met and had contact with many foreign nationals over the years. Therefore for ease, please focus on the people who you have personal friendships with; have personal business connections to; family members that are not included elsewhere on the DV questionnaire."*

---

### 3. Oliver Robbins tried to limit new disclosable evidence during the FAC inquiry

The most striking passage in the entire corpus. In September 2025, as the Foreign Affairs Committee was pressing FCDO about Mandelson's appointment, Permanent Under-Secretary Sir Oliver Robbins wrote to colleagues:

> *"I can understand why people are interested in questions like these, but I think we need to be very careful about sharing such information. If this ends in court, this department will be the defendant.*
>
> *I will speak to Dan about making sure we are keeping the creation of new disclosable evidence within reasonable bounds."*
> — Oliver Robbins to Ailsa Terry, Caroline Hurndall, Dan York-Smith, 13 Sep 2025, unit_029

"Dan" is Dan York-Smith, a senior Cabinet Office official. The email is marked OFFICIAL-SENSITIVE. Robbins appears to be talking about limiting what new written material gets created during an active parliamentary scrutiny process — raising obvious questions about document management during the inquiry.

---

### 4. Varun Chandra: the No.10 fixer at the centre of everything

The second most-connected person after Mandelson himself is **Varun Chandra** — PM Starmer's Special Adviser on Business and Investment, based at No.10. He appears in 28 documents, in direct communication with Mandelson, Robbins, Jonathan Powell (NSA), Morgan McSweeney (chief of staff), and Ailsa Terry (No.10 foreign affairs). Chandra is a former McKinsey partner with deep ties to the same world Mandelson came from. His role as the No.10 interlocutor on all things Mandelson suggests the appointment was driven much more from the PM's private office than from FCDO.

---

### 5. Mandelson's inner network inside government

The entity graph shows Mandelson's top direct communication partners were:

| Person | Role | Contact count |
|--------|------|--------------|
| Ailsa Terry | No.10 foreign affairs | 26 |
| Oliver Robbins | FCDO Permanent Under-Secretary | 23 |
| Jonathan Powell | National Security Adviser | 16 |
| Morgan McSweeney | No.10 Chief of Staff | 14 |
| Michael Ellam | No.10 | 9 |
| Varun Chandra | No.10 Special Adviser | 6 |

This is essentially the PM's inner circle. Mandelson appears to have bypassed normal diplomatic chains and communicated directly at the highest level from his first week in post.

---

### 6. The McSweeney channel: Mandelson reporting direct to No.10's chief of staff

Morgan McSweeney — Keir Starmer's chief of staff and the most powerful political operative in No.10 — appears in 14 direct communications with Mandelson. That frequency places him fourth in Mandelson's contact list, above career diplomats and FCDO ministers. The nature of those communications is as striking as the volume: they read less like ambassador-to-Whitehall reporting and more like a political operative staying in close touch with his principal.

**The Mark Burnett briefing (unit_069, 11 Feb 2025)**

Shortly after arriving in Washington, Mandelson sent McSweeney a personal intelligence note following a private dinner with TV producer Mark Burnett — the man who made *The Apprentice* and has a close personal relationship with Donald Trump:

> *"Dinner with Mark Burnett — Ahead of Mark's visit I thought I would give you some impressions following my dinner with him last night. Mark, [Third Party] and I had a (very) convivial dinner together."*
> — Peter Mandelson to Morgan McSweeney, unit_069, 11 Feb 2025

No FCDO official is copied. This is Mandelson reporting privately to No.10's political chief of staff on a contact in Trump's orbit — bypassing any normal diplomatic record-keeping chain.

**"Please don't forward" — the economic agenda (unit_076, 16 Feb 2025)**

Five days later, Mandelson sent McSweeney a draft document laying out what the UK wanted from the economic side of the upcoming UK–US summit on the 27th. The instruction was explicit:

> *"This is first stab to describe what we want on economic side for 27th. Please don't forward."*
> — Peter Mandelson to Morgan McSweeney, unit_076, 16 Feb 2025

An ambassador sending a policy document to the chief of staff marked "don't forward" is an unusual piece of document management — the kind that keeps a channel tightly controlled between two people rather than feeding into normal inter-departmental circulation.

**The Karen Pierce deletion request (unit_130, 13 Mar 2025)**

The most significant McSweeney exchange in the corpus. Mandelson forwarded a WhatsApp exchange with Karen Pierce (the outgoing US Ambassador) to McSweeney, with an instruction that would later raise eyebrows given the concurrent FAC inquiry:

> *"I have just had this exchange with *** by whatsapp. I don't know why Karen decided to email everyone last night... Please ignore - and if you can do it discreetly, delete!"*
> — Peter Mandelson to Morgan McSweeney, unit_130, 13 Mar 2025

Within hours, Ailsa Terry (No.10 foreign affairs) confirmed the instruction had been relayed up the chain:

> *"Olly has been clear about the need to delete all traffic on this."*
> — Ailsa Terry, unit_130, 13 Mar 2025

"Olly" is Oliver Robbins, FCDO Permanent Under-Secretary — the same official who later wrote about *"keeping the creation of new disclosable evidence within reasonable bounds"* (unit_029, Sep 2025). The deletion instruction and Robbins' later comment sit in the same uncomfortable space: sensitive communications being actively managed out of the documentary record.

**A White House visit, relayed informally (unit_162, 1 Apr 2025)**

In early April, Mandelson dropped McSweeney and Varun Chandra a brief note — no subject, no formal reporting structure — flagging that he had just been at the White House:

> *"I just was in WH seeing the VP about something else."*
> — Peter Mandelson to Morgan McSweeney and Varun Chandra, unit_162, 1 Apr 2025

The informality is notable. A meeting with the Vice President of the United States, disclosed as a casual aside.

**Tariff information control (unit_170, 4 Apr 2025)**

Days later, during the acute phase of UK–US tariff negotiations, Mandelson wrote to McSweeney about the need to control the information narrative flowing out of Whitehall:

> *"The immediate need is to control the information flow out of Whitehall. We must get our version of events out before others do, including those who have always been sceptical about the possibility of a deal."*
> — Peter Mandelson to Morgan McSweeney, unit_170, 4 Apr 2025

**State Visit coordination (unit_154, 30 Mar 2025)**

Mandelson was also coordinating Trump's State Visit directly with McSweeney and Robbins — not through formal diplomatic channels:

> *"Are you content for me firmly to offer the September dates?"*
> — Peter Mandelson to Morgan McSweeney and Oliver Robbins, unit_154, 30 Mar 2025

**The pattern**

Across these communications, Mandelson used McSweeney as a direct back-channel to No.10's political operation: sharing intelligence from private dinners, circulating sensitive documents with instructions not to forward them, requesting deletion of WhatsApp exchanges, and briefing on White House meetings informally. The channel is largely invisible to the normal FCDO reporting structure. Whether this reflects an unusual appointment — a political heavyweight running his own communications network from the Embassy — or a deliberate design by Starmer's operation to keep the Washington channel close to No.10, the documents suggest the two things are the same.

---

### 7. The China thread: a paid Shanghai engagement, messaging management, and the "other side of the fence"

China runs as a quiet undercurrent through the entire corpus — present at Mandelson's appointment, during his vetting, and through to his conduct as Ambassador. The documents reveal three distinct dimensions: a paid private engagement in Shanghai that FCDO had to urgently escalate to No.10; an early exercise in China messaging management; and Mandelson's own framing of the UK's China position in his Ambassador-level communications.

**The UBS Shanghai conference: a paid China engagement days before he started (unit_040, 31 Dec 2024)**

The most significant China-related document is an internal FCDO email chain from 30–31 December 2024 — three days before the New Year, just two weeks before Mandelson was due to start as Ambassador. Officials discovered he had already committed to a paid panel appearance at UBS's **Greater China Conference** in Shanghai, scheduled for 11–13 January 2025:

> *"HMA-Des has committed to participating in a panel event at investment bank UBS's Greater China Conference, hosted in Shanghai from 11-13 January. This is a major event with ~4000 attendees and considerable media. Many sessions are recorded... We understand he would plan to attend virtually and participate in his Global Counsel capacity. We also understand that he would be paid for this engagement."*
> — FCDO internal email, unit_040, 30 Dec 2024

More striking: Mandelson had specifically asked to delay starting on the FCDO payroll until 13 January in order to remain free to fulfil this private, paid China engagement. FCDO officials consulted multiple departments simultaneously — BEW (British Embassy Washington), the China Desk, Americas, HRD, and Security — before escalating to No.10's SpAds:

> *"LPM plans to participate in an international event relating to China. This is renumerated; As he will not by then have taken up employment with HMG, it is a matter for LPM whether or not he proceeds with this event. He has asked that any concerns are flagged to SpAds so that they and No 10 can take a view as to whether they wish to intervene with LPM."*
> — FCDO internal email, unit_040, 31 Dec 2024

The fact that officials consulted Washington, China Desk, Americas, Human Rights & Democracy, and Security in parallel — over New Year — indicates how sensitive they judged the situation. This was a paid engagement via Global Counsel, the lobbying firm Mandelson was supposed to be winding down as a condition of taking the Washington role, at a major Chinese investment bank conference, days before becoming HM Ambassador to the United States.

**"Links with China etc" — known from the start (unit_041, 19 Dec 2024)**

Even in the initial appointment Q&A preparation, the FCDO official drafting the lines flagged China explicitly as a gap that needed addressing:

> *"I know we need more on his background (links with China etc) but I'll pull that together in the morning."*
> — FCDO official, unit_041, 19 Dec 2024

The phrase "links with China etc" — casual, unexplained, evidently a known quantity — suggests Mandelson's China connections were already a recognised political liability requiring managed communications from day one of the appointment.

**Crafting the China message (unit_044, 13 Sep 2024)**

Before his appointment was even formally announced, Mandelson was receiving briefings from FCDO's China Department. In September 2024, the Head of the China Department (Kate Harrisson) sent him "public lines reflecting this government's position on China" ahead of a VIP speaking engagement. Mandelson's response to the draft lines is revealing:

> *"It has to be turned into something I can say! The drift is fine. it mustn't sound naive ie we are vigilant and have eyes wide open but we also want a serious sustained relationship. Yes?"*
> — Peter Mandelson, unit_044, 12 Sep 2024

He was not simply receiving the official lines — he was actively shaping the tone: steering away from what he called "sounding naive," toward a formulation of engaged watchfulness. The phrase "we are vigilant and have eyes wide open but we also want a serious sustained relationship" became the framing he wanted to project.

**China in the Ambassador's own words**

Once in post, Mandelson's own written communications show him navigating the US-China dynamic in two ways. In his February media bullets for Starmer's visit (unit_083), he described the Chagos deal in terms designed to satisfy American concerns about China:

> *"Current issues are Chagos and tariffs. On the former, the US has made certain asks of detail in relation to the deal that sees the US retaining full operational use of Diego Garcia with China kept firmly at bay."*
> — Peter Mandelson, unit_083, 21 Feb 2025

And in his scenesetter to Business Secretary Jonathan Reynolds ahead of Reynolds' March DC visit (unit_131), Mandelson framed the entire US trade agenda in explicit China-exclusion terms:

> *"This is not just about 'equalising' America's trade relationships through addressing tariffs and non-tariff barriers. The America First policy aims to rebuild domestic manufacturing and create a new global trade order with allies working closely together (following US rules) that leaves China increasingly on the 'other side of the fence'."*
> — Peter Mandelson, scenesetter to SoS Reynolds, unit_131, 15 Mar 2025

**The pattern**

The China thread in this corpus runs from a paid Shanghai conference engagement timed to avoid FCDO oversight, through messaging management from day one, to a fully formed Ambassador-level framing in which the UK positions itself explicitly on the US side of an emerging trade bloc confrontation with China. Whether that represents genuine strategic alignment or a deliberate effort to demonstrate China-scepticism given Mandelson's past associations, the documents don't say. What they do show is that China was never far from the surface — and that officials were anxious about it from the first week.

---

### 8. Russia and Ukraine: Mandelson writing the PM's war messaging, a UN crisis, and the April peace talks

Ukraine is the most operationally intensive foreign policy thread in the corpus. Mandelson appears not as a passive diplomatic conduit but as an active shaper of how the UK positions itself on the war — writing Starmer's public lines, being pulled into real-time UN crisis management, and eventually being looped into the London peace talks preparations.

**Mandelson writes Starmer's Russia/Ukraine framing (unit_083, 21 Feb 2025)**

The most striking passage is Mandelson's personal media bullets for Starmer's February 2025 Washington summit — sent directly to McSweeney and Matthew Doyle (No.10 Communications Director). On Russia and Ukraine, the framing is entirely Mandelson's own:

> *"PM believes he can be a bridge between EU and US views re Ukraine because he strongly believes that the only viable outcome of any negotiation has to be a permanent peace not a temporary ceasefire but he also acknowledges that, to get Russia to the table, President Trump's relationship with Putin has to be utilised and that only the US has the heft in Putin's eyes to get talks started."*
> — Peter Mandelson to Morgan McSweeney and Matthew Doyle, unit_083, 21 Feb 2025

This is a significant formulation. Mandelson is framing the UK position as explicitly endorsing Trump's Putin relationship as the necessary lever — a stance well to the right of where most European allies stood in February 2025. The bullets also frame NATO burden-sharing in terms of a "growth deal" centrepiece, subordinating the security discussion to the economic one.

**The UN Ukraine resolution crisis (unit_086, 23 Feb 2025)**

Two days later, Mandelson was directly involved in a real-time diplomatic crisis: the United States had proposed a rival UN Security Council resolution on Ukraine, explicitly "pitting it against Europe." The email chain — copied to ambassadors across multiple capitals, the UN mission, FCDO, and No.10 — shows the UK scrambling to coordinate a position before a Monday morning vote:

> *"UN press are aware and starting to report the US initiative. Reuters filed with the headline: 'US proposes rival UN action on Ukraine, pitting it against Europe'. On current trajectory — if the US go ahead with their resolutions as drafted, and Ukraine too — is likely to be the framing of media reporting out of Monday: whether the 'world' is 'siding' with the Ukrainian or the US vision of peace."*
> — Fergus Eckersley (Political Coordinator, UKMIS New York), unit_086, 21 Feb 2025

Mandelson is on the chain alongside ambassadors from Washington, New York (UKMIS), and EECAD (Eastern Europe and Central Asia Directorate). His reply is redacted, but his inclusion in this urgent coordination — not as a passive observer but as a substantive voice — is notable. UK officials needed instructions and a "cleared EOV [Explanation of Vote] by 0800 NY time on Monday."

**Intelligence from European posts fed directly to Mandelson (units 084 and 125)**

On the same day as the media bullets, UK Ambassador to Italy Ed Llewellyn forwarded Mandelson a private intelligence assessment of Italy's Ukraine position — Meloni's approach to the conflict — marked OFFICIAL-SENSITIVE:

> *"To see... some straws in the wind here on Ukraine over the last 24 hours."*
> — Ed Llewellyn to Peter Mandelson, unit_084, 21 Feb 2025

Three weeks later (unit_125, 11 Mar 2025), Llewellyn again sent Mandelson a personal "sitrep from Rome" on Meloni's Ukraine position. The content of the sitrep itself is heavily redacted, but the pattern — European ambassadors feeding Mandelson informal intelligence on allied leaders' private positions — suggests he was operating as a node for intelligence on the Western coalition's internal Ukraine dynamics, not just as Washington's liaison.

**"Got the Ukraine point" — the State Visit linkage (unit_153, 30 Mar 2025)**

In the State Visit coordination thread, McSweeney sent Mandelson and Robbins a message with a "Ukraine point" attached to the State Visit planning. Mandelson's reply acknowledges it directly:

> *"Got the Ukraine point. On SV, it helps that he agreed dates on Friday for Gulf visits in May."*
> — Peter Mandelson to Morgan McSweeney and Oliver Robbins, unit_153, 30 Mar 2025

The content of McSweeney's Ukraine point is redacted, but the juxtaposition — Ukraine policy linked explicitly to State Visit scheduling in the same email — indicates how tightly the political and diplomatic tracks were being managed together from No.10.

**The London Russia/Ukraine peace talks (unit_190, 22 Apr 2025)**

By late April 2025, Mandelson was being looped directly into the logistics of the London Russia/Ukraine peace talks, scheduled for 23 April at 1 Carlton Gardens. Christian Turner (Political Director, FCDO) forwarded him the internal FCDO brief on the day's structure:

> *"You and copy addressees might welcome a brief update on our plans to host the next round of Russia/Ukraine talks in London on Wednesday (23 April), following on from the meetings in Paris on Thursday. We have moved fast over the Easter weekend to confirm that the meetings will take place at 1 Carlton Gardens from c1000 until 1600 on Wednesday."*
> — FCDO internal email forwarded to Mandelson, unit_190, 22 Apr 2025

**The pattern**

On Russia/Ukraine, Mandelson was not a passive implementer of UK policy — he was writing the messaging, being pulled into real-time UN voting crises, receiving private intelligence from European capitals, and included in peace talks logistics. The framing he authored in February — that Trump's relationship with Putin is the necessary lever — positioned the UK conspicuously close to Washington's line at a moment of acute trans-Atlantic tension over the war's direction.

---

### 9. Jonathan Powell: the NSA channel and the innermost circle

Jonathan Powell — Keir Starmer's National Security Adviser, previously Tony Blair's chief of staff and a central figure in New Labour — appears in 43 documents and is Mandelson's third-most-frequent contact across the corpus. The relationship predates the appointment and runs throughout: from an anticipated press attack line in December 2024 to tight LIMDIS intelligence chains in April 2025. Powell functions not as a formal oversight layer but as a peer — co-drafting announcements, receiving unsolicited intelligence notes, and ensuring Mandelson's requests are actioned by the NSC machinery.

**"Just appointing friends to top jobs?" (unit_041, 19 Dec 2024)**

Even before Mandelson was formally announced, the FCDO Q&A prep anticipated the obvious political attack. The official drafting the lines wrote:

> *"First Jonathan Powell, now Peter Mandelson — just appointing friends to top jobs?"*
> — FCDO draft Q&A, unit_041, 19 Dec 2024

The prepared answer pivoted to skills and experience. But the fact that the line was anticipated — and that the Powell appointment was the frame of reference — signals that both appointments were understood as a deliberate pattern, not coincidental political choices.

**Powell co-drafting economic announcements for the Trump meeting (unit_071, 12 Feb 2025)**

Six weeks into Mandelson's posting, Powell wrote to him directly about the preparation for Starmer's Washington summit:

> *"When I see *** tomorrow we will give him the suggestion for what we could announce on the economic relationship when Keir visits — will send the draft to you this evening for comment."*
> — Jonathan Powell to Peter Mandelson, unit_071, 12 Feb 2025

Mandelson's reply asks about the SMG:

> *"I had no read out of SMG meeting. Any conclusions?"*
> — Peter Mandelson to Jonathan Powell, unit_071, 12 Feb 2025

The SMG — the Small Ministerial Group on the US — is a restricted senior decision-making body that would not normally include the Ambassador as a standard distribution. Mandelson's expectation of a readout, and his direct line to the NSA for it, places him inside the highest-level No.10 decision-making loop on the US relationship.

**The "DO NOT CIRCULATE" lunch intelligence (unit_088, 24 Feb 2025)**

At 3am on 24 February, Mandelson forwarded Powell an intelligence note from a private lunch the previous day — redacted throughout but sent under the subject line "LUNCH WITH [REDACTED] DO NOT CIRCULATE":

> *"Not sure I sent this to you. Scroll down."*
> — Peter Mandelson to Jonathan Powell, unit_088, 24 Feb 2025

The lunch note had been shared earlier with his Washington Embassy team. Forwarding it to the NSA at 3am, on his personal device, marked "do not circulate," is another instance of Mandelson routing sensitive intelligence directly to No.10's security adviser — outside formal reporting channels.

**Powell's unfiltered read on Chagos/BIOT (unit_097, 26 Feb 2025)**

On the Chagos deal, Powell gave Mandelson his candid political risk assessment via a LIMDIS chain following an NSC engagement:

> *"The problem is that if BIOT is not solved before the meeting we will certainly be asked about it by British journalists at the press conference afterwards, and we don't want to be banjaxed there. So if it is not sorted before the meeting it will have to come up there in one form or another."*
> — Jonathan Powell, unit_097, 26 Feb 2025

This is the NSA writing candidly to the Ambassador about domestic political exposure — not a formal brief, but a peer conversation about managing a problem before it blows up in a press conference.

**Powell actioning Mandelson's request via the deputy NSA (units 157 and 160, 31 Mar – 1 Apr 2025)**

At the end of March, Mandelson sent Powell a request (fully redacted). Powell's response — one sentence — confirms execution:

> *"Yes we are making sure that happens. Matt Collins and his team are doing it."*
> — Jonathan Powell to Peter Mandelson, unit_160, 1 Apr 2025

Matt Collins is the Deputy National Security Adviser for Intelligence, Defence and Security. The NSC machinery was being directed, on Mandelson's ask, by the NSA himself.

**"Letter from America" forwarded unsolicited to Powell (unit_183, 12 Apr 2025)**

In April, Mandelson forwarded a "Letter from America" analytical dispatch to Powell directly, with an accompanying note:

> *"I haven't been asked but if I were, the above is what I would say."*
> — Peter Mandelson to Jonathan Powell, unit_183, 12 Apr 2025

The context is a No.10 communications situation — Stephanie Driver (No.10 Director of Communications) had just written to Mandelson about a "misstep by a cabinet member on background" that had leaked a projected timetable for the US trade deal. Mandelson was offering unsolicited strategic advice to the NSA on how to manage the fallout. The phrase "if I were" is notable: it positions him as a parallel policy voice, not a subordinate reporting to London.

**Tight LIMDIS intelligence chains to the end (units 191 and 193, 23–24 Apr 2025)**

In the final weeks of the corpus, Powell, Mandelson, Ailsa Terry, and Ed Llewellyn (Rome) were exchanging LIMDIS-marked intelligence on Meloni's Washington visit and Vance in Rome — a restricted chain about European allied positioning with only four or five recipients. By this point, Mandelson is not an Ambassador being briefed by the NSA; he is a peer participant in the innermost foreign policy decision circle.

**The pattern**

Jonathan Powell appears as the No.10 counterpart who most closely mirrors Mandelson's own profile — a Blair-era political operator now running national security. Their communications are peer-to-peer, informal, and often outside normal channels: 3am intelligence forwards, unsolicited strategic memos, direct asks actioned by the Deputy NSA. Taken alongside the McSweeney channel and the Varun Chandra connection, the Powell relationship confirms that Mandelson's primary operating network was not the FCDO chain of command but a tight inner circle of Starmer's No.10 — one with deep roots in the New Labour world both men came from.

