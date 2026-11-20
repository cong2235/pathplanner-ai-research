"""Solver lập lộ trình bằng OR-Tools CP-SAT (DUT – CNTT Việt-Nhật).

Thứ tự ưu tiên (từ điển, giải tuần tự từng pha, mỗi pha khóa kết quả pha trước):
  1. thời gian ra trường sớm nhất (mốc kết thúc kỳ cuối nhỏ nhất)
  2. tối đa độ phù hợp mục tiêu của SV (trọng số môn tự chọn)
  3. tối thiểu số tín chỉ học hè
  4. tối thiểu tải kỳ cao nhất (cân bằng tải)
Vô nghiệm không retry: trả lý do từ cận dưới độc lập (diagnose).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from ortools.sat.python import cp_model

from .config import PlanConfig, Student, effective_cap2
from .curriculum import Curriculum
from .diagnose import explain_infeasible, lower_bounds


@dataclass
class Plan:
    status: str                                  # OPTIMAL | FEASIBLE | INFEASIBLE | TIMEOUT
    terms: dict[int, list[str]] = field(default_factory=dict)   # chỉ số kỳ trong lịch -> mã môn
    electives: dict[str, list[str]] = field(default_factory=dict)
    last_index: int | None = None
    end_time: int | None = None
    preference_score: float = 0.0
    phases: list[dict] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    wall_s: float = 0.0

    def term_credits(self, cur: Curriculum, t: int) -> float:
        return sum(cur.courses[c].credits2 for c in self.terms.get(t, [])) / 2


def _build(cur: Curriculum, cfg: PlanConfig, st: Student, lock: dict):
    done = set(st.done)
    unknown = done - set(cur.courses)
    if unknown:
        raise ValueError(f"mã đã học không có trong khung: {sorted(unknown)}")

    m = cp_model.CpModel()
    cal = cfg.calendar
    undone = [c for c in cur.courses.values() if c.code not in done]

    def allowed_terms(code: str):
        out = []
        for t in cal:
            if not t.usable:
                continue
            if cfg.deadline_index is not None and t.index > cfg.deadline_index:
                continue
            if t.kind == "summer" and cfg.summer_allowed is not None and code not in cfg.summer_allowed:
                continue
            out.append(t)
        return out

    x: dict[tuple[str, int], cp_model.IntVar] = {}
    sel: dict[str, cp_model.IntVar] = {}
    tv: dict[str, cp_model.IntVar] = {}
    n_terms = len(cal)
    dead_required: list[str] = []

    for c in undone:
        at = allowed_terms(c.code)
        if c.required and not at:
            dead_required.append(c.code)
        sel[c.code] = m.NewBoolVar(f"sel_{c.code}")
        tv[c.code] = m.NewIntVar(0, n_terms - 1, f"term_{c.code}")
        lits = []
        for t in at:
            b = m.NewBoolVar(f"x_{c.code}_{t.index}")
            x[(c.code, t.index)] = b
            lits.append((t, b))
        m.Add(sum(b for _, b in lits) == sel[c.code])
        m.Add(tv[c.code] == sum(t.index * b for t, b in lits))
        if c.required:
            m.Add(sel[c.code] == 1)

    # tự chọn: đúng `need` môn mỗi đợt (đã trừ môn đã học)
    for g, members in cur.groups.items():
        done_n = sum(1 for k in members if k in done)
        need = max(0, cfg.elective_need - done_n)
        m.Add(sum(sel[k] for k in members if k not in done) == need)

    # tiên quyết (kỳ sớm hơn) và song hành (cùng kỳ)
    for c in undone:
        for p in c.prereq:
            if p in done:
                continue
            m.Add(sel[c.code] <= sel[p])
            m.Add(tv[c.code] >= tv[p] + 1).OnlyEnforceIf([sel[c.code], sel[p]])
        for d in c.coreq:
            if d in done:
                continue
            m.Add(sel[c.code] <= sel[d])
            m.Add(tv[c.code] == tv[d]).OnlyEnforceIf([sel[c.code], sel[d]])
    for seq in cfg.sequences:
        live = [k for k in seq if k not in done and k in sel]
        for a, b in zip(live, live[1:]):
            m.Add(tv[b] >= tv[a]).OnlyEnforceIf([sel[a], sel[b]])      # không xếp trước; được cùng kỳ
    for g in cfg.term_group_limits:                                    # tối đa n môn của nhóm mỗi kỳ
        members = [k for k in g["courses"] if k not in done and k in sel]
        for t in cal:
            in_t = [x[(k, t.index)] for k in members if (k, t.index) in x]
            if len(in_t) > g["max"]:
                m.Add(sum(in_t) <= g["max"])

    # trần tín chỉ từng kỳ
    loads = {}
    for t in cal:
        terms_x = [(cur.courses[c.code].credits2, x[(c.code, t.index)]) for c in undone if (c.code, t.index) in x]
        if terms_x:
            loads[t.index] = sum(cr * b for cr, b in terms_x)
            cap = effective_cap2(t, st)
            if cap is not None:
                m.Add(loads[t.index] <= cap)

    max_end = max(t.end for t in cal)
    last_end = m.NewIntVar(0, max_end, "last_end")
    for (code, ti), b in x.items():
        m.Add(last_end >= cal[ti].end).OnlyEnforceIf(b)

    PW = 100
    pref_terms = [(int(round(st.preferences.get(c.code, 0) * PW)), sel[c.code])
                  for c in undone if not c.required and st.preferences.get(c.code)]
    pref = sum(w * s for w, s in pref_terms) if pref_terms else 0
    summer_load = sum(loads[t.index] for t in cal if t.kind == "summer" and t.index in loads) if loads else 0
    peak = m.NewIntVar(0, sum(c.credits2 for c in cur.courses.values()), "peak")
    for li in loads.values():
        m.Add(peak >= li)

    if "last_end" in lock:
        m.Add(last_end <= lock["last_end"])
    if "pref" in lock and pref_terms:
        m.Add(pref >= lock["pref"])
    if "summer" in lock:
        m.Add(summer_load <= lock["summer"])

    ctx = dict(x=x, sel=sel, last_end=last_end, pref=pref, summer=summer_load, peak=peak,
               has_pref=bool(pref_terms), dead_required=dead_required)
    return m, ctx


def _run(model, objective, sense, cfg, hint=None):
    if sense == "min":
        model.Minimize(objective)
    else:
        model.Maximize(objective)
    if hint:
        for var, val in hint:
            model.AddHint(var, val)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = cfg.time_limit_s
    s.parameters.num_workers = cfg.num_workers
    s.parameters.random_seed = cfg.seed
    status = s.Solve(model)
    return s, status


def _extract(cur, cfg, ctx, solver) -> tuple[dict[int, list[str]], dict[str, list[str]]]:
    terms: dict[int, list[str]] = {}
    for (code, ti), b in ctx["x"].items():
        if solver.Value(b):
            terms.setdefault(ti, []).append(code)
    for ti in terms:
        terms[ti].sort(key=lambda c: (cur.courses[c].std_term, c))
    chosen: dict[str, list[str]] = {}
    for g, members in cur.groups.items():
        chosen[g] = sorted(k for k in members if k in ctx["sel"] and solver.Value(ctx["sel"][k]))
    return dict(sorted(terms.items())), chosen


def solve(cur: Curriculum, cfg: PlanConfig, st: Student) -> Plan:
    t0 = time.perf_counter()
    plan = Plan(status="UNKNOWN")
    status_name = {cp_model.OPTIMAL: "OPTIMAL", cp_model.FEASIBLE: "FEASIBLE", cp_model.INFEASIBLE: "INFEASIBLE"}

    # trống: không còn gì để học
    if all(c.code in st.done for c in cur.courses.values() if c.required) and \
       all(sum(1 for k in mem if k in st.done) >= cfg.elective_need for mem in cur.groups.values()):
        plan.status = "OPTIMAL"
        plan.wall_s = time.perf_counter() - t0
        return plan

    lock: dict = {}
    proven = True
    best = None

    phase_defs = [("last_end", "min"), ("pref", "max"), ("summer", "min"), ("peak", "min")]
    for name, sense in phase_defs:
        model, ctx = _build(cur, cfg, st, lock)
        if ctx["dead_required"]:
            plan.status = "INFEASIBLE"
            plan.reasons = [f"môn bắt buộc không có kỳ nào xếp được: {', '.join(ctx['dead_required'])}"]
            break
        if name == "pref" and not ctx["has_pref"]:
            continue
        if name == "summer" and not any(t.kind == "summer" and t.usable for t in cfg.calendar):
            continue
        obj = ctx[name]
        hint = None
        if best is not None:
            hint = [(b, best["xv"].get(k, 0)) for k, b in ctx["x"].items()]
        solver, status = _run(model, obj, sense, cfg, hint)
        info = {"phase": name, "status": status_name.get(status, "UNKNOWN"),
                "value": solver.ObjectiveValue() if status in (cp_model.OPTIMAL, cp_model.FEASIBLE) else None,
                "wall_s": round(solver.WallTime(), 3)}
        plan.phases.append(info)

        if status == cp_model.INFEASIBLE:
            if best is None:
                plan.status = "INFEASIBLE"
                plan.reasons = explain_infeasible(cur, cfg, st) or ["Không có lộ trình thỏa mọi ràng buộc."]
            break
        if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            if best is None:
                plan.status = "TIMEOUT"
                plan.reasons = [f"hết thời gian ở pha {name} mà chưa tìm được lộ trình"]
            else:
                proven = False
            break
        if status == cp_model.FEASIBLE:
            proven = False
        val = int(round(solver.ObjectiveValue()))
        lock[{"last_end": "last_end", "pref": "pref", "summer": "summer", "peak": "peak"}[name]] = val
        if name == "peak":
            lock.pop("peak")                     # pha cuối, không cần khóa
        terms, chosen = _extract(cur, cfg, ctx, solver)
        best = {"terms": terms, "chosen": chosen,
                "xv": {k: solver.Value(b) for k, b in ctx["x"].items()},
                "end": solver.Value(ctx["last_end"]), "pref": val if name == "pref" else None}

    if best is not None:
        plan.terms, plan.electives = best["terms"], best["chosen"]
        plan.status = "OPTIMAL" if proven else "FEASIBLE"
        if plan.terms:
            plan.last_index = max(plan.terms)
            plan.end_time = cfg.calendar[plan.last_index].end
        plan.preference_score = sum(st.preferences.get(c, 0) for g in plan.electives.values() for c in g)
    plan.wall_s = time.perf_counter() - t0
    return plan
