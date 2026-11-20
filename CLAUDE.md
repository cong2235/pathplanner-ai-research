# PathPlanner AI (EDU-06) – VinUni Project

Agent lập lộ trình học cá nhân hóa (mục tiêu + năng lực + ràng buộc tín chỉ/tiên quyết), có giải thích, grounded vào catalog, cố vấn duyệt (HITL), bảo mật điểm SV.
Stack gợi ý: LangGraph + OR-Tools, pgvector RAG + reranker, Postgres, FastAPI, Next.js, Docker.

## Giai đoạn hiện tại: RESEARCH (chưa implement)
Thứ tự: `competitor-scan` → `gap-analysis` → `research-synthesis` (luôn dùng `source-verification`).
Kết quả nằm trong `research/` (competitors/, gaps/, sources/registry.md, reports/).

## Phạm vi research (user chốt 2026-11-12)
Ưu tiên 1: sinh viên VinUni (catalog, quy chế, advising công khai tại policy.vinuni.edu.vn). Ưu tiên 2: các trường đại học khác của Việt Nam. **KHÔNG nghiên cứu sản phẩm/trường quốc tế** (bỏ qua Stellic, Degree Works… trong competitor-scan). Dataset mở (EdNet, OULAD…) chỉ dùng cho eval, không tính là đối thủ.
Tài liệu VinUni: PDF gốc ở `research/sources/pdfs/`, text trích ở `research/sources/text/`. Nhiều trang vinuni.edu.vn trả 403 với fetch tự động → mở bằng trình duyệt/tải tay.

## Hướng đề tài (user chốt 2026-11-17)
Gợi ý định hướng môn học + lịch học từng kỳ dựa trên: (1) **mục tiêu học tập** của SV, có thể **đổi giữa chừng**; (2) **khung đào tạo** (môn bắt buộc + tự chọn); (3) **thời gian đào tạo mong muốn** (học hè để tốt nghiệp sớm…); (4) **cập nhật thay đổi** đào tạo của trường/khoa từ kênh chính thống để gợi ý kịp thời.

## Quyết định triển khai (user chốt 2026-11-20)
- **Trường demo: DUT (Đại học Bách khoa – ĐH Đà Nẵng), ngành CNTT Việt–Nhật** (đổi so với "VinUni ưu tiên 1" ở trên cho phần dựng MVP; VinUni vẫn là nguồn research). Chỉ làm tốt 1 trường: bỏ multi-school/Helm/multi-tenant, giữ 1 file cấu hình `rules.dut.json`.
- Dữ liệu CTĐT ngành này do user cung cấp (bắt buộc, tự chọn, tiên quyết, các định hướng) → nhập/khóa tay, KHÔNG dùng dòng DUT trong CSV chung (75% `requirement=unknown`, gần như không có mã môn). Dữ liệu SV trong demo luôn là dữ liệu giả có nhãn "MÔ PHỎNG".
- LLM: dự kiến AWS Bedrock (user tạo tài khoản mới, mục tiêu ~US$200 credit, chưa chắc). Chưa kiểm: model/vùng có trên Bedrock, giá Bedrock, điều khoản lưu dữ liệu.
- Solver: port sang Python (OR-Tools CP-SAT), giữ solver JS của mvp-demo làm oracle đối chiếu. Nhúng: Web Component + BFF (Next.js). Observability: log JSON + bảng `run_spans`, không Langfuse.
- Hàng đợi: MVP dùng process pool + bảng job trong Postgres; khi cần replan hàng loạt dùng RQ (không dùng arq).
- `catalog_version` = số phiên bản của toàn bộ ảnh chụp catalog/quy chế. Nguồn thay đổi: thông báo của Phòng Đào tạo DUT (trang đầu web sinh viên, KHÔNG cần đăng nhập → polling có kiểm soát được: allowlist, robots.txt, rate limit, body_hash). Người duyệt: vai trò quản trị catalog (nhóm đồ án) ở giai đoạn đồ án.
- Lưu trữ: log/prompt 15–30 ngày; plan mới nhất (kèm 2–3 bản trước/đã duyệt); nhật ký quyết định cố vấn lưu lâu hơn; TTL cấu hình được.
- Hoãn: ngưỡng nghiệm thu pilot (D10), ngân sách chi tiết (D12). Chi tiết ở `research/reports/harness-tech-analysis.md` mục 8.5.

## Dữ liệu khung đào tạo đa trường
`data/all-universities-curriculum.csv` (13 trường, 386 ngành, 28.091 dòng) → chuẩn hóa bằng `python -I data/scripts/build_catalog.py` → `data/processed/` (bảng quan hệ, graph, embedding). Đọc `data/README.md` trước khi dùng; luật phân loại ở `data/scripts/taxonomy.py`.

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
