"""Kiểm thử lõi lập lộ trình: dữ liệu, validator, solver, vô nghiệm, tái lập."""
import itertools

import pytest
from conftest import main_term_indices, standard_plan

from pp.config import Student
from pp.diagnose import lower_bounds
from pp.solver import solve
from pp.validator import validate


# ---------- dữ liệu ----------
def test_curriculum_shape(cur):
    assert len(cur.courses) == 80
    req = [c for c in cur.courses.values() if c.required]
    assert len(req) == 58
    assert sum(c.credits2 for c in req) / 2 == 122
    assert {g: len(m) for g, m in cur.groups.items()} == {"KY5_CHON2_TRONG11": 11, "KY7_CHON2_TRONG11": 11}
    assert all(c.credits2 == 4 for g in cur.groups.values() for c in map(cur.get, g))  # mỗi môn tự chọn 2 TC


def test_elective_combination_count(cur):
    from math import comb
    n = 1
    for members in cur.groups.values():
        n *= comb(len(members), 2)
    assert n == 3025


def test_standard_plan_is_valid(cur, make_cfg):
    """Lộ trình theo đúng kỳ chuẩn của khung phải qua validator: kiểm tra chéo dữ liệu chép từ ảnh với quy ước."""
    cfg = make_cfg()
    assert validate(cur, cfg, Student(), standard_plan(cur, cfg)) == []


# ---------- validator bắt đúng từng loại lỗi ----------
def _mut(plan, code, to_term):
    plan = {t: [c for c in cs if c != code] for t, cs in plan.items()}
    plan.setdefault(to_term, []).append(code)
    return plan


def codes_of(v):
    return {x.code for x in v}


def test_validator_detects_violations(cur, make_cfg):
    cfg = make_cfg()
    base = standard_plan(cur, cfg)
    mains = main_term_indices(cfg)
    st = Student()

    # học trước: Giải tích 2 (3190121) cùng kỳ với Giải tích 1
    assert "VALIDATE.prereq_violation" in codes_of(validate(cur, cfg, st, _mut(base, "3190121", mains[0])))
    # song hành: tách Kỹ thuật lập trình khỏi Đại số tuyến tính
    assert "VALIDATE.coreq_violation" in codes_of(validate(cur, cfg, st, _mut(base, "1022863", mains[1])))
    # thiếu môn bắt buộc
    assert "VALIDATE.missing_required" in codes_of(
        validate(cur, cfg, st, {t: [c for c in cs if c != "1023190"] for t, cs in base.items()}))
    # thừa tự chọn (3 môn trong một đợt)
    extra = {t: list(cs) for t, cs in base.items()}
    third = sorted(cur.groups["KY5_CHON2_TRONG11"])[2]
    extra[mains[4]].append(third)
    assert "VALIDATE.elective_count" in codes_of(validate(cur, cfg, st, extra))
    # DUT không có trần quy chế: kế hoạch chuẩn qua; chỉ vượt khi SV tự đặt trần thấp hơn
    assert "VALIDATE.credit_overflow" not in codes_of(validate(cur, cfg, st, base))
    assert "VALIDATE.credit_overflow" in codes_of(validate(cur, cfg, Student(max_credits_per_term=15), base))
    # thứ tự Tiếng Nhật
    seq = _mut(base, "5070030", mains[3])
    assert "VALIDATE.sequence_violation" in codes_of(validate(cur, cfg, st, seq))
    # trùng + mã lạ
    dup = {t: list(cs) for t, cs in base.items()}
    dup[mains[0]].append("3190111")
    dup[mains[0]].append("9999999")
    got = codes_of(validate(cur, cfg, st, dup))
    assert {"VALIDATE.duplicate", "VALIDATE.unknown_course"} <= got
    # kỳ hè bị tắt
    nosummer = make_cfg(summer=False)
    summer_idx = next(t.index for t in nosummer.calendar if t.kind == "summer")
    assert "VALIDATE.course_not_offered" in codes_of(validate(cur, nosummer, st, _mut(base, "5070040", summer_idx)))
    # kỳ hè bật: Tiếng Nhật và môn chuyên ngành không mở hè; môn đại cương thì có
    withsummer = make_cfg(summer=True)
    s_idx = next(t.index for t in withsummer.calendar if t.kind == "summer")
    assert "VALIDATE.course_not_offered" in codes_of(validate(cur, withsummer, st, _mut(base, "5070040", s_idx)))
    assert "VALIDATE.course_not_offered" in codes_of(validate(cur, withsummer, st, _mut(base, "1023280", s_idx)))
    assert "VALIDATE.course_not_offered" not in codes_of(validate(cur, withsummer, st, _mut(base, "2100010", s_idx)))


