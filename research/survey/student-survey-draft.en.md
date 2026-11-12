# VinUni Student Survey – DRAFT v0.1 (English)

English version of [student-survey-draft.md](student-survey-draft.md). Keep both files in sync.

Purpose: collect real pain points in **academic planning** to confirm or reject the gaps in the [gap register](../gaps/gap-register.md). Target length: **6–8 minutes**. Format: Google Forms / Microsoft Forms, **anonymous** (do not collect email, no required sign-in).

**Before sending:** get approval from the supervising lecturer / Student Affairs; pilot with 3–5 students and fix unclear questions; re-time the form.

---

## Section 0 – Introduction & consent (shown at the top)

> We are VinUni students running a research project on helping students **plan their courses semester by semester**. The survey takes about 7 minutes and is **fully anonymous**: we do not ask for your name, student ID, email or specific grades. Results are used for research only and reported in aggregate; individual answers are not published. You may skip any question or stop at any time. This is to understand real difficulties, **not an evaluation of the university or your advisor**.
> ☐ I have read this and agree to take part (required to continue)

---

## Section A – About you (broad groups only)

| # | Question | Type | Options |
|---|---|---|---|
| A1 | Which cohort are you in? | Single choice | 2021 or earlier · 2022 · 2023 · 2024 · 2025 |
| A2 | Your major | Single choice | CS · Data Science · EE · ME · BBA · Other (specify) |
| A3 | Over how many semesters (including summer) have you registered for courses? | Single choice | 1–2 · 3–4 · 5–6 · 7 or more |
| A4 | Current cumulative GPA (approximate) | Single choice | Below 2.5 · 2.5–3.0 · 3.0–3.5 · Above 3.5 · Prefer not to say |

*Anonymity note:* if a cohort × major cell has fewer than 5 respondents, merge groups when reporting.

## Section B – The last time you planned your courses (actual behaviour)

| # | Question | Type | Gap tested |
|---|---|---|---|
| B1 | The last time you chose courses for the next semester, which approaches did you use? (select all) | Multiple choice | G1, G3 |
| | ☐ Read the curriculum framework (PDF) · ☐ Asked my advisor · ☐ Asked friends / senior students · ☐ Tried the registration portal (VinUniDigi) · ☐ Used ChatGPT / other AI · ☐ Made my own sheet (Excel / Notion) · ☐ Did not prepare beforehand · ☐ Other | | |
| B2 | About how long did that planning take (including finding information)? | Single choice | G1, G5 |
| | Under 15 min · 15–60 min · 1–3 hours · More than 3 hours | | |
| B3 | Do you plan **several semesters ahead** (up to graduation)? | Single choice | G1 |
| | Yes, in detail · Yes, roughly · Only the coming semester · No | | |
| B4 | If yes, where do you keep the plan? | Single choice | G1 |
| | Student portal (SIS) · My own file (Excel / Docs / Notion) · Only in my head · I don't keep it | | |
| B5 | Have you ever discovered **after registering or taking a course** that you made a wrong choice (missing prerequisite, too many/few credits, missed a required course, timetable clash, wrong concentration…)? | Single choice + short description | G1, G5, G6 |
| | Never · Once · Two or more times → *"What happened and what did it cost you (time, credits, money, a semester)?"* (free text, optional) | | |

## Section C – Biggest difficulties (tests the hypothesis "are prerequisites the main problem?")

| # | Question | Type | Gap tested |
|---|---|---|---|
| C1 | Which of these makes academic planning **hardest**? Choose up to 3 and rank 1–2–3. *(option order randomised)* | Ranking | G1, G2, G5 |
| | · Knowing the prerequisites · Computing credits per semester (minimum / overload) · Knowing which classes are offered in which semester · Choosing electives / concentration that fit my goals · Understanding regulations (academic warning, failing, retaking, withdrawing) · My cohort's curriculum differs from other cohorts · Not knowing whom to ask · Balancing study load with other commitments · Other | | |
| C2 | Have you ever been unsure **which courses you still need to graduate**? | Scale 1–5 | G1, G5 |
| | 1 = never … 5 = very often | | |
| C3 | Do you often mix up your cohort's curriculum with another cohort's (from friends or old documents)? | Single choice | G5 |
| | Never · Sometimes · Often · Don't know | | |

## Section D – Goals & choices (personalisation)

| # | Question | Type | Gap tested |
|---|---|---|---|
| D1 | After graduation, what do you currently plan to do? | Single choice | G2 |
| | Work · Further study / research · Start a business · Not sure · Other | | |
| D2 | Does that goal affect how you choose electives / concentration / minor? | Scale 1–5 + optional explanation | G2 |
| D3 | Do you find it hard to **connect your career goal to the courses you should take**? | Scale 1–5 | G2 |
| D4 | Have you ever changed your goal / concentration midway? If yes, how hard was it to adjust your study plan? | Single choice + scale 1–5 | G2, G6 |

