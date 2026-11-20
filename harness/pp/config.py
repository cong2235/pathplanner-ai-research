"""Lịch học kỳ, cấu hình lập kế hoạch, trạng thái sinh viên."""
from __future__ import annotations

from dataclasses import dataclass, field

from .curriculum import load_rules


@dataclass(frozen=True)
class Term:
    index: int        # vị trí trong lịch (0..)
    label: str        # "HK1 năm 1", "Hè năm 1"...
    kind: str         # "main" | "summer"
    cap2: int | None  # trần tín chỉ x2 theo quy chế; None = không có trần (DUT)
    usable: bool      # có xếp môn được không (kỳ hè có thể bị tắt)
    end: int          # mốc thời gian kết thúc (cộng dồn độ dài tương đối)


def _cap2(value) -> int | None:
    return None if value is None else int(round(value * 2))


def build_calendar(rules: dict, n_years: int = 6, start: str = "HK1", summer: bool = True) -> list[Term]:
    """Lịch: HK1, HK2, Hè lặp lại. `summer=False` vẫn giữ kỳ hè trong lịch (thời gian vẫn trôi) nhưng không xếp môn được."""
    order = ["HK1", "HK2", "HE"]
    start_i = {"HK1": 0, "HK2": 1, "HE": 2}[start]
    terms: list[Term] = []
    t_end = 0
    for i in range(n_years * 3):
        kind_key = order[(start_i + i) % 3]
        year = (start_i + i) // 3 + 1
        main = kind_key != "HE"
        t_end += rules["duration_main"] if main else rules["duration_summer"]
        terms.append(Term(
            index=i,
            label=f"{'HK1' if kind_key == 'HK1' else 'HK2' if kind_key == 'HK2' else 'Hè'} năm {year}",
            kind="main" if main else "summer",
            cap2=_cap2(rules["max_credits_main"] if main else rules["max_credits_summer"]),
            usable=main or summer,
            end=t_end,
        ))
    return terms


@dataclass
class PlanConfig:
    calendar: list[Term]
    elective_need: int = 2
    sequences: list[list[str]] = field(default_factory=list)       # thứ tự cấp độ: môn sau không xếp trước môn trước
    term_group_limits: list[dict] = field(default_factory=list)    # {"name","courses":[...],"max": n}: tối đa n môn/nhóm mỗi kỳ
    summer_allowed: set[str] | None = None        # None = mọi môn
    deadline_index: int | None = None             # kỳ cuối cho phép (chỉ số trong lịch)
    time_limit_s: float = 10.0                    # mỗi pha tối ưu
    num_workers: int = 4
    seed: int = 7

    @classmethod
    def from_rules(cls, rules: dict | None = None, **overrides) -> "PlanConfig":
        rules = rules or load_rules()
        cal_args = {k: overrides.pop(k) for k in ("n_years", "start", "summer") if k in overrides}
        sa = rules.get("summer_allowed_courses")
        return cls(
            calendar=build_calendar(rules, **cal_args),
            elective_need=rules["elective_need"],
            sequences=[list(s) for s in rules.get("sequences", [])],
            term_group_limits=[dict(g) for g in rules.get("term_group_limits", [])],
            summer_allowed=set(sa) if sa is not None else None,
            **overrides,
        )


@dataclass
class Student:
    done: set[str] = field(default_factory=set)               # học phần đã hoàn thành
    preferences: dict[str, float] = field(default_factory=dict)  # trọng số ưu tiên cho môn tự chọn (mục tiêu học tập)
    max_credits_per_term: float | None = None   # trần tải do chính SV đặt (DUT không có trần quy chế)


def effective_cap2(term: Term, st: Student) -> int | None:
    """Trần tín chỉ x2 áp dụng cho một kỳ: min(trần quy chế, trần SV tự đặt); None = không giới hạn."""
    caps = [c for c in (term.cap2, None if st.max_credits_per_term is None else int(round(st.max_credits_per_term * 2)))
            if c is not None]
    return min(caps) if caps else None
