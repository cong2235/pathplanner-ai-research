# harness (DUT – CNTT Việt–Nhật): lõi lập lộ trình

Lõi deterministic của PathPlanner: nạp khung CTĐT, giải bằng OR-Tools CP-SAT, kiểm tra bằng validator độc lập. Chưa có API, LLM, RAG hay giao diện (xem `research/reports/harness-tech-analysis.md`). Kết quả kiểm thử của bản hiện tại: `TEST_REPORT.md`.

## Chạy
```
cd harness
python -m venv .venv && .venv/Scripts/python -m pip install -r requirements.txt
.venv/Scripts/python -m pytest -q                                  # 34 test
.venv/Scripts/python -m pp.cli --summer --max-credits 16 --prefer 1021673 1022053
```
**Lưu ý phiên bản:** `ortools==9.15.6755` bị segfault ngay cả với mô hình đơn giản trên máy dev này (Windows); đã ghim `9.12.4544`. Khi đổi máy/phiên bản phải chạy lại test.

## Cấu trúc
| File | Vai trò |
|---|---|
| `pp/curriculum.py` | nạp `data/dut/cntt-viet-nhat/curriculum.csv` |
| `pp/config.py` | lịch kỳ (HK1/HK2/Hè), cấu hình, hồ sơ SV |
| `pp/solver.py` | CP-SAT, giải tuần tự 4 pha: ra trường sớm nhất → hợp mục tiêu → ít học hè → cân bằng tải |
| `pp/validator.py` | kiểm tra độc lập (không import solver), mã lỗi `VALIDATE.*` |
| `pp/diagnose.py` | cận dưới độc lập + lý do khi vô nghiệm |
| `rules.dut.json` | tham số; mỗi giá trị ghi rõ nguồn |

## Quy ước mô hình (user xác nhận 2026-11-20)
- Học trước/tiên quyết: xong ở kỳ **sớm hơn**. Nhiều mã trong ô = **đủ tất cả**. Song hành: **cùng kỳ** (hoặc đã học xong).
- Mỗi đợt tự chọn: **đúng 2** môn (trừ môn đã học).
- **DUT không có trần tín chỉ tối đa mỗi kỳ.** Ràng buộc thật là xung đột lịch học trong kỳ; lịch từng môn chỉ biết lúc đăng ký môn học nên **lõi này không kiểm xung đột lịch**. SV có thể tự đặt trần tải (`Student.max_credits_per_term`) để tránh kỳ quá nặng.
- **Kỳ hè chỉ mở một phần môn** (đa số đại cương/nhập môn, không có Tiếng Nhật). Danh sách 14 môn trong `rules.dut.json` do người dựng suy ra từ mô tả, **chưa đối chiếu danh sách mở hè thật**.
- Vô nghiệm: không retry, trả lý do từ cận dưới (chuỗi kỳ, tín chỉ).

- **Được học vượt** trước kỳ chuẩn miễn là đủ tiên quyết và song hành (user xác nhận); không có tham số giới hạn.
- **Tiếng Nhật:** không có quy định cấm 2 môn cùng kỳ, nhưng user khuyên không xếp 2 môn vào 1 kỳ (lập lịch). Mặc định tối đa **1 môn Tiếng Nhật mỗi kỳ** (`term_group_limits`, đổi `max` hoặc `--japanese-max 2` để nới).

## Kết quả đáng chú ý
- **Ra trường sớm nhất = 7 kỳ chính** (khung chuẩn 8 kỳ). Cận này đến từ chuỗi tiên quyết: Kỹ thuật lập trình → Cấu trúc dữ liệu → Nguyên lý HĐH → Mạng máy tính → PBL 4 → Thực tập TN → Đồ án TN. Chuỗi này không đổi dù nới giới hạn Tiếng Nhật, bật học hè hay bỏ trần tải (có test).
- Kỳ hè không rút ngắn thời gian ra trường vì không môn nào trong chuỗi mở hè; nó chỉ giúp giảm tải khi SV tự đặt trần tín chỉ thấp.

## Giả định CHƯA được xác nhận (đổi trong `rules.dut.json`)
- Danh sách môn mở hè (xem trên).
- Thứ tự cấp độ Tiếng Nhật 1..7 (môn sau không xếp trước môn trước; khung không ghi tiên quyết).
- Độ dài tương đối kỳ chính : kỳ hè = 3 : 1 (chỉ để so sánh thời gian).
- Chưa mô hình: thời khóa biểu/sĩ số lớp, điều kiện tích lũy tối thiểu để làm Đồ án.
