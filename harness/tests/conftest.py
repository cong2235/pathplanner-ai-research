import copy
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pp.config import PlanConfig, Student  # noqa: E402
from pp.curriculum import load_curriculum, load_rules  # noqa: E402


@pytest.fixture(scope="session")
def cur():
    return load_curriculum()


@pytest.fixture(scope="session")
def rules():
    return load_rules()


@pytest.fixture
def make_cfg(rules):
    def _make(summer=True, **kw):
        r = copy.deepcopy(rules)
        return PlanConfig.from_rules(r, summer=summer, time_limit_s=kw.pop("time_limit_s", 15.0), **kw)
    return _make


def main_term_indices(cfg):
    return [t.index for t in cfg.calendar if t.kind == "main"]


def standard_plan(cur, cfg, picks=None):
    """Kế hoạch theo đúng kỳ chuẩn của khung (kỳ k -> kỳ chính thứ k trong lịch)."""
    mains = main_term_indices(cfg)
    picks = picks or {g: sorted(m)[:2] for g, m in cur.groups.items()}
    chosen = {c for g in picks.values() for c in g}
    terms = {}
    for c in cur.courses.values():
        if c.required or c.code in chosen:
            terms.setdefault(mains[c.std_term - 1], []).append(c.code)
    return terms