# ---------- solver ----------
def test_solver_fresh_student(cur, make_cfg):
    cfg = make_cfg(summer=False)
    st = Student()
    plan = solve(cur, cfg, st)
    assert plan.status == "OPTIMAL"
    assert validate(cur, cfg, st, plan.terms) == []
    lb = lower_bounds(cur, cfg, st)
    assert plan.end_time >= lb["lb_end"]                      # solver không thể tốt hơn cận dưới
    std_end = cfg.calendar[main_term_indices(cfg)[7]].end
    assert plan.end_time <= std_end                           # không tệ hơn kế hoạch chuẩn 8 kỳ


def test_each_group_has_exactly_two_electives(cur, make_cfg):
    plan = solve(cur, make_cfg(summer=False), Student())
    assert {g: len(v) for g, v in plan.electives.items()} == {g: 2 for g in cur.groups}


def test_coreq_courses_share_a_term(cur, make_cfg):
    plan = solve(cur, make_cfg(), Student())
    where = {c: t for t, cs in plan.terms.items() for c in cs}
    for code, t in where.items():
        for d in cur.get(code).coreq:
            assert where[d] == t, f"{code} và {d} phải cùng kỳ"


def test_summer_never_slower(cur, make_cfg):
    st = Student()
    with_summer = solve(cur, make_cfg(summer=True), st)
    without = solve(cur, make_cfg(summer=False), st)
    assert with_summer.status == without.status == "OPTIMAL"
    assert with_summer.end_time <= without.end_time


def test_preferences_steer_elective_choice(cur, make_cfg):
    by_name = {c.name: c.code for c in cur.courses.values()}
    want = [by_name["Thị giác máy tính"], by_name["Khai phá dữ liệu"],
            by_name["Lập trình Python"], by_name["Đồ họa máy tính"]]
    st = Student(preferences={c: 1.0 for c in want})
    cfg = make_cfg(summer=False)
    plan = solve(cur, cfg, st)
    assert plan.status == "OPTIMAL"
    assert sorted(c for g in plan.electives.values() for c in g) == sorted(want)
    assert validate(cur, cfg, st, plan.terms) == []

    net = [by_name["Mã hóa và mật mã"], by_name["Thiết kế Hệ thống mạng"],
           by_name["An toàn Thông tin mạng"], by_name["Phân tích và xử lý mã độc"]]
    st2 = Student(preferences={c: 1.0 for c in net})
    plan2 = solve(cur, cfg, st2)
    assert sorted(c for g in plan2.electives.values() for c in g) == sorted(net)


def test_preference_does_not_delay_graduation(cur, make_cfg):
    """Ưu tiên của SV chỉ phá hòa sau khi đã ra trường sớm nhất."""
    cfg = make_cfg(summer=False)
    base = solve(cur, cfg, Student())
    steered = solve(cur, cfg, Student(preferences={"1021673": 5.0}))
    assert steered.end_time == base.end_time


def test_student_with_progress(cur, make_cfg):
    done = {c.code for c in cur.courses.values() if c.required and c.std_term <= 4}
    st = Student(done=done)
    cfg = make_cfg(summer=False)
    plan = solve(cur, cfg, st)
    assert plan.status == "OPTIMAL"
    planned = {c for cs in plan.terms.values() for c in cs}
    assert not (planned & done)
    assert validate(cur, cfg, st, plan.terms) == []


def test_finished_student_gets_empty_plan(cur, make_cfg):
    done = {c.code for c in cur.courses.values() if c.required}
    for members in cur.groups.values():
        done.update(sorted(members)[:2])
    plan = solve(cur, make_cfg(), Student(done=done))
    assert plan.status == "OPTIMAL" and plan.terms == {}


# ---------- vô nghiệm ----------
def test_infeasible_deadline_explains_reason(cur, make_cfg):
    cfg = make_cfg(summer=False, deadline_index=4)            # chỉ 3 kỳ chính đầu tiên
    st = Student()
    plan = solve(cur, cfg, st)
    assert plan.status == "INFEASIBLE"
    assert plan.reasons and any("kỳ" in r for r in plan.reasons)
    assert [p["phase"] for p in plan.phases] == ["last_end"]  # không retry, dừng ngay


def test_infeasible_when_student_cap_too_low(cur, make_cfg):
    cfg = make_cfg(summer=False, n_years=6)                  # 6 năm × 2 kỳ × 8 TC = 96 < 130
    plan = solve(cur, cfg, Student(max_credits_per_term=8))
    assert plan.status == "INFEASIBLE"
    assert any("tín chỉ" in r for r in plan.reasons)


def test_unknown_done_course_is_rejected(cur, make_cfg):
    with pytest.raises(ValueError):
        solve(cur, make_cfg(), Student(done={"0000000"}))


# ---------- tái lập ----------
def test_single_worker_is_reproducible(cur, make_cfg):
    cfg = make_cfg(summer=True, num_workers=1)
    a, b = solve(cur, cfg, Student()), solve(cur, cfg, Student())
    assert a.terms == b.terms and a.electives == b.electives