## Section E – Advisors & support

| # | Question | Type | Gap tested |
|---|---|---|---|
| E1 | About how many times per semester do you meet your academic advisor? | Single choice | G4 |
| | 0 · 1 · 2–3 · More | | |
| E2 | When you meet your advisor about study planning, what do you mainly discuss? | Multiple choice | G4 |
| | Checking prerequisites / credits · Choosing electives · Careers · Academic issues (grades, warnings) · Paperwork / procedures · We don't discuss planning | | |
| E3 | Level of agreement: "I know who to ask, and how, when I have a problem with my study plan." | Scale 1–5 | G4 |
| E4 | What makes you **hesitate to ask your advisor**, or ask enough? (select all) | Multiple choice | G4, G8 |
| | Hard to book an appointment · Advisor is busy · Afraid of being judged · Don't know what to ask · Answers are too general · I don't feel the need | | |

## Section F – AI tools, trust, privacy (tests G3, G8)

| # | Question | Type | Gap tested |
|---|---|---|---|
| F1 | Have you used AI (ChatGPT, Gemini, a university chatbot…) to ask about your curriculum or choose courses? | Single choice | G3 |
| | Never · Tried it · Sometimes · Often | | |
| F2 | If yes: was the answer accurate for **your own curriculum**? Did you double-check it? | Scale 1–5 + Single choice (Always / Sometimes / Never double-check) | G3 |
| F3 | For a tool that suggests a study path, what would make you **trust or distrust** its suggestions? (up to 3) | Multiple choice | G3, G8 |
| | Cites the rule / course description · Explains the reason for each suggestion · Reviewed by my advisor · Based on my own cohort's curriculum · Lets me edit it · I don't need this | | |
| F4 | How comfortable are you with a tool using **your grades** to suggest a path (assuming only you and your advisor can see them)? | Scale 1–5 | G8 |
| F5 | What worries you most about AI course suggestions? (up to 2) | Multiple choice | G8 |
| | Wrong suggestions · Grade data leaks · Being steered too rigidly · Over-reliance, not thinking for myself · No one is accountable when it is wrong · Nothing worries me | | |

## Section G – Closing (optional)

| # | Question | Type |
|---|---|---|
| G1 | If you could have **one thing** that made study planning easier, what would it be? | Short free text |

---

## Question → gap & hypothesis map

| Gap / hypothesis | Questions | Evidence the gap is *real* | Evidence the gap is *weak* |
|---|---|---|---|
| G1 multi-semester planning | B1–B5, C1, C2 | Most plan one semester only, keep plans outside the system, have mixed up plans | Most have a full-degree plan in SIS and rarely err |
| G2 goal-based personalisation | D1–D4, C1 | Goals matter but are hard to link to courses | Course choice barely depends on goals |
| G3 AI Q&A not grounded | B1, F1–F3 | Use AI without verifying, hit errors | Rarely use AI for this |
| G4 advisor burden | E1–E4 | Few meetings, paperwork-focused, hesitant / hard to book | Regular meetings, satisfied |
| G5 complex, cohort-dependent rules | B5, C1, C2, C3 | Cohort mix-ups, regulations hard to follow | Well understood |
| G6 replanning when grades change | B5, D4 | Hard to adjust after failing / changing direction | Rarely happens |
| G8 privacy & bias | F3–F5 | Worried about data and being steered | Comfortable, little worry |
| **Central hypothesis:** the main difficulty is credit load / regulations / choosing electives rather than prerequisites | C1 | "Knowing the prerequisites" ranks below other items | It ranks first → prioritise the prerequisite solver |

## Light analysis plan

- Target 30–60 responses covering ≥3 majors and ≥3 cohorts. Report **frequencies and quotes**, no inferential statistics; state that the sample is a convenience sample, not representative.
- C1: rank score (rank 1 = 3, 2 = 2, 3 = 1) plus selection rate.
- Free text: group into themes (a theme needs ≥2 mentions); store **short quotes** (≤2 sentences, identifying details removed) with role / cohort in the registry as type-C evidence (see [source-verification](../../.claude/skills/source-verification/SKILL.md)).
- Update `gap-register.md`: adjust *Freq* and *Sev* from the data; downgrade unsupported gaps.

## Decisions needed before sending

1. Approval / notification from the university (research ethics, distribution channel).
2. Form tool (Google Forms or Microsoft Forms – prefer a university account if possible).
3. Keep the Vietnamese and English versions in sync (this file mirrors `student-survey-draft.md`).
4. Write a separate **advisor interview guide** (5–8 advisors: workload, tools, hard cases, how study plans are reviewed).
5. Pilot with 3–5 people, fix, then release.
