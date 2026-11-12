---
name: competitor-scan
description: Research existing products similar to PathPlanner AI (AI academic advising, degree planning, personalized learning path, course recommendation, learning analytics). Use when asked to find, profile, or compare competitors/related work, commercial or academic.
---

# Competitor & Related-Work Scan

Goal: build an evidence-based map of products/papers overlapping with PathPlanner AI (EDU-06): goal+ability-aware semester path planning, prerequisite/credit constraints, explanations with citations, advisor HITL, dynamic replanning, FERPA-style privacy.

## SCOPE OVERRIDE (user, 2026-11-12): chỉ VinUni rồi các trường Việt Nam; bỏ qua sản phẩm/trường quốc tế. Các lane dưới đây chỉ áp dụng cho phần Việt Nam (lane 1–3 dùng ví dụ VN: hệ thống QLĐT, chatbot trường, pilot VinUni/CMC/HUFLIT…); lane 4 chỉ paper có dữ liệu/tác giả VN.

## Search lanes (original template – lọc theo scope trên)
1. **Commercial degree-planning / advising**: Stellic, Degree Works (Ellucian), uAchieve, Civitas, EAB Navigate, Salesforce Education Cloud, Coursera/Handshake career paths, Kuali.
2. **AI tutors / path recommenders**: Khanmigo, Coursera Coach, Knewton/Alta, ALEKS, Squirrel AI, adaptive-learning platforms.
3. **University-built pilots**: Georgia State (Pounce, GPS Advising), ASU, UCF, and Vietnamese universities (VinUni, HUST, FPT...).
4. **Academic work (last 5 yrs)**: course recommendation, knowledge tracing (DKT/SAKT/AKT), LLM + constraint-solving planning, curriculum-graph RAG, explainable recommenders, fairness in educational recommenders. Prefer L@S/LAK/EDM/AIED/RecSys/arXiv.
5. **Open datasets/standards**: EdNet, ASSISTments, OULAD, ESCO, O*NET, LTI 1.3 (record licence + what each can and cannot validate).

## Procedure
- Use WebSearch (standard first; extended for niche/recent). Run independent searches in parallel.
- For each candidate open the primary source (official site/docs/paper), not a blog summary.
- Fill `research/_templates/competitor-profile.md` and save to `research/competitors/<slug>.md`.
- Log every claim with URL + access date in `research/sources/registry.md` (see source-verification).
- Capability matrix marks: ✅ documented / 🟡 partial or marketing-only / ❌ none found / ❓ unknown. Never mark ✅ from marketing alone without noting it.
- Stop when 3 consecutive searches yield no new product; target >=15 products and >=10 papers.

## Output
`research/competitors/_matrix.md`: rows = products, cols = the 12 capability dimensions in CLAUDE.md.