# ---------- kỳ hè và trần tải do SV đặt ----------
def test_summer_unused_when_not_needed(cur, make_cfg):
    """Không có trần tải: ra trường sớm nhất đã đạt bằng kỳ chính, pha 'ít học hè' đưa kỳ hè về 0."""
    cfg = make_cfg(summer=True)
    plan = solve(cur, cfg, Student())
    assert not any(cfg.calendar[t].kind == "summer" for t in plan.terms)


def test_summer_used_only_for_allowed_courses(cur, make_cfg):
    cfg = make_cfg(summer=True)
    st = Student(max_credits_per_term=16)      # trần tải thấp → kỳ hè hữu ích
    plan = solve(cur, cfg, st)
    # pha "ít học hè" có thể mất ~10 giây để chứng minh tối ưu; hết giờ thì trả FEASIBLE (hợp lệ, chưa chứng minh tối ưu)
    assert plan.status in ("OPTIMAL", "FEASIBLE")
    summer_courses = {c for t, cs in plan.terms.items() if cfg.calendar[t].kind == "summer" for c in cs}
    assert summer_courses, "với trần 16 TC, kế hoạch phải dùng kỳ hè"
    assert summer_courses <= cfg.summer_allowed
    assert not any(cur.get(c).name.startswith("Tiếng Nhật") for c in summer_courses)
    assert validate(cur, cfg, st, plan.terms) == []


def test_prerequisite_chain_alone_needs_seven_terms(cur, make_cfg):
    """Chuỗi Kỹ thuật lập trình → CTDL → Nguyên lý HĐH → Mạng máy tính → PBL4 → Thực tập TN → Đồ án TN
    dài 7 môn, mỗi môn ở kỳ sau môn trước và không môn nào mở hè → ≥ 7 kỳ chính, bất kể Tiếng Nhật hay học hè."""
    for summer in (False, True):
        cfg = make_cfg(summer=summer)
        cfg.sequences, cfg.term_group_limits = [], []          # bỏ hết ràng buộc Tiếng Nhật
        assert lower_bounds(cur, cfg, Student())["chain_terms"] == 7
        plan = solve(cur, cfg, Student())
        assert plan.end_time == cfg.calendar[main_term_indices(cfg)[6]].end


def test_japanese_limit_default_one_per_term(cur, make_cfg):
    cfg = make_cfg(summer=False)
    plan = solve(cur, cfg, Student())
    for t, cs in plan.terms.items():
        assert sum(1 for c in cs if c.startswith("5070")) <= 1


def test_japanese_limit_can_be_relaxed_but_does_not_shorten(cur, make_cfg):
    base = standard_plan(cur, make_cfg(summer=False))
    mains = main_term_indices(make_cfg(summer=False))
    two_in_one = _mut(base, "5070040", mains[0])               # Tiếng Nhật 2 cùng kỳ với Tiếng Nhật 1
    strict = make_cfg(summer=False)
    assert "VALIDATE.term_group_limit" in codes_of(validate(cur, strict, Student(), two_in_one))
    relaxed = make_cfg(summer=False)
    relaxed.term_group_limits[0]["max"] = 2
    assert validate(cur, relaxed, Student(), two_in_one) == []
    # nới giới hạn không làm ra trường sớm hơn (chuỗi tiên quyết mới là ràng buộc chặt)
    p_strict, p_relaxed = solve(cur, strict, Student()), solve(cur, relaxed, Student())
    assert p_relaxed.end_time == p_strict.end_time
    assert validate(cur, relaxed, Student(), p_relaxed.terms) == []


def test_student_cap_is_respected(cur, make_cfg):
    cfg = make_cfg(summer=False)
    st = Student(max_credits_per_term=18)
    plan = solve(cur, cfg, st)
    assert plan.status == "OPTIMAL"
    assert all(plan.term_credits(cur, t) <= 18 for t in plan.terms)
    assert validate(cur, cfg, st, plan.terms) == []


# ---------- quét tham số (tinh thần sweep 1.920 tổ hợp của mvp/) ----------
@pytest.mark.parametrize("cap,summer", list(itertools.product([16, 18, 20, 22, 25, None], [False, True])))
def test_sweep_every_plan_passes_validator(cur, make_cfg, cap, summer):
    cfg = make_cfg(summer=summer, time_limit_s=10.0)
    st = Student(preferences={"1021673": 1.0, "1020503": 0.5}, max_credits_per_term=cap)
    plan = solve(cur, cfg, st)
    assert plan.status in ("OPTIMAL", "FEASIBLE", "INFEASIBLE")
    if plan.status == "INFEASIBLE":
        assert plan.reasons
    else:
        assert validate(cur, cfg, st, plan.terms) == [], f"cap={cap} summer={summer}"
        assert plan.end_time >= lower_bounds(cur, cfg, st)["lb_end"]
