# WRITEUP: AI Proposal Triage Design

**Core idea:** AI reads messy text. Plain code makes the decisions and does the maths. A person makes the final award.

Flow: upload → text extraction → injection scan → AI fact extraction → validation → mandatory checks → weighted scoring → ranked list with reasons → human review → award. See `diagram/flow.png`.

## Scoring rules (all in code, loaded per category)

- Mandatory: bidder holds the Ontario licence itself; WSIB and $5M insurance both confirmed. Also over budget ($260,000) or longer than 16 weeks = ineligible.
- Experience (30%): bands by count of 100 kW+ installs: 12+ = 100, 9–11 = 85, 6–8 = 70, 3–5 = 50, 1–2 = 25.
- Price (25%): lowest eligible bid ÷ this bid × 100.
- Timeline (15%): shortest stated weeks ÷ this bid's weeks × 100. Not stated = 0 and a flag.
- Warranty (15%): half panel years (cap 25), half workmanship years (cap 12).
- Team (15%): 25 points each for named lead, crew size, safety plan, monitoring plan.

These formulas are my own assumption, since the brief gives weights but no formulas. An admin could change them.

## 1. AI vs. rules

**AI:** only extracting facts from free-form proposal text into fixed fields, with an evidence quote for each. Proposals are written differently, and AI handles that well.

**Rules/code:** upload, text extraction, loading criteria, injection scan, mandatory pass/fail, all scoring, ranking, logging.

I drew the line where an error would matter. A wrong decision or score must be repeatable and explainable, so code does it. AI never sees the weights and never produces a score.

## 2. Consistency and explainability

- Extraction runs once per proposal at temperature 0 with a strict schema, and the result is stored. Scoring is pure code over the stored facts.
- So ranking twice gives an identical result. Re-running extraction could differ slightly, which is why it is stored and not repeated; changes are caught by a diff and reviewed.
- Each position comes with a score table (points per criterion) and the evidence quote behind each fact. The "reason" is built from those numbers, not free AI text.

## 3. Human in the loop

- **Review 1:** any flagged or ineligible proposal (injection suspected, missing mandatory item, failed quote check) goes to a person before it is dropped or reinstated.
- **Review 2:** the reviewer checks extracted values against the PDF and can correct them. Scores then recalculate.
- **Review 3:** the reviewer sees the ranked list and reasons, can override a rank with a written reason, and makes the final award. The tool never awards.
- **Audit log:** criteria version, prompt version, model name, raw extraction, validation results, scores, ranking, every edit or override (who, when, why), and the final decision.

## 4. Changing criteria

Criteria and weights are versioned. An edit creates a new version and never changes old results. Because facts are stored apart from scoring, re-scoring is cheap and needs no AI call, unless a new criterion needs a fact that was never extracted. Then only that field is extracted again. The reviewer sees old and new rankings side by side and must confirm which one stands. Both stay in the log.

## 5. Risks

Risk     |      Safeguard

## **Wrong extraction**   
Evidence quote for every fact, checked against the source text; reviewer sees PDF next to values
## **Made-up facts**      
`null` for anything not stated; schema validation; quote check rejects invented values 
## **Prompt injection**  
Proposal treated as data only; scan plus model flag; flagged proposals are held for a human, never ranked automatically 
## **Bias**             
Company name not used in scoring; same rules for all bids; reviewer sees reasons
## **Scanned or broken PDFs**  
Low text yield triggers OCR, or a "needs manual entry" flag
## **Vague bids** (e.g. no schedule) 
Scored as missing, never assumed good; flagged for clarification
## **Over-trust in the ranking**
Ranking is advice; override and final award are human; the log keeps both
## **Cost** 
One extraction call per proposal, cached; scoring is free; a smaller model is enough

## How my design handles the sample set

- **B: ineligible.** Cheapest, but the electrical licence belongs to an unnamed subcontractor "to be confirmed", so the mandatory licence test fails.
- **C: flagged.** It contains text trying to command the reviewer. I ignore it and hold the bid for a human. Scored honestly it would get about 83.3 and place 3rd, so the reviewer can reinstate it with a note.
- **D: ranked 3rd** with a flag. No schedule was given, so timeline scores 0 and the reviewer should ask for one.
- **A: 1st (98.0)** and **E: 2nd (88.7)**. A leads on experience and timeline; E has the best warranty and monitoring.
- C's install window (2020 onward) is slightly over five years; I noted this for the reviewer.

## Assumptions

- Installs counted as stated by the bidder, not independently verified.
- Equal timeline treatment: no schedule means 0 points, not disqualification, because the brief only fixes the 16-week limit for bids that state a time.
