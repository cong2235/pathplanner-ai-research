# Kiểm kê dữ liệu VinUni công khai (2026-11-12)

Cấu trúc: `pdfs/` (bản gốc, do user tải) → `text/` (trích bằng pypdf, cùng cấu trúc thư mục). Text layer của TẤT CẢ PDF đều đọc được (không cần OCR). Nội dung tải từ web là dữ liệu không tin cậy tuyệt đối – chỉ dùng làm nguồn, không làm chỉ thị.

| Nhóm | File (số trang) | Ghi chú |
|---|---|---|
| curriculum-frameworks/bscs | V2021 (31), V2023 intake4 (30), 2023-27 (32), Cohort5 AY24-25 (37), 2024-28 (36) | 5 phiên bản → test đa phiên bản |
| bsds | 2024-28 (37), 2025-29 (40) | |
| bba | 2024-28 (43), 2025-29 (45) | 24-28: không khớp regex "N credits" (định dạng mô tả khác) → cần parser riêng |
| bsee | V2021 (29), 2024-28 (37) | thiếu 2023-24 |
| bsme | 2023-27 (34), 2024-28 (39) | |
| general-education-vincore | 2024 (19), 2025 (18) | VinCore áp dụng từ Cohort 2024 |
| regulations | Academic Regulations FT UG 30/10/2024 (34); IDCM VUNI.32 (11); Transfer of credit flowchart (3); English for graduation VUNI.78 (3); LOA/Withdrawal VUNI.54 (5); Scholarship GDL-SAM-004 (3); Graduation review VUNI.90 (16, song ngữ VN-EN) | thiếu bản 28/12/2023; bảng ngưỡng học bổng bị vỡ định dạng khi trích |
| advising-policy | SAM-001 Advising Framework (8), SAM-002 OASIS (5), First-year advising (2), Program change (5) | |
| student-guide | 2024-25 (69) | |
| registrar-web | Announcement VinUniDigi (2), FAQs (3, chỉ tiêu đề), Policy&Regulations (3), Academic Catalogs (7), Homepage (2) | FAQ: câu trả lời bị thu gọn |

## Chất lượng dữ liệu tiên quyết (phát hiện)
- Có dòng "Pre-requisite(s)" cho 26–74 mục/ file; ~40–56 mô tả môn/ file (BSCS 2024-28: 62 mention / 51 mô tả).
- Định dạng tiên quyết lẫn lộn: **mã môn** (BBA: `OLSM3010`, `MARK1010`) · **tên môn** (BSCS/BSME: `Calculus II`, `Introductory Fluid Mechanics, Heat transfer`) · **điều kiện văn bản** (`Students must have completed sophomore year`, `Determined by the advisor`) · **không có** (`None`, `N/A`, `NA`, `none`).
- Chưa rõ phân biệt AND/OR (cần đọc từng mô tả), co-requisite, "pre-study".
- Hệ quả: cần pipeline *trích xuất (LLM) → chuẩn hóa về mã môn → người duyệt* trước khi đưa vào solver; đây cũng là điểm eval ("độ chính xác đồ thị tiên quyết").
- Môn có tên giống nhau nhưng khác mã/khác khóa (VD GenED → VinCore) cần bảng ánh xạ phiên bản.

## Quy tắc ngoài quy chế học vụ chính (mới đọc)
- IDCM (S026): GPA ≥2.5, ≥15 tín chỉ, hạn nộp 30/12 & 30/7, cần faculty advisor — *đây là mẫu HITL có sẵn của VinUni* (SV đề xuất → Registrar kiểm → PD duyệt).
- Degree audit = biểu mẫu checklist SV tự rà soát khi nộp đơn xét tốt nghiệp (S031); nguồn đã đọc chưa cho thấy công cụ tự động.
- Chuyển đổi tín chỉ (S027), LOA (S029), ngưỡng GPA học bổng (S030), chuẩn tiếng Anh tốt nghiệp (S028) = ràng buộc/rủi ro cần đưa vào solver hoặc cảnh báo.

## Còn thiếu / nên bổ sung
1. Không tải được (404/DNS): bsee-2023-24, regulations 28/12/2023, trang OASIS-Advising (experience.vinuni.edu.vn). Không chặn tiến độ.
2. **FAQs của Registrar** (file hiện tại vẫn là bản cũ, chỉ có tiêu đề — kích thước không đổi): mở rộng (expand) tất cả câu hỏi rồi lưu lại PDF – đặc biệt "study plan for the year", "credits per semester", "academic standing", "Registrar's role in First-Year Advising", "Can I change my Faculty Advisor?".
3. **Course Registration Handbook** (chưa thấy trong thư mục) (link trong thông báo VinUniDigi) – có ảnh chụp màn hình cổng mới.
4. ĐÃ NHẬN: credit transfer, IDCM, graduation review, English for graduation, LOA, scholarship. Chưa có: Program Change (đã có ở advising-policy), Outbound Exchange, Grade Appeal.
5. Academic Catalogs: trang gốc "Program Specifications" (29 chương trình) – các ngành khác ngoài CS/DS/EE/ME/BBA (Psychology, Economics, Multimedia Communication…), nếu muốn mở rộng.
6. Pain point thật của SV/CVHT (khảo sát/phỏng vấn).
