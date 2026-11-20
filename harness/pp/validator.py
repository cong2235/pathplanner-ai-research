"""Validator độc lập với solver (không import solver, không dùng CP-SAT).

Kiểm tra một lộ trình theo đúng quy ước đã chốt với user (2026-11-20):
- học trước / tiên quyết: môn phải xong ở kỳ SỚM HƠN (hoặc đã hoàn thành trước kế hoạch);
- học song hành: cùng kỳ (hoặc đã hoàn thành trước kế hoạch);
- nhiều mã trong một ô = cần ĐỦ TẤT CẢ;
- mỗi đợt tự chọn: đúng `elective_need` môn (tính cả môn đã học);
Mã lỗi theo taxonomy của harness (VALIDATE.*).
"""
from __future__ import annotations

from dataclasses import dataclass

from .config import PlanConfig, Student, effective_cap2
from .curriculum import Curriculum


@dataclass(frozen=True)
class Violation:
    code: str
    message: str
    course: str = ""


def validate(cur: Curriculum, cfg: PlanConfig, st: Student, terms: dict[int, list[str]]) -> list[Violation]:
    v: list[Violation] = []
    done = set(st.done)

    where: dict[str, int] = {}
    for t_idx, codes in terms.items():
        for code in codes:
            if code not in cur.courses:
                v.append(Violation("VALIDATE.unknown_course", f"mã {code} không có trong khung", code))
                continue
            if code in done:
                v.append(Violation("VALIDATE.duplicate", f"{code} đã hoàn thành nhưng bị xếp lại", code))
            if code in where:
                v.append(Violation("VALIDATE.duplicate", f"{code} bị xếp 2 lần (kỳ {where[code]} và {t_idx})", code))
            where[code] = t_idx

    # kỳ hợp lệ, kỳ hè, trần tín chỉ
    for t_idx, codes in terms.items():
        if not (0 <= t_idx < len(cfg.calendar)):
            v.append(Violation("VALIDATE.course_not_offered", f"kỳ {t_idx} không có trong lịch"))
            continue
        term = cfg.calendar[t_idx]
        if codes and not term.usable:
            v.append(Violation("VALIDATE.course_not_offered", f"{term.label} không xếp được môn"))
        if cfg.deadline_index is not None and codes and t_idx > cfg.deadline_index:
            v.append(Violation("VALIDATE.course_not_offered", f"{term.label} vượt hạn kỳ cuối"))
        if term.kind == "summer" and cfg.summer_allowed is not None:
            for code in codes:
                if code not in cfg.summer_allowed:
                    v.append(Violation("VALIDATE.course_not_offered", f"{code} không mở ở {term.label}", code))
        total2 = sum(cur.courses[c].credits2 for c in codes if c in cur.courses)
        cap = effective_cap2(term, st)
        if cap is not None and total2 > cap:
            v.append(Violation("VALIDATE.credit_overflow",
                               f"{term.label}: {total2 / 2:g} TC > trần {cap / 2:g} TC"))

    # môn bắt buộc phải có
    for c in cur.courses.values():
        if c.required and c.code not in done and c.code not in where:
            v.append(Violation("VALIDATE.missing_required", f"thiếu môn bắt buộc {c.code} {c.name}", c.code))

    # tự chọn: đúng số môn mỗi đợt
    for g, members in cur.groups.items():
        n = sum(1 for m in members if m in done) + sum(1 for m in members if m in where)
        if n != cfg.elective_need:
            v.append(Violation("VALIDATE.elective_count",
                               f"đợt {g}: có {n} môn tự chọn, cần đúng {cfg.elective_need}"))

    # tiên quyết / song hành
    for code, t_idx in where.items():
        if code not in cur.courses:
            continue
        c = cur.courses[code]
        for p in c.prereq:
            if p in done:
                continue
            if p not in where:
                v.append(Violation("VALIDATE.prereq_violation", f"{code} cần {p} nhưng {p} không có trong kế hoạch", code))
            elif where[p] >= t_idx:
                v.append(Violation("VALIDATE.prereq_violation",
                                   f"{code} (kỳ {t_idx}) cần {p} xong ở kỳ sớm hơn (đang ở kỳ {where[p]})", code))
        for d in c.coreq:
            if d in done:
                continue
            if d not in where:
                v.append(Violation("VALIDATE.coreq_violation", f"{code} cần học song hành {d} nhưng {d} không có trong kế hoạch", code))
            elif where[d] != t_idx:
                v.append(Violation("VALIDATE.coreq_violation",
                                   f"{code} (kỳ {t_idx}) phải cùng kỳ với {d} (đang ở kỳ {where[d]})", code))

    # thứ tự cấp độ (không xếp môn sau trước môn trước; được cùng kỳ)
    for seq in cfg.sequences:
        live = [x for x in seq if x not in done and x in where]
        for a, b in zip(live, live[1:]):
            if where[a] > where[b]:
                v.append(Violation("VALIDATE.sequence_violation", f"{a} không được xếp sau {b}", b))

    # tối đa n môn của một nhóm mỗi kỳ (ví dụ Tiếng Nhật)
    for g in cfg.term_group_limits:
        per_term: dict[int, list[str]] = {}
        for code in g["courses"]:
            if code in where and code not in done:
                per_term.setdefault(where[code], []).append(code)
        for t_idx, codes in per_term.items():
            if len(codes) > g["max"]:
                v.append(Violation("VALIDATE.term_group_limit",
                                   f"{g['name']}: {len(codes)} môn ở kỳ {t_idx} (tối đa {g['max']}): {', '.join(codes)}"))
    return v
