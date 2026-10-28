"""Deterministic scoring over already-extracted facts. No AI, no randomness.

Usage: python score.py criteria.json extracted_sample.json
"""
import json
import sys


def experience_score(n):
    if n is None:
        return 0
    for floor, pts in ((12, 100), (9, 85), (6, 70), (3, 50), (1, 25)):
        if n >= floor:
            return pts
    return 0


def warranty_score(panel, work):
    p = min((panel or 0) / 25, 1)
    w = min((work or 0) / 12, 1)
    return 100 * (0.5 * p + 0.5 * w)


def team_score(x):
    keys = ("named_lead", "crew_size_stated", "safety_plan", "monitoring_plan")
    return 25 * sum(bool(x.get(k)) for k in keys)


def main(criteria_path, facts_path):
    crit = json.load(open(criteria_path))
    facts = json.load(open(facts_path))
    wts = crit["weights"]
    assert sum(wts.values()) == 100, "weights must total 100"

    results, passing = [], []
    for f in facts:
        p = f["proposal"]
        mandatory_ok = (f["licence_held_by_bidder"]
                        and f["wsib_confirmed"] and f["insurance_5m_confirmed"])
        over_budget = f["price_cad"] is None or f["price_cad"] > crit["budget_ceiling_cad"]
        late = f["weeks"] is not None and f["weeks"] > crit["max_weeks"]
        if not mandatory_ok or over_budget or late:
            results.append({"proposal": p, "status": "ineligible", "score": None})
        else:
            passing.append(f)

    best_price = min(f["price_cad"] for f in passing)
    stated_weeks = [f["weeks"] for f in passing if f["weeks"]]
    best_weeks = min(stated_weeks)

    scored = []
    for f in passing:
        parts = {
            "experience": experience_score(f["installs_100kw_plus_last5y"]),
            "price": 100 * best_price / f["price_cad"],
            "timeline": 100 * best_weeks / f["weeks"] if f["weeks"] else 0,
            "warranty": warranty_score(f["panel_warranty_years"], f["workmanship_warranty_years"]),
            "team": team_score(f),
        }
        total = sum(parts[k] * wts[k] / 100 for k in parts)
        scored.append((f, parts, round(total, 1)))

    ranked = sorted((s for s in scored if not s[0]["injection_suspected"]),
                    key=lambda s: -s[2])
    for i, (f, parts, total) in enumerate(ranked, 1):
        results.append({"proposal": f["proposal"], "status": "ranked", "rank": i,
                        "score": total, "parts": {k: round(v, 1) for k, v in parts.items()}})
    for f, parts, total in scored:
        if f["injection_suspected"]:
            results.append({"proposal": f["proposal"], "status": "flagged", "score": None,
                            "shadow_score_if_reinstated": total,
                            "parts": {k: round(v, 1) for k, v in parts.items()}})

    results.sort(key=lambda r: (r.get("rank") is None, r.get("rank") or 0, r["proposal"]))
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
