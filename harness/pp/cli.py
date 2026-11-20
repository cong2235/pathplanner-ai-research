"""In lộ trình cho một sinh viên giả: python -m pp.cli [--summer] [--done-through K] [--prefer MÃ[=TRỌNG SỐ] ...]"""
from __future__ import annotations

import argparse

from .config import PlanConfig, Student
from .curriculum import load_curriculum
from .diagnose import lower_bounds
from .solver import solve
from .validator import validate


def main(argv=None):
    import sys
    if hasattr(sys.stdout, "reconfigure"):          # console Windows mặc định cp1258 không in được tiếng Việt
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--summer", action="store_true", help="cho phép học hè")
    ap.add_argument("--done-through", type=int, default=0, help="đã xong mọi môn bắt buộc của kỳ chuẩn 1..K")
    ap.add_argument("--prefer", nargs="*", default=[], help="mã môn tự chọn ưu tiên, dạng MÃ hoặc MÃ=trọng số")
    ap.add_argument("--max-credits", type=float, default=None, help="trần tín chỉ/kỳ do SV tự đặt (DUT không có trần quy chế)")
    ap.add_argument("--deadline", type=int, default=None, help="chỉ số kỳ cuối cho phép trong lịch")
    ap.add_argument("--japanese-max", type=int, default=None, help="tối đa bao nhiêu môn Tiếng Nhật mỗi kỳ (mặc định 1)")
    a = ap.parse_args(argv)

    cur = load_curriculum()
    cfg = PlanConfig.from_rules(summer=a.summer, deadline_index=a.deadline)
    if a.japanese_max:
        for g in cfg.term_group_limits:
            if g["name"] == "Tiếng Nhật":
                g["max"] = a.japanese_max
    prefs = {}
    for p in a.prefer:
        code, _, w = p.partition("=")
        prefs[code] = float(w or 1)
    st = Student(done={c.code for c in cur.courses.values() if c.required and c.std_term <= a.done_through},
                 preferences=prefs, max_credits_per_term=a.max_credits)

    plan = solve(cur, cfg, st)
    print(f"Trạng thái: {plan.status}  ({plan.wall_s:.2f}s)  pha: {[(p['phase'], p['status']) for p in plan.phases]}")
    if plan.reasons:
        print("Lý do:", *plan.reasons, sep="\n  - ")
        return 1
    lb = lower_bounds(cur, cfg, st)
    print(f"Cận dưới độc lập: chuỗi ≥ {lb['chain_terms']} kỳ, tín chỉ ≥ {lb['credit_terms']} kỳ")
    for t, codes in plan.terms.items():
        term = cfg.calendar[t]
        print(f"\n{term.label} ({plan.term_credits(cur, t):g} TC)")
        for c in codes:
            co = cur.courses[c]
            tag = " [tự chọn]" if not co.required else ""
            print(f"  {c}  {co.name}  ({co.credits:g}){tag}")
    print("\nTự chọn:", {g: [cur.courses[c].name for c in v] for g, v in plan.electives.items()})
    v = validate(cur, cfg, st, plan.terms)
    print("Validator:", "0 vi phạm" if not v else [x.message for x in v])
    print(f"Kỳ cuối: {cfg.calendar[plan.last_index].label}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
