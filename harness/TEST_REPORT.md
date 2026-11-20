# Biên bản kiểm thử harness (DUT – CNTT Việt–Nhật)

- Thời điểm chạy: 2026-11-20 21:52 (Windows 10)
- Python 3.11.5 · ortools **9.12.4544** · pytest 9.2.0
- Kết quả: **34 passed in 43.37s**
- Git: HEAD `93bea57`; thư mục `harness/` và `data/dut/` **chưa commit** (trạng thái: `?? data/dut/ | ?? harness/`). Vì vậy bản được test được xác định bằng mã băm bên dưới, không phải bằng commit.
- **Mã băm tổng của bản được test:** `4d9f425ff635fe36` (sha256 gộp các file liệt kê bên dưới)

## Các file thuộc bản được test

| File | sha256 (16 ký tự đầu) |
|---|---|
| data/dut/cntt-viet-nhat/curriculum.csv | `89e0017ca28f9221` |
| harness/pp/__init__.py | `80d372dac89d0a1e` |
| harness/pp/cli.py | `bb10a5e35e486aa6` |
| harness/pp/config.py | `d6a97d319e179f71` |
| harness/pp/curriculum.py | `29577c36f2635f7a` |
| harness/pp/diagnose.py | `20ab78350a2da09e` |
| harness/pp/solver.py | `a5e279b62f530b78` |
| harness/pp/validator.py | `1c7cbc17ddb3d202` |
| harness/requirements.txt | `014fd413dfac11ce` |
| harness/rules.dut.json | `f50cd17e7a63d072` |
| harness/tests/conftest.py | `ab02f919b0e88297` |
| harness/tests/test_core.py | `aa63ee529afc8bea` |

## Kết quả từng test

```
tests/test_core.py::test_curriculum_shape PASSED                        
tests/test_core.py::test_elective_combination_count PASSED              
tests/test_core.py::test_standard_plan_is_valid PASSED                  
tests/test_core.py::test_validator_detects_violations PASSED            
tests/test_core.py::test_solver_fresh_student PASSED                    
tests/test_core.py::test_each_group_has_exactly_two_electives PASSED    
tests/test_core.py::test_coreq_courses_share_a_term PASSED              
tests/test_core.py::test_summer_never_slower PASSED                     
tests/test_core.py::test_preferences_steer_elective_choice PASSED       
tests/test_core.py::test_preference_does_not_delay_graduation PASSED    
tests/test_core.py::test_student_with_progress PASSED                   
tests/test_core.py::test_finished_student_gets_empty_plan PASSED        
tests/test_core.py::test_infeasible_deadline_explains_reason PASSED     
tests/test_core.py::test_infeasible_when_student_cap_too_low PASSED     
tests/test_core.py::test_unknown_done_course_is_rejected PASSED         
tests/test_core.py::test_single_worker_is_reproducible PASSED           
tests/test_core.py::test_summer_unused_when_not_needed PASSED           
tests/test_core.py::test_summer_used_only_for_allowed_courses PASSED    
tests/test_core.py::test_prerequisite_chain_alone_needs_seven_terms PASSED
tests/test_core.py::test_japanese_limit_default_one_per_term PASSED     
tests/test_core.py::test_japanese_limit_can_be_relaxed_but_does_not_shorten PASSED
tests/test_core.py::test_student_cap_is_respected PASSED                
tests/test_core.py::test_sweep_every_plan_passes_validator[16-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[16-True] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[18-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[18-True] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[20-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[20-True] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[22-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[22-True] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[25-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[25-True] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[None-False] PASSED
tests/test_core.py::test_sweep_every_plan_passes_validator[None-True] PASSED
```

## Phạm vi và giới hạn

- Test kiểm tra: tính nhất quán dữ liệu (80 môn, 58 bắt buộc/122 TC, 3.025 tổ hợp tự chọn), validator bắt đúng từng loại lỗi, solver cho lộ trình hợp lệ (0 vi phạm theo validator độc lập), không tệ hơn kế hoạch chuẩn, không tốt hơn cận dưới độc lập, vô nghiệm có lý do, tái lập với 1 worker, và quét 12 tổ hợp (trần tải SV × học hè).
- **Chưa kiểm:** so với solver JS (oracle); xung đột thời khóa biểu (chưa có dữ liệu lịch); danh sách môn mở hè thật; thứ tự cấp độ Tiếng Nhật 1..7 (giả định). Học vượt kỳ chuẩn và giới hạn 1 môn Tiếng Nhật/kỳ do user xác nhận. Các điểm còn lại là giả định, ghi trong `harness/README.md` và `rules.dut.json`.
- Thời gian mỗi pha tối ưu bị giới hạn (mặc định 10–15 giây). Nếu hết giờ, solver trả `FEASIBLE` (hợp lệ nhưng chưa chứng minh tối ưu); ca trần tải 16 TC + học hè có thể rơi vào trường hợp này.
- Kết quả đáng chú ý được test: chuỗi tiên quyết một mình đã đòi ≥ 7 kỳ chính (khung chuẩn 8 kỳ); nới giới hạn Tiếng Nhật, bật học hè hay bỏ trần tải đều không rút ngắn thêm.
