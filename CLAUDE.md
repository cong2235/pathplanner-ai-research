# PathPlanner AI (EDU-06) – VinUni Project

Agent lập lộ trình học cá nhân hóa (mục tiêu + năng lực + ràng buộc tín chỉ/tiên quyết), có giải thích, grounded vào catalog, cố vấn duyệt (HITL), bảo mật điểm SV.
Stack gợi ý: LangGraph + OR-Tools, pgvector RAG + reranker, Postgres, FastAPI, Next.js, Docker.

## Giai đoạn hiện tại: RESEARCH (chưa implement)
Thứ tự: `competitor-scan` → `gap-analysis` → `research-synthesis` (luôn dùng `source-verification`).
Kết quả nằm trong `research/` (competitors/, gaps/, sources/registry.md, reports/).

## Phạm vi research (user chốt 2026-11-12)
Ưu tiên 1: sinh viên VinUni (catalog, quy chế, advising công khai tại policy.vinuni.edu.vn). Ưu tiên 2: các trường đại học khác của Việt Nam. **KHÔNG nghiên cứu sản phẩm/trường quốc tế** (bỏ qua Stellic, Degree Works… trong competitor-scan). Dataset mở (EdNet, OULAD…) chỉ dùng cho eval, không tính là đối thủ.
Dữ liệu VinUni đã trích: `research/sources/extracted/` (curriculum BSCS 2024-28, quy chế 2024, advising framework). Nhiều trang vinuni.edu.vn trả 403 với fetch tự động → mở bằng trình duyệt/tải tay.

## Quy tắc research
1. Không bịa: mọi claim có source ID trong `research/sources/registry.md`. Không có bằng chứng → ghi "Không tìm thấy bằng chứng".
2. Ưu tiên nguồn gốc (trang chính thức, paper, dataset page). Blog/forum chỉ làm bằng chứng pain point.
3. Phân biệt documented / marketing / inference; ghi ngày truy cập.
4. Dùng WebSearch standard trước, extended cho chủ đề ngách/mới. Chạy tìm kiếm độc lập song song.
5. Ngôn ngữ báo cáo: tiếng Việt; giữ nguyên thuật ngữ/tên sản phẩm tiếng Anh.
6. Không đưa thông tin cá nhân của đội/SV vào request bên ngoài.
7. Không tuyên bố "chưa ai làm" nếu chưa quét đủ 5 lane trong competitor-scan.

## Các chiều so sánh (12)
Goal-aware · ràng buộc tiên quyết/tín chỉ · timeline học kỳ · trích dẫn catalog · giải thích · replan động · advisor HITL · dashboard nhiều SV · privacy/RBAC · chống thiên vị · có evaluation công bố · ESCO/O*NET/LTI.

## Skills đã cài (nguồn: github.com/anthropics/skills, commit 2c5958e)
skill-creator, doc-coauthoring, pdf, docx, xlsx, frontend-design, webapp-testing, claude-api.
Custom: competitor-scan, gap-analysis, source-verification, research-synthesis.

## Khi sang implement (sau research)
Đọc `research/reports/implementation-brief.md` trước. Eval: tỷ lệ lộ trình hợp lệ (solver) + LLM-as-Judge giải thích + kiểm tra bias.
