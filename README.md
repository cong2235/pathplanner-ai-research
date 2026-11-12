# PathPlanner AI (EDU-06) – Repo research

Nghiên cứu nền cho đề tài **PathPlanner AI**: agent lập lộ trình học cá nhân hóa theo mục tiêu và năng lực (ràng buộc tín chỉ/tiên quyết, giải thích có trích nguồn, cố vấn duyệt – HITL, bảo mật dữ liệu điểm).

> **Trạng thái:** research vòng 1 (bản nháp, 2026-11-12). Chưa implement. Phạm vi: **sinh viên VinUni trước, sau đó các trường đại học Việt Nam; không nghiên cứu sản phẩm quốc tế.**
> Mọi kết luận ở đây là *giả thuyết có bằng chứng ở mức ghi rõ*, chưa phải kết luận cuối.

## Đọc theo thứ tự này (15 phút)

| # | File | Nội dung |
|---|---|---|
| 1 | [research/gaps/gap-register.md](research/gaps/gap-register.md) | 8 vấn đề tồn đọng, có điểm, mức tin cậy bằng chứng, danh sách "không nên tuyên bố" |
| 2 | [research/competitors/_matrix.md](research/competitors/_matrix.md) | Ma trận sản phẩm/paper tương tự ở Việt Nam trên 12 chiều |
| 3 | [research/analysis/FINDINGS.md](research/analysis/FINDINGS.md) | 6 phát hiện từ dữ liệu catalog BSCS |
| 4 | [research/analysis/bscs-prereq-graph.md](research/analysis/bscs-prereq-graph.md) | Đồ thị tiên quyết BSCS và khác biệt giữa 5 phiên bản |
| 5 | [research/sources/DATA_INVENTORY.md](research/sources/DATA_INVENTORY.md) | Kiểm kê tài liệu VinUni đã thu thập, chất lượng dữ liệu, phần còn thiếu |
| 6 | [research/sources/registry.md](research/sources/registry.md) | Sổ nguồn S001–S031 (mỗi claim phải trỏ về đây) |

## Kết quả chính

1. **Thị trường VN:** các trợ lý AI của trường (ĐH CMC, HUFLIT, chatbot tuyển sinh) là *hỏi-đáp thông tin*; trong các bài báo đã đọc không thấy mô tả lập kế hoạch học kỳ hay kiểm tra tiên quyết (S006–S009). Hệ thống quản lý đào tạo thì kiểm tra tiên quyết cứng khi đăng ký.
2. **VinUni:** cổng VinUniDigi (Summer 2026) **có** kiểm tra tiên quyết tự động (S004), nên điểm khác biệt của dự án *không phải* kiểm tra tiên quyết mà là **lập lộ trình nhiều học kỳ + giải thích có trích nguồn + cố vấn duyệt**. Tính năng "academic plan" trên cổng SIS (S024) chưa rõ, cần xác minh.
3. **Dữ liệu catalog:** tiên quyết **đổi theo khóa** dù môn giữ nguyên; mã môn có lỗi trùng (COMP2020 dùng cho 2 môn); định dạng tiên quyết lẫn lộn (mã/tên/văn bản tự do, không rõ AND/OR). → cần catalog có phiên bản + bước người duyệt.
4. **Giả thuyết cần kiểm chứng:** đồ thị tiên quyết BSCS khá thưa (20/49 môn có tiên quyết, chuỗi dài nhất 4 môn); khó khăn thực của sinh viên có thể nằm ở tải tín chỉ, GPA, chọn concentration hơn là tiên quyết. **Chưa có pain point thật từ sinh viên/cố vấn**; đây là bước tiếp theo quan trọng nhất.

## Giới hạn cần biết

- Nhiều trang web VinUni từng trả 403 với fetch tự động; một số nguồn trong registry chỉ là *snippet tìm kiếm* (ghi rõ cột Status) và **chưa được dùng làm bằng chứng**.
- Chưa quét FPT, HUST, UEH, NEU; vì vậy **không được tuyên bố "chưa ai ở Việt Nam làm lộ trình học bằng AI"**.
- Parser đồ thị tiên quyết là heuristic; kết quả phải được người duyệt đối chiếu PDF gốc.
- Dữ liệu công khai không có lịch mở lớp theo học kỳ hay điểm thật.
- Bảng ngưỡng GPA học bổng (S030) bị vỡ định dạng khi trích text, chưa dùng số liệu.

## Cấu trúc repo

```
README.md
CLAUDE.md                     # quy tắc & phạm vi research cho Claude Code
.claude/skills/               # skill: competitor-scan, gap-analysis, source-verification,
                              #   research-synthesis (tự viết) + 8 skill từ anthropics/skills (Apache-2.0)
research/
  competitors/_matrix.md      # ma trận đối thủ
  gaps/gap-register.md        # gap register
  analysis/                   # parser + phân tích BSCS (parse_catalog.py, analyze_bscs.py, *.md, json/)
  sources/
    registry.md  DATA_INVENTORY.md  DOWNLOAD_LIST.md
    pdfs/                     # tài liệu gốc VinUni công khai (xem lưu ý bản quyền)
    text/                     # text trích từ pdfs/ (pypdf), cùng cấu trúc thư mục
  _templates/                 # mẫu profile đối thủ, outline báo cáo
```

## Tái tạo phân tích BSCS

Cần Python 3.11 và `pypdf`.

```bash
cd research/analysis
for f in ../sources/text/curriculum-frameworks/bscs/*.txt; do
  python -I parse_catalog.py "$f" json/$(basename "$f" .txt).json
done
python -I analyze_bscs.py        # ghi bscs-prereq-graph.md
```

Trích lại text từ PDF: dùng `pypdf.PdfReader(...).pages[i].extract_text()` (tất cả PDF đều có text layer, không cần OCR).

## Quy ước làm việc (tóm tắt, chi tiết trong [CLAUDE.md](CLAUDE.md))

- Mọi claim có mã nguồn `S###` trong registry; không có bằng chứng thì ghi "Không tìm thấy bằng chứng".
- Phân biệt *documented / marketing / inference*; ghi ngày truy cập.
- Không đưa dữ liệu cá nhân của sinh viên (điểm, mã sinh viên) vào repo.
- Đây là repo **private** của nhóm. Các PDF trong `research/sources/pdfs/` là tài liệu công khai của VinUni, giữ để đối chiếu nội bộ; không phát tán lại công khai.

## Việc tiếp theo

1. Khảo sát sinh viên + phỏng vấn cố vấn VinUni (ẩn danh, không thu điểm/mã SV) để có pain point thật.
2. Xác minh tính năng "academic plan" trên SIS và degree audit với Registrar.
3. Quét vòng 2: FPT, HUST, UEH, NEU; đọc bản gốc các paper còn ở mức snippet (S011–S014, S021–S022).
4. Chuẩn hóa catalog BSCS thành dữ liệu có phiên bản + người duyệt; mở rộng sang BSDS, BBA, BSEE, BSME.
5. Soạn `implementation-brief.md` (scope MVP/nâng cao, dữ liệu, eval) từ kết quả trên.
