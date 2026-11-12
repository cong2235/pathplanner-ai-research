---
name: gap-analysis
description: Identify unsolved real-world problems and gaps that existing advising/learning-path products leave open, and rank them as opportunities for PathPlanner AI. Use after competitor scan, or when asked about pain points, unmet needs, or differentiation.
---

# Gap Analysis

## Inputs
`research/competitors/*.md`, `research/sources/registry.md`, plus pain-point evidence (surveys, news, papers, forums, user reviews on G2/Capterra/Reddit/Vietnamese student communities).

## Method
1. **Pain-point mining**: collect >=30 evidence snippets (URL, date, role, short verbatim quote).
2. **Cluster** into themes, e.g.: static rule-based planning, no career-goal alignment, no explanation, hallucinated prerequisites in LLM tools, advisor workload, privacy/FERPA, bias/steering, replanning when grades change, fragmented multi-version curricula, cost/latency, no evaluation, Vietnamese credit-system localisation.
3. **Score each theme 1-5**: Severity, Frequency, Competitor-gap (5 = unsolved), Feasibility in project scope, Measurability (provable with metrics/datasets).
4. **Opportunity score** = Severity x Frequency x Competitor-gap x Feasibility; justify each score in one line.
5. **Map to the brief**: which required/advanced deliverable of EDU-06 addresses the gap and which metric proves it.
6. **Anti-claims**: list gaps we should NOT claim (already solved, unverifiable, out of scope).

## Output
`research/gaps/gap-register.md` (table) and a top-5 shortlist with a one-paragraph hypothesis each. Every row cites evidence IDs from the registry; no uncited gaps.
