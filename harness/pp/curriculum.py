"""Nạp khung chương trình đào tạo từ CSV chuẩn hóa (data/dut/cntt-viet-nhat/curriculum.csv)."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CSV = ROOT / "data" / "dut" / "cntt-viet-nhat" / "curriculum.csv"
DEFAULT_RULES = Path(__file__).resolve().parents[1] / "rules.dut.json"


@dataclass(frozen=True)
class Course:
    code: str
    name: str
    credits2: int            # tín chỉ nhân 2 (để tránh số thực: 2,5 TC = 5)
    std_term: int            # kỳ chuẩn trong khung (1..8)
    required: bool
    group: str               # "" nếu bắt buộc
    prereq: tuple[str, ...]  # học trước + tiên quyết: phải xong ở kỳ SỚM HƠN
    coreq: tuple[str, ...]   # học song hành: cùng kỳ (nếu chưa học xong)

    @property
    def credits(self) -> float:
        return self.credits2 / 2


@dataclass
class Curriculum:
    courses: dict[str, Course]
    groups: dict[str, list[str]] = field(default_factory=dict)

    def __post_init__(self):
        self.groups = {}
        for c in self.courses.values():
            if c.group:
                self.groups.setdefault(c.group, []).append(c.code)

    def get(self, code: str) -> Course:
        return self.courses[code]


def _split(s: str) -> tuple[str, ...]:
    return tuple(x for x in s.split(";") if x)


def load_curriculum(path: Path | str = DEFAULT_CSV) -> Curriculum:
    courses: dict[str, Course] = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            code = r["ma_hp"]
            if code in courses:
                raise ValueError(f"trùng mã học phần {code}")
            courses[code] = Course(
                code=code,
                name=r["ten_hp"],
                credits2=int(round(float(r["so_tin_chi"]) * 2)),
                std_term=int(r["hoc_ky"]),
                required=r["loai"] == "bat_buoc",
                group=r["nhom_tu_chon"],
                prereq=_split(r["hoc_truoc"]) + _split(r["tien_quyet"]),
                coreq=_split(r["song_hanh"]),
            )
    cur = Curriculum(courses)
    for c in courses.values():  # mọi mã tham chiếu phải tồn tại
        for x in c.prereq + c.coreq:
            if x not in courses:
                raise ValueError(f"{c.code} tham chiếu mã không có trong khung: {x}")
    return cur


def load_rules(path: Path | str = DEFAULT_RULES) -> dict:
    """Trả về dict {khóa: giá trị} (bỏ lớp bọc nguon/ghi_chu)."""
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: v["value"] for k, v in raw.items() if isinstance(v, dict) and "value" in v}
