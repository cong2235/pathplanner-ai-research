---
name: source-verification
description: Rules for citing, logging and verifying sources during research so no claim is fabricated. Use whenever writing a research note, comparing products, or stating a statistic/feature claim.
---

# Source Verification (anti-hallucination)

- Every factual claim (feature, price, stat, date, paper result) gets a source ID `S###` in `research/sources/registry.md`:
  `| S### | title | URL | publisher/venue | type | accessed YYYY-MM-DD | reliability A/B/C | note |`
- Reliability: **A** primary (official docs, peer-reviewed paper, dataset page); **B** reputable secondary (major news, vendor case study); **C** forum/review/blog (only as pain-point *evidence*, never for feature claims).
- Cite only URLs actually opened or seen in search results. If unfetchable, mark `unverified`.
- Distinguish documented vs marketing vs inferred; label inferences "(inference)".
- Copy numbers exactly with unit/year/sample size.
- Conflicting sources: record both, say which is trusted and why.
- No evidence found: write "Không tìm thấy bằng chứng"; never fill gaps from memory.
- Re-check claims older than 18 months on fast-moving topics (LLM products).
