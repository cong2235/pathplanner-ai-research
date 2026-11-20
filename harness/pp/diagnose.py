"""Cận dưới (không dùng CP-SAT) để giải thích khi vô nghiệm và để kiểm chéo solver.

Hai cận độc lập:
- chuỗi: số kỳ tối thiểu theo chuỗi học trước/song hành/thứ tự (không giới hạn tín chỉ);
- tín chỉ: số kỳ tối thiểu để chứa đủ tín chỉ còn lại với trần từng kỳ.
"""
from __future__ import annotations

from .config import PlanConfig, Student, effective_cap2
from .curriculum import Curriculum


def lower_bounds(cur: Curriculum, cfg: PlanConfig, st: Student) -> dict:
    done = set(st.done)
    req = [c for c in cur.courses.values() if c.required and c.code not in done]
    codes = {c.code for c in req}

    est = {c: 0 for c in codes}          # chỉ số "bước kỳ dùng được", bắt đầu từ 0
    for _ in range(len(codes) + 2):
        changed = False
        for c in req:
            for p in c.prereq:
                if p in codes and est[c.code] < est[p] + 1:
                    est[c.code] = est[p] + 1; changed = True
            for d in c.coreq:
                if d in codes:
                    m = max(est[c.code], est[d])
                    if est[c.code] != m or est[d] != m:
                        est[c.code] = est[d] = m; changed = True
        for seq in cfg.sequences:
            live = [x for x in seq if x in codes]
            for a, b in zip(live, live[1:]):
                if est[b] < est[a]:
                    est[b] = est[a]; changed = True
        if not changed:
            break
    else:
        raise ValueError("đồ thị tiên quyết có chu trình")
    chain_terms = (max(est.values()) + 1) if est else 0
    for g in cfg.term_group_limits:               # n môn, mỗi kỳ tối đa m môn → cần ≥ ceil(n/m) kỳ
        n = sum(1 for k in g["courses"] if k in codes)
        if n:
            chain_terms = max(chain_terms, -(-n // g["max"]))

    need2 = sum(c.credits2 for c in req)
    for g, members in cur.groups.items():
        done_n = sum(1 for m in members if m in done)
        need = max(0, cfg.elective_need - done_n)
        cheapest = sorted(cur.courses[m].credits2 for m in members if m not in done)[:need]
        need2 += sum(cheapest)
    usable = [t for t in cfg.calendar if t.usable and (cfg.deadline_index is None or t.index <= cfg.deadline_index)]
    acc, credit_terms, unlimited = 0, 0, False
    for t in usable:
        if acc >= need2:
            break
        cap = effective_cap2(t, st)
        if cap is None:                       # không có trần: 1 kỳ chứa được hết
            unlimited = True
            credit_terms += 1
            break
        acc += cap
        credit_terms += 1
    if not unlimited and acc < need2:
        credit_terms = len(usable) + 1       # không đủ chỗ trong lịch

    lb_terms = max(chain_terms, credit_terms)
    lb_index = usable[lb_terms - 1].index if 0 < lb_terms <= len(usable) else None
    return {
        "chain_terms": chain_terms, "credit_terms": credit_terms, "lb_terms": lb_terms,
        "lb_index": lb_index, "lb_end": cfg.calendar[lb_index].end if lb_index is not None else None,
        "remaining_credits": need2 / 2,
    }


def explain_infeasible(cur: Curriculum, cfg: PlanConfig, st: Student) -> list[str]:
    lb = lower_bounds(cur, cfg, st)
    usable = [t for t in cfg.calendar if t.usable and (cfg.deadline_index is None or t.index <= cfg.deadline_index)]
    out: list[str] = []
    if lb["chain_terms"] > len(usable):
        out.append(f"Chuỗi học trước/song hành/thứ tự dài nhất cần ≥ {lb['chain_terms']} kỳ, "
                   f"nhưng lịch chỉ có {len(usable)} kỳ xếp được.")
    if lb["credit_terms"] > len(usable):
        out.append(f"Còn {lb['remaining_credits']:g} tín chỉ; với trần tín chỉ từng kỳ cần ≥ "
                   f"{lb['credit_terms']} kỳ nhưng lịch chỉ có {len(usable)} kỳ xếp được.")
    return out
