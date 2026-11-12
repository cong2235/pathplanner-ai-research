# Gap register (bản nháp v0.1, 2026-11-12)

Điểm 1–5 (5 = nghiêm trọng / thường gặp / chưa ai giải / khả thi). Score = Sev × Freq × Gap × Feas (tối đa 625).
**Độ tin cậy bằng chứng:** H = nguồn đã đọc; M = một phần là suy luận từ nguồn đã đọc; L = chủ yếu snippet/suy luận, cần xác minh. Pain point từ SV/CVHT thật CHƯA thu thập được (mục tiêu ≥30 trích dẫn) → cần khảo sát/phỏng vấn nội bộ VinUni.

| ID | Gap | Evidence | Ai chịu | Vì sao hiện tại chưa giải quyết | Sev | Freq | Gap | Feas | Score | Tin cậy |
|---|---|---|---|---|---|---|---|---|---|---|
| G1 | Tiên quyết được kiểm tra **cứng ở bước đăng ký** (VinUniDigi: "automatically checks prerequisite" – S004), nhưng nguồn đã đọc không mô tả công cụ lập **lộ trình nhiều học kỳ** tối ưu theo tiên quyết + tín chỉ (min 14 / overload 18–22 / summer ≤9) + tiến độ tốt nghiệp. SV chỉ "create an academic plan on the Student Portal" cùng advisor (S024) – tính năng chưa rõ | S001 (Curriculum Planner dạng bảng theo khóa), S002 Điều 11, S004, S024 | SV, CVHT | QLĐT là rule-check theo từng môn; planner là bảng tĩnh theo đúng lộ trình chuẩn | 4 | 5 | 3 | 5 | 300 | M (hạ Gap 4→3 vì cổng SIS có academic plan chưa rõ; cần xin demo/handbook) |
| G2 | **Cá nhân hóa theo mục tiêu** (nghiên cứu / startup / đi làm / học tiếp) chưa gắn với chọn môn tự chọn & concentration; IDP là biểu mẫu thủ công | S001 (concentration AI/Data/Security… "or design own"), S003 (IDP, Faculty Advisor mentoring), S010 | SV năm 2–3 | Advising dựa vào cuộc gặp 1-1; paper KEOD khớp kỹ năng nghề nhưng không ràng buộc CTĐT | 4 | 4 | 4 | 4 | 256 | M |
| G3 | **Chatbot AI hiện có là hỏi-đáp**, chưa có planning grounded có kiểm chứng ràng buộc; claim "cá nhân hóa lộ trình" không mô tả tính năng | S006, S008, S009 | SV | Không nêu solver/kiểm tra tiên quyết; chỉ CMC nêu có trích dẫn nguồn | 4 | 4 | 4 | 4 | 256 | H (vì "không nêu trong bài báo", chưa audit sản phẩm) |
| G4 | **Khối lượng CVHT & thiếu công cụ phân tích**: 10–20 SV/Faculty Advisor, nhiều vai (faculty/professional/peer), early alert; số hóa CVHT mới ở mức thử nghiệm | S003 §4.2, S016 | CVHT | Dashboard nhiều SV với trạng thái tiến độ / rủi ro chưa thấy trong nguồn đã đọc | 4 | 4 | 3 | 5 | 240 | M |
| G5 | **Quy tắc học vụ phức tạp, đổi theo khóa** (warning theo GPA từng năm, probation cần CVHT duyệt, retake, W tối đa, cohort frameworks khác nhau, VinCore thay GenED từ Cohort 2024) → SV khó tự tính | S002 Điều 11–17, S001/S005 | SV, Registrar | Nhiều phiên bản PDF, tiên quyết dưới dạng text tự do → khó máy đọc | 4 | 4 | 4 | 4 | 256 | H/M |
| G6 | **Replan động khi điểm đổi / rớt môn / vào probation**: chưa thấy sản phẩm VN làm | S002 (retake, probation), S011 (chỉ cho nhóm nguy cơ, snippet) | SV rớt môn | Mô hình dự báo (paper) tách khỏi planning có ràng buộc | 5 | 3 | 4 | 4 | 240 | M |
| G7 | **Thiếu đánh giá chuẩn**: các sản phẩm AI VN chỉ có số tự công bố (CMC ~80% hỏi-đáp), paper chưa so baseline/không đo tính hợp lệ lộ trình | S009, S010 | Nhà trường | Chưa có metric "tỷ lệ lộ trình hợp lệ" + LLM-judge giải thích | 3 | 3 | 4 | 5 | 180 | H |
| G8 | **Privacy & bias**: chatbot tuyển sinh theo dõi người hỏi (HUTECH) nhưng không bàn rủi ro; chưa thấy guardrail chống "steer" SV theo hướng cứng nhắc | S007, S009 | SV | Không nêu trong nguồn | 4 | 3 | 4 | 4 | 192 | L (thiếu bằng chứng; đừng claim "chưa ai làm") |

## Shortlist đề xuất (cần bạn xác nhận hướng)
1. **G1+G5 (lõi)**: Chuẩn hóa catalog VinUni thành đồ thị máy đọc (mã môn, tín chỉ, tiên quyết, cohort) + solver cho lộ trình hợp lệ nhiều học kỳ theo quy chế S002.
2. **G2+G3**: LLM chỉ giải thích/đề xuất trong phạm vi solver cho phép, mỗi gợi ý trích điều khoản/mô tả môn (S001, S002).
3. **G4+G6**: Dashboard CVHT + replan khi điểm đổi + cờ rủi ro theo ngưỡng warning/probation của VinUni (S002 Điều 17).
4. **G7+G8**: Eval pipeline công khai (path validity %, LLM-judge, test fairness theo mục tiêu nghề).

## Anti-claims (không nên tuyên bố)
- "Chưa ai ở VN làm lộ trình học bằng AI": chưa quét đủ (FPT, HUST, UEH, NEU, VinUni nội bộ chưa kiểm chứng).
- "VinUni không có degree audit tự động": chỉ có snippet (S023); cần xác minh với Registrar.
- Số liệu dropout 24,45% (S021) và 92,54% (S011): chưa đọc bản gốc.


## Cập nhật 2026-11-12 (sau khi đọc PDF registrar)
- Đính chính: VinUniDigi **có** kiểm tra tiên quyết tự động (S004). Không claim "VinUni chưa kiểm tra tiên quyết"; khác biệt của PathPlanner phải là *lập kế hoạch nhiều học kỳ + giải thích + HITL*, không phải kiểm tra tiên quyết.
- Dữ liệu tiên quyết **không đồng nhất** giữa ngành (mã môn / tên môn / văn bản tự do / None-N/A-NA / "Determined by the advisor", "completed sophomore year") → cần bước chuẩn hóa + người duyệt (xem `DATA_INVENTORY.md`).
- Cần xác minh: tính năng "academic plan" trên sis.vinuni.edu.vn (S024) và Course Registration Handbook (S004).
