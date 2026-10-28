# MATACS-TH-2026-02: AI Proposal Triage Design

- **Name:** Ayesha Amjad
- **Reference:** MATACS-TH-2026-02
- **Time actually spent:** 70 minutes (1 hour 10 minutes)

## Files

- [WRITEUP.md](WRITEUP.md): answers to the five questions, scoring rules and sample-set handling
- [PROMPTS.md](PROMPTS.md): the extraction prompt, exactly as it would be sent
- [ranking.json](ranking.json): expected ranking of proposals A–E
- [diagram/flow.png](diagram/flow.png): process flow from upload to ranked output
- [prototype/score.py](prototype/score.py): optional script that applies the scoring rules to already-extracted facts (`python score.py criteria.json extracted_sample.json`), with [criteria.json](prototype/criteria.json) and [extracted_sample.json](prototype/extracted_sample.json). It does not call any AI model; `prototype/flow.dot` is the diagram source.

## How I used AI tools

I used Claude (Anthropic) to help with this task. I asked it how to approach the brief, and it drafted the process flow, the extraction prompt, the scoring formulas, the write-up and a small scoring script. I then read through all of it, [edited the parts I disagreed with, e.g. WHAT YOU CHANGED], and made sure I could explain every design choice myself.

One place I corrected the AI: its first estimate of proposal E’s score (about 86) was done by rough mental arithmetic. When the scoring rules were put into code and run, E came out at 88.7 (and C’s hidden-instruction score at 83.3, not 82). I used the figures from the code and updated the write-up and ranking file to match.

The AI ranked D third and gave it 0 for timeline. I disagreed because the brief requires completion within 16 weeks and D never states a schedule, so that requirement cannot be confirmed. I changed D to [flagged / ranked lower], with the reason in ranking.json.