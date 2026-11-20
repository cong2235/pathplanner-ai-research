# Phân tích công nghệ: dựng và đóng gói harness PathPlanner AI để tích hợp vào cổng sinh viên

Ngày: 2026-11-20 · Vai trò: AI infrastructure / MLOps / platform · Trạng thái: nháp v0.1 để nhóm quyết định
Phạm vi: bối cảnh đại học Việt Nam (VinUni trước). Công cụ hạ tầng dùng được toàn cầu; không khảo sát sản phẩm/trường quốc tế như đối thủ.
Nguồn mới: **S052–S078** trong `research/sources/registry.md` (truy cập 2026-11-20). Nguồn cũ dùng lại: S032–S045 (giá API, tool use, citations, luật dữ liệu, paper RAG cục bộ), S046–S050 (DUT).

Nhãn bằng chứng:
- **[D]** documented, đã mở và đọc trang nguồn (status "read" trong registry).
- **[D-s]** documented nhưng chỉ thấy đoạn trích trong kết quả tìm kiếm (status "snippet"): cần mở bản gốc trước khi dựa vào chi tiết.
- **[M]** marketing/blog/bên thứ ba.
- **[I]** inference, ý kiến của người phân tích, không phải sự thật đã kiểm chứng.
- **[P]** đề xuất/ngưỡng do mình đặt, không lấy từ nguồn.

---

## 0. Tóm tắt điều hành (10 dòng)

1. **Đóng gói:** harness là **dịch vụ độc lập** (FastAPI + worker + Postgres/pgvector + Redis) có hợp đồng OpenAPI `/v1`; không làm thư viện nhúng vào backend của trường, vì mỗi trường một stack khác nhau [I].
2. **Nhúng vào web SV:** đồ án dùng **Web Component (custom element) + reverse proxy/BFF cùng origin của cổng**; iframe là phương án dự phòng cho cổng khó sửa; token không bao giờ nằm trong JS của trình duyệt (mục 1).
3. **Danh tính:** cổng của trường làm SSO (OIDC); harness chỉ tin **JWT ngắn hạn do BFF của trường ký** (hoặc token exchange RFC 8693, S071), lấy `tenant/role/student_pseudonym` từ token, **không** từ body hay từ tham số LLM. Tool schema của `mvp-demo` đã đúng hướng: `get_student_summary` không có tham số `student_id` (mục 2).
4. **Dữ liệu SIS:** mô hình **canonical + adapter theo trường** (hợp đồng tương tự `SRS-01..09` đã có trong `mvp-demo`); khung đào tạo **đồng bộ có version**, hồ sơ SV **truy vấn trực tiếp lúc chạy rồi chụp snapshot** vào run; thông báo của trường đi qua hàng đợi "ứng viên thay đổi" có người duyệt trước khi tăng `catalog_version` (mục 2.5).
5. **Riêng tư:** quy tắc số một là **tối thiểu hóa**: prompt chỉ chứa mã môn/trạng thái, không chứa tên, MSSV, điểm số. Presidio **không có tiếng Việt sẵn** (S060), nên không dựa vào NER để che PII mà dựa vào cấu trúc dữ liệu + regex + RLS (mục 3).
6. **Pháp lý:** có nguồn thứ cấp cho Luật BVDLCN 91/2025 và NĐ 356/2025 (hiệu lực 1/1/2026): hồ sơ đánh giá tác động chuyển dữ liệu ra nước ngoài (CTIA) khi dùng LLM/cloud nước ngoài (S036, S077). API Anthropic **không có vùng Việt Nam** (S032). **Pilot dữ liệu thật phải qua pháp chế của trường** (mục 3.7).
7. **Công nghệ:** LangGraph + PostgresSaver, LiteLLM gateway, OR-Tools CP-SAT chạy **tiến trình riêng có hard timeout**, pgvector + BM25/FTS + RRF + `bge-m3`/`bge-reranker-v2-m3` (cần tự benchmark tiếng Việt), Langfuse tự host *hoặc* JSON log + OTel ở mức đồ án, Promptfoo/pytest cho eval (mục 4).
8. **Triển khai:** docker-compose 8–9 service cho demo (mục 5.2); production nên **một bản triển khai riêng cho mỗi trường (silo)** bằng Helm, không vội multi-tenant dùng chung; RLS chỉ là lớp phòng thủ thứ hai.
9. **Chi phí/độ tin cậy:** ước tính **~US$0,018/plan** với Sonnet 5.5 cho bước giải thích + Haiku 5.5 cho bước hiểu mục tiêu (giả định mục 7.3), ~US$0,001 nếu cả hai dùng Haiku. Khi LLM lỗi, hệ thống trả plan + **giải thích bằng template xác định** (mục 7.4).
10. **Lộ trình:** Demo → Pilot 1 trường → Multi-school, mỗi giai đoạn có tiêu chí đo được (mục 8); 12 quyết định cần người dùng chốt, trong đó **trường mô phỏng cổng (VinUni hay DUT)** và **LLM ngoài vs tự host** là hai quyết định chặn nhiều việc nhất.

---

## Hiện trạng đã có (để khỏi làm lại)

| Thành phần | Có gì | Dùng cho harness |
|---|---|---|
| `research/proposals/harness-flow.html` | 12 bước, 6 lớp, taxonomy lỗi (`INPUT.*`, `GUARD.*`, `PARSE.*`, `RETRIEVAL.*`, `SOLVER.*`, `VALIDATE.*`, `EXPLAIN.*`, `HITL.*`, `SYSTEM.*`), 5 kịch bản (chuẩn, tiêm prompt, vô nghiệm, bịa trích dẫn, rủi ro cao). Ngân sách mỗi run: ≤4 lần gọi LLM, ≤6.000 token, ≤15 giây; solver time limit 10 giây. Số liệu trong trang là minh họa, **chưa phải đo thực**. | Đặc tả hành vi; kịch bản thành golden set; budget thành cấu hình |
| `mvp/` | Planner JS tham lam (`planner.js`), `validate()` thuần, `bscs.json` (65 môn, 24 tiên quyết, 17 khối), test `planner.test.js` (sweep 1.920 tổ hợp), UI tĩnh `file://` | Dữ liệu BSCS đã chuẩn hóa; bộ bất biến INV-1..11 làm spec cho validator Python |
| `mvp-demo/` | ~3.400 dòng JS UMD: `solver.js` (B&B + greedy dự phòng), `planner.js` (`validate` độc lập solver), `academic.js` (GPA/standing), `coverage.js`, `catalog.js` (áp thay đổi khung, `catalogImpact`), `record-source.js` (`MockStudentRecordSource`, hợp đồng SRS-01..09), `tools.js` + `docs/tool-schema.json` (19 tool: 4 nhóm student/advisor/…; envelope `{ok,data,labels,citations,warnings,error}`; 8 mã lỗi), 7 tài khoản giả (`accounts.json`, nhãn `is_simulated`), `announcements.json` (thông báo giả lập), `catalog-versions.json`, `rules.json`, bộ test Node + oracle | Hợp đồng adapter SIS, hợp đồng tool, seed dữ liệu giả, kịch bản STR-A..J |
| `data/processed/` | 10.089 môn, 386 ngành, 12.865 token tiên quyết, embedding jsonl, graph CSV; BSCS VinUni thô có **0 dòng tiên quyết/học kỳ** (BA đã tính, `ba-llm-chat-and-scale.md`), cần khóa tay | Nguồn RAG; không dùng thẳng làm ground truth |
| Quyết định BA (`ba-demo-school-decision.md`) | Khuyến nghị demo chính **VinUni BSCS**, DUT làm trường thứ hai; **nhưng** `requirements-addendum-sv-portal.md` nói một thành viên đang dựng cổng giả lập theo **DUT** → **hai tài liệu mâu thuẫn**, cần chốt (D1, mục 8.4) | |

Điều **chưa có**: backend thật (mọi thứ chạy `file://`, state ở `localStorage`), CP-SAT, pgvector, LLM, SSO, RLS, CI. Toàn bộ phần dưới là thiết kế cho các mảnh này.

---

## 1. Kiến trúc đóng gói và tích hợp

### 1.1 Khuyến nghị

**Harness là dịch vụ độc lập (microservice), không phải thư viện.** Lõi quyết định (solver, validator, rules) vẫn là **thư viện Python thuần** bên trong dịch vụ, có test riêng, để chạy được cả trong worker, CI và notebook. Ranh giới triển khai là HTTP + OpenAPI.

Lý do [I]:
- Mỗi trường có stack khác nhau (hiện biết DUT dùng các site `sv/dk1–dk4.dut.udn.vn`, S046/S050; VinUni dùng `sis.vinuni.edu.vn`, S024). Thư viện Python buộc trường phải chạy Python.
- LangGraph, OR-Tools, model embedding là phụ thuộc nặng, cần nâng cấp độc lập với cổng.
- Ranh giới dịch vụ là chỗ duy nhất để đặt xác thực, rate limit, audit và cách ly dữ liệu.

Phương án thay thế: **thư viện/SDK nhúng** (nhanh hơn cho demo một repo, nhưng chặn multi-school); **sidecar cùng pod với cổng** (hợp khi trường chạy K8s và muốn dữ liệu không rời mạng nội bộ: đây là biến thể triển khai của cùng dịch vụ, không phải kiến trúc khác).

### 1.2 So sánh cách nhúng vào web SV

| Cách | Cách hoạt động | Ưu | Nhược | Hợp khi |
|---|---|---|---|---|
| **Web Component (custom element) + BFF/reverse proxy cùng origin** *(khuyến nghị)* | Cổng thêm 1 thẻ `<pathplanner-widget>` + 1 đường dẫn `/pathplanner-api/*` proxy sang harness; proxy gắn JWT sau khi xác thực phiên cổng | Không phụ thuộc framework của cổng (Next, PHP, ASP.NET đều nhúng được); không CORS; token không lộ ra JS; Shadow DOM cách ly CSS | Cổng phải thêm 1 thẻ script và 1 rule proxy; mỗi trường cần ít nhất 1 lần sửa nhỏ | Mặc định cho cả đồ án lẫn multi-school |
| **iframe** | Cổng nhúng trang `pp.<trường>.edu.vn/embed` | Cách ly mạnh nhất; không cần sửa code cổng ngoài 1 thẻ iframe | Cần phiên riêng (SSO lại hoặc token qua URL/postMessage); đồng bộ chiều cao/giao diện khó; phải đặt CSP `frame-ancestors` bằng **HTTP header** (không dùng được qua meta, không fallback về `default-src`; `X-Frame-Options: ALLOW-FROM` không còn được hỗ trợ) [D-s S072]; mọi `postMessage` phải kiểm `event.origin` và không dùng `*` (hướng dẫn thứ cấp, S072) | Cổng không cho thêm script (chỉ cho nhúng link) |
| **REST/GraphQL API + SDK** | Trường tự viết giao diện, gọi API qua SDK | Linh hoạt nhất; không phụ thuộc UI của mình | Mỗi trường phải xây UI lại; tốn công nhất | Trường có đội dev riêng (pilot sâu) |
| **Reverse proxy thuần** (cổng chuyển tiếp `/pathplanner/*` tới app Next.js của mình) | Người dùng thấy cùng domain, trang do harness phục vụ | Nhanh nhất để demo | SSO/session phải dùng chung cookie domain; khó nhúng vào giữa trang cổng | Đồ án nếu muốn demo nhanh bằng 1 domain |
| **LTI 1.3 launch** | LMS gọi công cụ qua OIDC third-party-initiated login [D-s S069] | Chuẩn cho công cụ nhúng vào LMS | Dành cho LMS (Moodle/Canvas…), **không tìm thấy bằng chứng** cổng SV Việt Nam hỗ trợ LTI | Chỉ khi trường muốn đưa vào LMS, không phải SIS |

**Phương án đồ án:** Web Component + BFF trong chính app Next.js của web mô phỏng (BFF là route handler Next.js gọi harness bằng service token). Nếu ngại làm custom element, dùng **component React** trong giai đoạn đầu rồi bọc thành custom element khi sang multi-school; hợp đồng API không đổi.
**Phương án multi-school:** Web Component phát hành qua CDN/npm, cấu hình bằng thuộc tính (`tenant`, `api-base`, `locale`, `theme-tokens`), cộng một **"integration kit"** gồm: mẫu cấu hình nginx/IIS cho proxy, hướng dẫn CSP, bộ test hợp đồng cho adapter. iframe là chế độ thay thế khi cổng không cho chèn script.

### 1.3 Hợp đồng API (OpenAPI) và phiên bản

Nguyên tắc [P]:
- Tiền tố `/v1`; thay đổi **cộng thêm** (field mới tùy chọn) không đổi số phiên bản; thay đổi phá vỡ → `/v2`, chạy song song ≥ 1 học kỳ.
- Mỗi payload plan mang `schema_version`, `catalog_version`, `rules_version`, `solver_version`, `prompt_version` (đã có trong bước 11 của harness-flow).
- `Idempotency-Key` cho mọi POST tạo run (tránh trùng khi SV bấm hai lần lúc đăng ký đông).
- Lỗi theo dạng **problem+json** với `code` lấy đúng taxonomy của harness-flow (`SOLVER.infeasible_prereq_chain`…) [I; chuẩn problem+json chưa tra nguồn trong phiên này].
- Tool schema của LLM (`tool-schema.json`) **không** là API công khai: nó là hợp đồng nội bộ giữa LLM và tool, và không có tham số định danh.

Skeleton rút gọn (minh họa, không phải bản cuối):

```yaml
openapi: 3.1.0
info: { title: PathPlanner Harness API, version: 1.0.0 }
servers: [ { url: /pathplanner-api/v1 } ]   # qua BFF cùng origin
security: [ { bearerJWT: [] } ]             # JWT do BFF cấp, TTL <= 5 phút
paths:
  /runs:                                    # tạo run lập/đổi lộ trình
    post:
      parameters: [ { name: Idempotency-Key, in: header, required: true, schema: { type: string } } ]
      requestBody:                          # KHÔNG có student_id/tenant_id: lấy từ JWT
        content: { application/json: { schema: { $ref: '#/components/schemas/RunRequest' } } }
      responses:
        '202': { description: Đã nhận; trả run_id, links.events }
        '422': { $ref: '#/components/responses/Problem' }   # INPUT.*, GUARD.*
        '429': { $ref: '#/components/responses/Problem' }   # SYSTEM.rate_limited
  /runs/{run_id}:        { get: { summary: Trạng thái + kết quả cuối } }
  /runs/{run_id}/events: { get: { summary: SSE tiến độ bước 1..12 (text/event-stream) } }
  /plans/{plan_id}:      { get: { summary: Plan versioned (plan_vN, trạng thái draft|approved) } }
  /advisor/queue:        { get: { summary: Hàng đợi duyệt (role=advisor) } }
  /advisor/plans/{plan_id}/decision: { post: { summary: approve | edit | reject } }
  /catalog/change-candidates: { post: { summary: Cổng ingest thông báo (role=system), chỉ tạo ứng viên } }
  /healthz: { get: { security: [] } }
```

### 1.4 Streaming

**SSE** cho tiến độ và token giải thích; **không cần WebSocket** vì luồng chỉ một chiều server→client (tài liệu thứ cấp, S-không đăng ký riêng: các bài so sánh SSE/WebSocket đều là blog [M]). Lưu ý [I, chưa kiểm chứng bằng tài liệu MDN trong phiên này]: `EventSource` gốc của trình duyệt không đặt được header `Authorization`, nên dùng cookie qua BFF hoặc `fetch` + ReadableStream; proxy (nginx) phải tắt buffering cho `text/event-stream`.
Mô hình **202 + run_id + SSE**: tạo run trả ngay, widget mở SSE; nếu mất kết nối thì `GET /runs/{id}` lấy trạng thái cuối (bền nhờ checkpointer, S052). Việc chờ cố vấn duyệt (HITL, SLA 48 giờ trong harness-flow) **không** giữ kết nối: SV nhận trạng thái `draft/awaiting_advisor`.

---

## 2. Tích hợp dữ liệu SV và danh tính

### 2.1 SSO và cách harness nhận danh tính

Luồng khuyến nghị [I, cấu trúc; chuẩn: S070, S071]:

```
SV --OIDC Authorization Code (+PKCE)--> IdP của trường --> Cổng SV (phiên)
Cổng SV (BFF) --(phiên đã xác thực)--> cấp JWT ngắn hạn cho harness
Widget --(cookie phiên, cùng origin)--> BFF --(Bearer JWT)--> Harness
Harness: kiểm chữ ký bằng JWKS của tenant -> dựng RequestContext từ claim
```

- **Cổng làm SSO, harness không làm SSO.** OIDC là lớp danh tính trên OAuth 2.0, dùng Authorization Code flow và ID token [D-s S070]. Hướng dẫn hiện hành (bài thứ ba nhắc RFC 9700) là Authorization Code + PKCE, bỏ implicit [M, chưa đối chiếu RFC]. SAML: không nghiên cứu trong phiên này; nếu IdP trường chỉ có SAML thì tầng cổng/BFF chuyển đổi, harness vẫn nhận JWT.
- **Claim bắt buộc trong JWT harness:** `iss` (tenant), `sub` = **pseudonym của SV** (không phải MSSV), `role` ∈ {student, advisor, admin, system}, `scope`, `exp` ≤ 5 phút, `jti`. Với cố vấn xem SV: thêm `act`/`may_act` hoặc claim `advisee_ids` (token exchange có khái niệm delegation với claim `act`, S071) [I].
- **Không tin tham số do client/LLM gửi:** (1) `RequestContext` dựng **một lần** ở middleware từ JWT đã kiểm, bất biến; (2) mọi tool của LLM nhận context từ server, tool schema **không có** `student_id`/`tenant_id` (đã đúng ở `get_student_summary`, input rỗng); (3) tool ghi (`approve_plan`, `override_dismissal_stop`) kiểm `role` ở server, trả `ROLE_FORBIDDEN` (mã lỗi đã có trong envelope của mvp-demo); (4) lớp DB tự áp RLS theo `app.tenant_id`/`app.student_id` do server đặt (mục 3.3), nên dù code lỗi vẫn không đọc chéo.
- OWASP nêu cùng nguyên tắc: xử lý chức năng đặc quyền **trong code với token của ứng dụng, không đưa cho model**, và coi model như người dùng không tin cậy [D S061].

Phương án thay thế: harness tự verify ID token OIDC của trường (bỏ BFF) → đơn giản hơn nhưng widget phải giữ token trong trình duyệt và harness phải biết từng IdP; **không khuyến nghị** cho multi-school. API key theo tenant cho máy-với-máy (sync catalog, webhook) là hợp lý, kèm HMAC chữ ký thân request.

### 2.2 Adapter theo trường và canonical data model

**Canonical model (tối thiểu)**, đối chiếu với `mvp-demo` (`StudentRecord`, `TermRecord`, `Rules`) và `data/processed`:

| Thực thể | Trường chính | Ghi chú |
|---|---|---|
| `Tenant` | `tenant_id`, `locale`, `grading_scale`, `rules_ref` | Quy chế **không hard-code**: nạp `rules.<trường>.json` (quyết định đã nêu ở addendum §1) |
| `StudentRef` | `pseudonym`, `program_id`, `cohort`, `advisor_pseudonym` | Bảng ánh xạ pseudonym↔MSSV nằm riêng, quyền hẹp (mục 3.1) |
| `Program` / `CatalogVersion` | `catalog_version_id`, khung bắt buộc/tự chọn, requirement groups | `data/README` ghi còn thiếu bảng requirement groups |
| `CourseResult` | `course_code`, `term`, `credits`, `grade_letter`, `grade_point`, `status` (passed/failed/withdrawn/in_progress) | Điểm số chỉ dùng trong solver/validator, **không vào prompt** |
| `ConductRecord` (kết quả rèn luyện) | `term`, `score`, `label` | Thang điểm/xếp loại để cấu hình theo trường; **không tìm thấy bằng chứng** trong phiên này về thang chuẩn quốc gia → không giả định |
| `Announcement` | `source`, `url`, `published_at`, `body_hash`, `body` | Luôn gắn `trust=untrusted` (mục 3.5) |
| `AcademicStatus` | GPA kỳ/tích lũy, standing, môn nợ | Tính bằng hàm thuần như `computeAcademicStatus` |

Hợp đồng adapter (Python `Protocol`; mục tiêu: cùng bộ test hợp đồng chạy trên mọi adapter, như TST-SRS-03 của mvp-demo):

```python
class SISAdapter(Protocol):
    def get_student(self, ctx) -> StudentRef: ...
    def get_results(self, ctx) -> list[CourseResult]: ...        # transcript
    def get_conduct(self, ctx) -> list[ConductRecord]: ...
    def list_announcements(self, since) -> list[Announcement]: ...
    def get_catalog(self, program_id, version=None) -> CatalogBundle: ...
    def capabilities(self) -> set[str]                           # adapter nào thiếu gì, khai rõ
```

`MockStudentRecordSource` (SRS-01..09) chính là adapter số 0. Không có bằng chứng SIS nào của trường VN công khai API: DUT cần đăng nhập, không truy cập được (S050), VinUni có cổng riêng (S024). Nên có **ba mức adapter**, theo độ khó tăng dần [I]:

1. **API/endpoint do trường cung cấp** (tốt nhất; trường chịu trách nhiệm quyền).
2. **View/bảng đọc-chỉ trong DB hoặc file export định kỳ (CSV/SFTP)** do phòng CNTT trường tạo.
3. **SV tự tải bảng điểm/đồng ý nhập tay** (dự phòng; chấp nhận độ tươi thấp). **Không** scrape trang SV bằng tài khoản SV: vi phạm điều khoản thường gặp và dễ vỡ [I].

`OneRoster 1.2` (gradebook/rostering qua REST + OAuth2 client credentials) [D-s S068] và LTI [D-s S069] chỉ là **tham chiếu mô hình**. **Không tìm thấy bằng chứng** rằng SIS trường Việt Nam dùng các chuẩn này; đừng hứa tương thích.

### 2.3 Đồng bộ hay truy vấn trực tiếp

| Dữ liệu | Cách lấy | Lý do |
|---|---|---|
| Khung đào tạo, quy chế, tiên quyết (catalog) | **Đồng bộ + version** (`catalog_version`), build thành bảng + embedding | Ít đổi, phải tái hiện được từng plan; RAG cần index sẵn |
| Hồ sơ SV (điểm, rèn luyện) | **Truy vấn trực tiếp khi bắt đầu run, chụp snapshot** (đã pseudonymize, lưu `record_hash` + bản tối thiểu) | Luôn tươi; không nhân bản bảng điểm vào DB của harness; vẫn tái hiện được |
| Thông báo | **Kéo định kỳ/nhận webhook** vào hàng đợi ứng viên | Mục 2.5 |
| Tổng hợp dashboard cố vấn | Bảng tổng hợp (không chứa điểm từng môn) cập nhật theo sự kiện | Giảm lượng dữ liệu nhạy cảm nằm lại |

Đánh đổi: truy vấn trực tiếp phụ thuộc SLA của SIS (SIS lúc đăng ký môn thường quá tải [I]) → cần cache ngắn (TTL 5–15 phút [P]) và chế độ "dùng snapshot gần nhất + cảnh báo độ tươi".

### 2.4 Nguồn cập nhật thay đổi đào tạo

Thứ tự ưu tiên kênh [I]: (1) **webhook/API từ trường** khi có; (2) **RSS/Atom/sitemap** của trang thông báo; (3) **polling có kiểm soát** trang công khai. Lưu ý từ `CLAUDE.md`: nhiều trang `vinuni.edu.vn` trả 403 với fetch tự động; đó là tín hiệu **không nên cố vượt chặn**. Với trang công khai: allowlist nguồn theo tenant, tôn trọng `robots.txt` và rate limit, lưu `body_hash` để phát hiện thay đổi, **không** scrape khu vực cần đăng nhập.

### 2.5 Pipeline cập nhật `catalog_version` + replan

```
(1) Thu thập --> (2) Chuẩn hóa/hash/diff --> (3) Trích xuất "ứng viên thay đổi" --> (4) Người duyệt
        --> (5) Phát hành catalog_version mới --> (6) Impact analysis --> (7) Replan hàng loạt --> (8) Thông báo SV + CV
```

- (3) dùng bước trích xuất **không có tool, không có quyền ghi**, đầu ra bắt buộc đúng schema (loại thay đổi, mã môn, hiệu lực) và **bị đối chiếu với catalog hiện hành** bằng code; nội dung thông báo là dữ liệu không tin cậy (OWASP: tách và gắn nhãn nội dung ngoài; kiểm định đầu ra bằng code; người duyệt cho hành động rủi ro cao [D S061]).
- (4) **Không tự deploy thay đổi** (nguyên tắc harness, tối đa L1–L2 tự động): cán bộ đào tạo/quản trị xác nhận. Đây cũng là chỗ chặn thông báo giả mạo.
- (5) Tạo `catalog_version` bất biến; áp lên bản gốc như `PPCatalog.applyChanges` (INH-06) đã làm.
- (6) `catalogImpact` (đã có ở `mvp-demo/js/planner.js`) xác định SV nào bị ảnh hưởng, ưu tiên theo "kỳ sắp đăng ký".
- (7) Job hàng loạt trên hàng đợi (mục 4, hàng queue), **chỉ chạy solver + validator**, không gọi LLM; giải thích sinh khi SV mở plan hoặc theo Batch API (giảm 50%, S032). Plan cũ giữ nguyên (không ghi đè), plan mới là `plan_vN+1` ở trạng thái `proposed` cho đến khi SV/cố vấn chấp nhận.
- Quy định áp dụng thay đổi cho SV đang học (RUL-27): mvp-demo ghi **"Không có căn cứ (CẦN XÁC MINH)"** → harness phải cho phép cấu hình `applies_to_cohorts` thay vì giả định.

---

## 3. Bảo mật và riêng tư dữ liệu SV

### 3.1 Pseudonymization và tối thiểu hóa

- `student_pseudonym = HMAC-SHA256(key_tenant, MSSV)` (rút gọn, có tiền tố `stu_`). Khóa theo tenant nằm trong KMS/secret store; bảng ánh xạ ngược (nếu cần cho cố vấn) nằm ở **schema riêng, role riêng**, không join được từ role của dịch vụ plan [I].
- **Không đưa vào prompt:** họ tên, MSSV, email, số điện thoại, ảnh, điểm số cụ thể, điểm rèn luyện. Chỉ đưa: mã môn, trạng thái (đã đạt/nợ), kỳ, số tín chỉ, chunk catalog. Giải thích "vì cần Xác suất–Thống kê hoàn thành ở kỳ 3" không cần biết điểm.
- Giữ PII **ngoài state của LangGraph**: state chỉ chứa id/hash, vì checkpoint được lưu bền và tích lũy theo thời gian; trang persistence đã đọc **không nói** về mã hóa checkpoint [D S052]. Muốn mã hóa mức serializer phải kiểm tra thêm (**Không tìm thấy bằng chứng** trong phiên này).

### 3.2 Phân quyền: RBAC + ABAC

| Vai | Quyền | Điều kiện ABAC |
|---|---|---|
| student | Đọc/ghi plan **của mình**; đổi mục tiêu; gửi duyệt | `plan.student_pseudonym == ctx.sub` |
| advisor | Xem plan/tiến độ SV **được phân công**; approve/edit/reject | `student ∈ advisees(ctx.sub)`; mọi truy cập ghi audit |
| admin (đào tạo/IT) | Cấu hình rules, duyệt thay đổi catalog; **không** xem điểm cá nhân mặc định | Break-glass có lý do + audit |
| system | Ingest thông báo, chạy job | Không có quyền đọc hồ sơ SV |

### 3.3 Row-level security (Postgres)

- Bật `ENABLE ROW LEVEL SECURITY` trên mọi bảng có dữ liệu SV; policy permissive gộp OR, restrictive gộp AND; bật RLS không policy = từ chối mọi dòng [D-s S067].
- Thiết kế [I]: server đặt `SET LOCAL app.tenant_id`, `app.role`, `app.student_id` **trong từng transaction** (với connection pool phải dùng `SET LOCAL`/giao dịch, không `SET` cấp phiên); policy so cột `tenant_id`/`student_pseudonym` với `current_setting(...)`. Dịch vụ chạy bằng role **không phải owner** của bảng (chủ bảng mặc định bỏ qua RLS, cần `FORCE ROW LEVEL SECURITY`: điểm này mình biết từ tài liệu PostgreSQL nhưng **chưa xác nhận lại ở trang đọc trong phiên này**, hãy kiểm khi triển khai).
- Test bắt buộc trong CI: bộ test "đọc chéo" (student A không đọc được B; tenant X không đọc được tenant Y) chạy bằng role ứng dụng thật.

### 3.4 Mã hóa, log, retention, audit, secret

| Hạng mục | Đồ án/demo | Production |
|---|---|---|
| Truyền | TLS tại gateway (Caddy/nginx) | TLS 1.2+ mọi hop, mTLS giữa dịch vụ nếu cluster dùng chung |
| Lưu | Volume Postgres thường; dữ liệu giả | Mã hóa đĩa/volume + mã hóa cột cho bảng ánh xạ pseudonym; sao lưu mã hóa |
| Log | JSON log qua `structlog`/bộ lọc; **cấm** log body request/prompt thô ở mức INFO | Redaction có bộ regex (MSSV theo mẫu của trường, email, SĐT VN, số định danh) + **allowlist field**, không blacklist |
| Retention [P] | Trace/prompt thô ≤ 30 ngày; checkpoint LangGraph xóa theo job định kỳ (trang persistence đề xuất đúng việc này, S052); plan versions giữ đến khi SV tốt nghiệp + thời hạn do trường định | Thời hạn pháp định: **Không tìm thấy bằng chứng** trong phiên này; hỏi pháp chế |
| Audit trail | Bảng `audit_log` append-only (ai, vai, hành động, đối tượng, `run_id`, thời điểm) | Chuyển sang kho bất biến (WORM/object lock) hoặc SIEM; mọi truy cập của cố vấn/admin phải có dòng |
| Secret | `.env` không commit; Docker secrets; LiteLLM virtual keys để **app không giữ khóa nhà cung cấp** (virtual keys cần DB; S054, nguồn thứ ba) | Vault/KMS/Secret Manager của hạ tầng trường; xoay khóa; khóa theo tenant; quét secret trong CI |

Lưu ý: Langfuse bản MIT **không có** project-level RBAC, retention policy và audit log (đó là phần `ee/` cần license key) [D-s S063]. Nếu cần những tính năng này ở production → tính phí/giấy phép hoặc tự làm ở lớp mình.

### 3.5 Chống prompt injection từ nội dung không tin cậy

Bề mặt tấn công: (a) ô mục tiêu của SV (direct), (b) **thông báo khoa/trường** (indirect), (c) nội dung catalog/PDF nạp vào RAG. OWASP LLM01 liệt kê 7 biện pháp (ràng buộc vai trò; kiểm định định dạng đầu ra bằng code; lọc vào/ra; least privilege; người duyệt cho hành động rủi ro; tách và gắn nhãn nội dung không tin cậy; red-team định kỳ) [D S061]. Áp vào harness:

1. **Kiến trúc là biện pháp chính:** LLM không có tool ghi, không xếp lịch; kết quả hợp lệ do solver + validator quyết định (cũng là tinh thần LLM-Modulo, S040). Injection thành công nhất cũng chỉ làm sai **lời giải thích**, mà lời giải thích bị out-guard kiểm (trích dẫn tồn tại, số khớp plan).
2. **Thông báo không bao giờ vào prompt giải thích thô.** Chỉ đi qua bước trích xuất có schema (mục 2.5), tách vùng dữ liệu bằng thẻ rõ ràng, đầu ra đối chiếu catalog bằng code, rồi **người duyệt**.
3. **Classifier + luật** cho input (đã có ở bước 2) và kịch bản "tiêm prompt" trong golden set; thêm **canary** (chuỗi bí mật trong system prompt, cảnh báo nếu xuất hiện trong output).
4. **Red-team định kỳ** bằng Promptfoo (có chế độ red-team tách khỏi eval, S066).

### 3.6 LLM chạy ở đâu và rủi ro gửi dữ liệu ra ngoài

| Phương án | Ưu | Nhược/rủi ro | Bằng chứng |
|---|---|---|---|
| **API ngoài (Anthropic)** | Chất lượng, không phải vận hành GPU | Không thấy vùng Việt Nam (`inference_geo` chỉ `us`/`global`) [D S032]; dữ liệu rời VN → nghĩa vụ CTIA [S036, S077]; ZDR là thỏa thuận riêng qua sales [D S076]; một số dòng model có yêu cầu giữ 30 ngày [D S076]. **Chưa xác nhận** chính sách áp cho đúng model dự kiến dùng | |
| **Nhà cung cấp ngoài khác (OpenAI, Google…)** | Tương tự | **Không tìm thấy bằng chứng** (chưa tra điều khoản từng nhà) | |
| **Self-host open-weight (on-prem/cloud trong nước)** | Dữ liệu không rời trường; đã có nghiên cứu triển khai cục bộ cho advising (S043, S044) | Chất lượng tiếng Việt chưa biết; tốn GPU và vận hành; **Không tìm thấy bằng chứng** trong phiên này về model open-weight cụ thể đạt chuẩn tiếng Việt cho nhiệm vụ này | |

Khuyến nghị [I]: **thiết kế sẵn khả năng đổi model** (LiteLLM, mục 4) và chạy **hai tầng** như BA đã đề xuất: demo/đồ án dùng dữ liệu tổng hợp qua API ngoài; dữ liệu thật chỉ sau khi pháp chế duyệt, kèm phương án dự phòng self-host. Vì prompt đã tối thiểu hóa (không PII, không điểm), rủi ro của API ngoài giảm đáng kể nhưng **không bằng 0**: mã môn + trạng thái hoàn thành vẫn là dữ liệu học tập gắn với một người nếu ghép được danh tính.

### 3.7 Khung pháp lý Việt Nam (chỉ nêu điều có nguồn)

Mọi mục dưới đây là **nguồn thứ cấp (B)**, chưa đối chiếu văn bản gốc; cần pháp chế/luật sư xác nhận.

- Luật Bảo vệ dữ liệu cá nhân 2025, số 91/2025/QH15, thông qua 26/6/2025, hiệu lực 1/1/2026 [S035, snippet].
- Nghị định 356/2025/NĐ-CP (31/12/2025) hướng dẫn luật; một số nguồn nói thay thế NĐ 13/2023 [S036, S078].
- Theo bản tóm tắt EY [S077, đã đọc, không có số Điều]: hồ sơ **đánh giá tác động chuyển dữ liệu ra nước ngoài (CTIA, Mẫu 09)** và **DPIA (Mẫu 10)**, A05 (Bộ Công an) xem xét trong 15 ngày; cập nhật 6 tháng/lần; bên xử lý phải xóa dữ liệu khi hết hợp đồng; thông báo chủ thể trong 72 giờ khi vi phạm; khái niệm dữ liệu nhạy cảm được mở rộng.
- Luật Trí tuệ nhân tạo 134/2025/QH15 (hiệu lực 1/3/2026) [S037, snippet]: **chưa kiểm tra** phân loại rủi ro/nghĩa vụ cho AI giáo dục.
- VinUni có Personal Data Protection Policy [S038] nhưng **chưa đọc được nội dung**; VinUni Student GenAI Guidelines không điều chỉnh việc nhà trường gửi dữ liệu SV cho nhà cung cấp AI [S039].
- **Không tìm thấy bằng chứng** về: (a) điểm số/bảng điểm SV có thuộc "dữ liệu nhạy cảm" hay không; (b) quy định riêng cho dữ liệu của người dưới 18 tuổi trong bối cảnh SV năm nhất; (c) thời hạn lưu trữ bắt buộc đối với hồ sơ học tập khi dùng AI; (d) việc sử dụng cloud trong nước có được coi là "chuyển ra nước ngoài" hay không. Cả bốn cần hỏi pháp chế.

---

## 4. Lựa chọn công nghệ cho từng lớp harness

Tên lớp theo harness-flow: L1 Input & Context, L2 Execution & Orchestration, L3 Guardrails & Control, L4 Observability & Error, L5 Evaluation, L6 Continuous Improvement.

| Lớp | Thành phần | Đề xuất | Lý do | Thay thế / đánh đổi |
|---|---|---|---|---|
| L2 | Orchestration | **LangGraph** + `PostgresSaver`/`AsyncPostgresSaver`; HITL bằng `interrupt()` + `Command(resume=...)` với cùng `thread_id` | Có checkpointer = durable execution; dùng được HITL, replay, fault tolerance; PostgresSaver là lựa chọn production được tài liệu nêu [D S052, D-s S053]. Gọi LLM bọc `@task` để kết quả không tất định được lưu và không gọi lại khi resume [D-s S053] | Tự viết state machine bằng Python thuần (ít phụ thuộc; mất replay/HITL có sẵn). Giữ **đồ thị mỏng**: 12 bước phần lớn là hàm thuần, chỉ bước LLM/HITL cần LangGraph [I] |
| L2 | LLM gateway/router | **LiteLLM proxy**: virtual keys, spend tracking, budgets, routing, fallbacks [D-s S054] | Một điểm đặt ngân sách token (khớp Budget Manager), fallback giữa model, khóa nhà cung cấp không nằm trong app | Gọi SDK nhà cung cấp trực tiếp (bớt 1 service). Lưu ý tính năng riêng nhà cung cấp (vd Citations, S034) **không** chắc đi qua lớp trừu tượng [I] |
| L2 | Structured output | Tool use `strict: true` / JSON schema + **Pydantic validate phía server** | `strict` bảo đảm đầu vào tool khớp schema, nhưng model vẫn có thể tự suy ra tham số thiếu → phải kiểm phía server [D S033]. Citations API **không dùng cùng structured outputs (400)** [D S034] | Với bước giải thích (văn bản), dùng thẻ `[chunk_id]` tự quản + out-guard như harness-flow thay vì Citations API; hai cách loại trừ nhau nếu muốn JSON |
| L2 | Solver | **OR-Tools CP-SAT**, chạy trong **tiến trình riêng** (process pool/worker) với `max_time_in_seconds` và **hard kill** ngoài tiến trình | `max_time_in_seconds` là tham số chuẩn [D-s S055]; có báo cáo giai thoại là giới hạn thời gian bị vượt khi nhiều worker [M S055] → không tin giới hạn mềm một mình. Đặt `num_workers` nhỏ (1–2) để chạy được nhiều solve song song | Giữ B&B JS của mvp-demo làm **oracle test** và đường dự phòng; MILP/CBC (không nghiên cứu). Mô hình hóa: biến bool (môn, kỳ), tiên quyết/đồng thời, trần/sàn tín chỉ, hè, hạn tốt nghiệp; trả unsat core để giải thích |
| L1 | Vector/RAG | **Postgres + pgvector**; HNSW (từ pgvector 0.5.0; `hnsw.ef_search` mặc định 40); **hybrid** = full-text/BM25 + vector gộp bằng **RRF** hoặc cross-encoder [D-s S056] | Một DB cho mọi thứ (đỡ vận hành); lọc theo metadata (`catalog_version`, `program_id`) bằng SQL. Quy mô: ~10k môn + 386 ngành [data/README] rất nhỏ; có thể **không cần index ANN** [I] | Qdrant/Weaviate (thêm service, không cần ở quy mô này). Full-text tiếng Việt trong Postgres: **chưa kiểm chứng** cấu hình/tách từ; cần thử `simple` + `unaccent` hoặc tách từ trước khi index |
| L1 | Embedding tiếng Việt | **BAAI/bge-m3** (MIT, 1024 chiều, 8192 token, dense+sparse+multi-vector) làm baseline [D S057] | Một model cho dense và sparse; đa ngôn ngữ. **Trang model không nêu riêng tiếng Việt** [D S057] → phải tự đo | Ứng viên để so trong VN-MTEB (41 dataset, 18 mô hình, có bge-m3, multilingual-e5, vietnamese-bi-encoder, Vietnamese_Embedding) [D-s S059]; chưa biết xếp hạng. **Làm mini-benchmark** trên ~100 truy vấn retrieval thật của đồ án (tên môn VI/EN, mô tả, tiên quyết) trước khi chốt |
| L1 | Reranker | **bge-reranker-v2-m3** (Apache-2.0, 0.6B, đa ngôn ngữ, dựa bge-m3) [D S058] | Cùng họ với embedder; model card khuyến nghị hybrid + rerank [D S057] | Bỏ reranker khi top-k nhỏ (10k môn): đo lợi ích trước. Chạy CPU được nhưng chậm hơn [I] |
| L3 | Guardrails: injection | Classifier + luật + canary; kiến trúc "LLM không có quyền" (mục 3.5) | OWASP [D S061] | LLM-based guard (thêm chi phí/độ trễ, thêm bề mặt tấn công) |
| L3 | PII | **Regex + allowlist field + tối thiểu hóa**; Presidio chỉ làm khung registry | Presidio mặc định chỉ có English; thêm ngôn ngữ cần NLP engine và recognizer riêng, mỗi recognizer 1 ngôn ngữ, **tiếng Việt không được liệt kê** [D S060]. Regex (MSSV, email, SĐT) không phụ thuộc ngôn ngữ [D S060] | Tự huấn luyện/ghép NER tiếng Việt: **Không tìm thấy bằng chứng** trong phiên này về công cụ cụ thể đáng tin; bỏ qua ở demo |
| L4 | Tracing/LLM observability | **Mức đồ án:** JSON log có `run_id/trace_id` + bảng `run_spans` trong Postgres + OTel SDK. **Mức pilot:** **Langfuse tự host** | Langfuse: lõi MIT, tracing/eval/prompt mgmt/datasets không giới hạn [M/D-s S063]; nhưng compose chính thức **không HA/scale/backup** [D-s S062] và nguồn thứ ba nói stack gồm Postgres, Redis, ClickHouse, MinIO (≥4 GB RAM, chưa kiểm chứng) | **Phoenix**: dựa OTel/OpenInference, tự host dễ [D-s S064] nhưng giấy phép **các nguồn mâu thuẫn** (ELv2?) → kiểm repo. **LangSmith**: **Không tìm thấy bằng chứng** (chưa tra điều khoản self-host/dữ liệu). **OTel GenAI semconv** hiện ở trạng thái Development (chưa stable): tên thuộc tính có thể đổi [D-s S065], nên bọc bằng lớp mỏng của mình |
| L4 | Metrics/alert/lỗi | Prometheus + Grafana (latency, cost, retry, mã lỗi theo taxonomy, hàng đợi), Sentry (lỗi ứng dụng) | Khớp bước 11 của harness-flow | Chỉ dùng log + Grafana Loki ở demo. **Sentry/Prometheus**: không tra nguồn riêng trong phiên này (công cụ phổ biến, không có claim số liệu) |
| L5 | Evaluation | **pytest** cho phần xác định (tỷ lệ plan hợp lệ, so solver↔validator↔oracle JS), **Promptfoo** cho bước LLM và red-team trong CI [D-s S066]; golden set ~140 ca (BA); LLM-as-Judge **lấy mẫu**, có hiệu chuẩn với người (thiên vị vị trí/độ dài/tự ưu ái, S042) | Promptfoo: CLI MIT, tách eval/red-team, có GitHub Action [D-s S066]. Cần biết: Promptfoo đã gia nhập OpenAI (3/2026), vẫn MIT [M S066] → rủi ro định hướng sản phẩm | **DeepEval, Ragas**: **Không tìm thấy bằng chứng** (chưa tra trong phiên này). Có thể tự viết harness chấm vì phần lớn chỉ số là xác định |
| L6 | Queue/async | **Redis + hàng đợi tiến trình** (Celery hoặc RQ) cho replan hàng loạt và job ingest | Công việc là **CPU-bound (solver)**, cần worker dạng tiến trình. **arq** là asyncio và README ghi **"maintenance only mode"** [D S074] → không chọn cho dự án mới | Hàng đợi trên Postgres (không thêm Redis; chưa tra nguồn). Chọn Celery vs RQ: **Không tìm thấy bằng chứng** chính thức trong phiên này (chỉ blog [M]); chọn theo kinh nghiệm nhóm. Redis vốn đã cần cho rate limit và LiteLLM |
| L1/L2 | Cache | Redis: (1) **plan cache** theo khóa `hash(goal chuẩn hóa, tập môn đã đạt, catalog_version, rules_version, solver_version)`; (2) cache hồ sơ SV TTL ngắn; (3) prompt caching phía nhà cung cấp | Trùng lặp cao khi nhiều SV cùng hồ sơ/mục tiêu [I]; giá cache read $0,10/MTok so với $2 input của Sonnet 5.5 [D S032] | Không cache giải thích riêng từng SV khi có PII; cache theo plan_hash |

Ghi chú về **vấn đề phiên bản:** mọi tên gói/phiên bản cụ thể (LangGraph, LiteLLM, OR-Tools, pgvector, Langfuse…) cần **ghim bản (pin) và ghi lại ngày** khi dựng; trong phiên này **không** xác minh số phiên bản hiện hành của các công cụ trên (chỉ xác minh khả năng), nên báo cáo này cố ý không nêu số phiên bản.

---

## 5. Đóng gói và triển khai

### 5.1 Docker

- **Multi-stage:** `builder` (cài phụ thuộc, wheel) → `runtime` (distroless/slim, user không root, `read_only` rootfs khi được). Hai image: `pp-api` (FastAPI + LangGraph) và `pp-worker` (cùng code, entrypoint worker, có OR-Tools). Image embedding/reranker tách riêng để cache lớp model.
- **Model/prompt version:** prompt là file có version trong repo (`prompts/<tên>/<semver>.md`), nạp qua `prompt_version`; mọi run lưu bộ ba (`prompt_version`, `model_id`, `catalog_version`) (đã có ở bước 11). Trọng số model đặt ở volume `models`, ghim hash/revision; không tải lúc khởi động ở production.
- **Cấu hình theo môi trường:** biến môi trường + file `tenants/<tenant>.yaml` (rules, adapter, giới hạn, nguồn thông báo); `Settings` Pydantic; mặc định an toàn (rate limit bật, log không PII).
- **Migration:** Alembic, chạy bằng job `migrate` trước khi `api` khởi động; `PostgresSaver.setup()` tạo bảng checkpoint (gọi một lần) [D S052].
- **Seed:** job `seed` nạp catalog (`data/processed` + bản khóa tay) và dữ liệu SV giả (mục 6.3).

### 5.2 docker-compose cho demo

| Service | Image/nguồn | Cổng (host) | Volume | Healthcheck |
|---|---|---|---|---|
| `gateway` | Caddy/nginx | 8080 | `./gateway` (conf) | `GET /healthz` qua upstream |
| `portal-web` | Next.js (web mô phỏng SV) | 3000 | – | `GET /api/health` |
| `sis-mock` | FastAPI (SIS giả) | 8100 | – | `GET /healthz` |
| `pp-api` | FastAPI + LangGraph | 8000 | `models` (ro) | `GET /healthz` (kiểm DB + Redis) |
| `pp-worker` | cùng code, worker queue | – | `models` (ro) | lệnh ping của queue |
| `postgres` | `pgvector/pgvector` | 5432 (chỉ nội bộ) | `pgdata` | `pg_isready` |
| `redis` | redis | 6379 (nội bộ) | `redisdata` | `redis-cli ping` |
| `litellm` | LiteLLM proxy | 4000 (nội bộ) | `./litellm.yaml` | `GET /health` |
| `embed` *(tùy chọn)* | bge-m3 + reranker phục vụ cục bộ | 8200 (nội bộ) | `models` | `GET /healthz` |
| `langfuse-*` *(profile `obs`)* | web, worker, Postgres, Redis, ClickHouse, MinIO | 3001 | nhiều volume | theo compose chính thức (S062) |
| `prometheus`, `grafana` *(profile `obs`)* | | 9090, 3002 | `promdata`, `grafdata` | HTTP 200 |

```yaml
# docker-compose.yml (minh họa, rút gọn)
x-common: &common { restart: unless-stopped, env_file: .env }
services:
  postgres:
    image: pgvector/pgvector:pg17          # ghim tag cụ thể khi dựng thật
    environment: { POSTGRES_PASSWORD_FILE: /run/secrets/pg_pass }
    secrets: [pg_pass]
    volumes: [pgdata:/var/lib/postgresql/data]
    healthcheck: { test: ["CMD-SHELL","pg_isready -U pp"], interval: 5s, retries: 10 }
  redis:
    image: redis:7
    healthcheck: { test: ["CMD","redis-cli","ping"], interval: 5s }
  pp-api:
    <<: *common
    build: { context: ., target: runtime, dockerfile: docker/api.Dockerfile }
    depends_on: { postgres: { condition: service_healthy }, redis: { condition: service_healthy } }
    environment: { PP_TENANT: demo-school, PP_LLM_BASE_URL: http://litellm:4000 }
    healthcheck: { test: ["CMD","curl","-f","http://localhost:8000/healthz"], interval: 10s }
  pp-worker:
    <<: *common
    build: { context: ., target: runtime, dockerfile: docker/worker.Dockerfile }
    command: ["python","-m","pp.worker"]
    deploy: { resources: { limits: { cpus: "4" } } }   # CP-SAT chiếm CPU
volumes: { pgdata: {}, redisdata: {} }
secrets: { pg_pass: { file: ./secrets/pg_pass.txt } }
```

Đồ án chạy ổn trên 1 máy 16 GB (không bật profile `obs`); với `obs` (ClickHouse) nên 32 GB [I, chưa đo].

### 5.3 Đường lên Kubernetes/Helm và multi-tenant

Kubernetes mô tả multi-tenancy theo "hard" và "soft"; khối xây dựng là namespace, RBAC, NetworkPolicy, ResourceQuota; blog thứ ba nhắc namespace **không đủ** cho tenant không tin cậy vì cùng chia sẻ node/kernel [D-s S073].

| Mô hình | Cách làm | Ưu | Nhược | Khuyến nghị |
|---|---|---|---|---|
| **Silo: mỗi trường một bản triển khai** (namespace hoặc cluster riêng) | Helm release/trường | Cách ly mạnh nhất; dễ đáp ứng yêu cầu "dữ liệu ở lại trường" (on-prem/VPC của trường); xóa trường = xóa release | Tốn tài nguyên; nâng cấp N lần | **Mặc định cho pilot và multi-school giai đoạn đầu** [I] |
| **Pool + schema-per-tenant** | 1 cluster, 1 Postgres, mỗi trường 1 schema | Cách ly logic tốt, xóa/xuất theo tenant dễ | Migration nhân N; số schema lớn khó quản | Khi > ~5–10 trường và cùng chấp nhận hạ tầng chung |
| **Pool + row-level (cột `tenant_id` + RLS)** | Mọi tenant chung bảng | Rẻ nhất, vận hành đơn giản | Một policy sai = lộ chéo tenant; khó xuất/xóa theo tenant | Chỉ khi nhiều tenant nhỏ, và **luôn kèm RLS** làm lớp thứ hai (mục 3.3) |

Helm tối thiểu: chart `pp` (api, worker, migrate job, cronjob ingest), phụ thuộc Postgres/Redis có thể trỏ ra dịch vụ managed; `values-<tenant>.yaml`; HPA theo độ dài hàng đợi cho worker; `NetworkPolicy` default-deny; `ResourceQuota`. IaC mức tối thiểu: Terraform/OpenTofu chỉ cho phần hạ tầng nền nếu có cloud; **đồ án không cần**.

### 5.4 CI/CD (GitHub Actions)

```
PR:    lint (ruff) -> type (mypy) -> unit/property tests -> bài test RLS "đọc chéo" (Postgres service)
       -> GOLDEN-SET GATE (phần xác định, không gọi LLM): 100% plan solver qua validator, 0 vi phạm bất biến
       -> contract test adapter (mock SIS) -> OpenAPI diff (chặn thay đổi phá vỡ)
PR có đổi prompt/model/rules: + Promptfoo eval (LLM thật, tập con) + red-team smoke
main:  build image (multi-stage) -> Trivy scan (image + config, fail HIGH/CRITICAL) -> SBOM -> push registry
       -> deploy staging (thủ công duyệt) ; production: KHÔNG tự deploy (nguyên tắc L1-L2)
Nightly: full eval có LLM + LLM-as-Judge lấy mẫu + báo cáo trôi chỉ số
```

- Trivy action: quét image/fs/config, xuất SARIF, `exit-code`/`severity`; **pin theo tag/SHA** [D-s S075]. Pin tất cả action theo SHA [P].
- Eval có LLM tốn tiền: ước tính ~US$2,5 mỗi lần chạy 140 ca (giả định mục 7.3); chạy đầy đủ theo đêm và khi đổi prompt/model, không mỗi commit.

### 5.5 "Đủ cho đồ án" và "production thật"

| Hạng mục | Đủ cho đồ án/demo | Production thật |
|---|---|---|
| Triển khai | docker-compose 1 máy | Helm/K8s, mỗi trường 1 release, HA Postgres, backup đã thử khôi phục |
| Dữ liệu | **Chỉ dữ liệu giả có nhãn "MÔ PHỎNG"** | Dữ liệu thật qua DPIA/CTIA (nếu cần), hợp đồng xử lý dữ liệu |
| Danh tính | JWT giả cấp bởi web mô phỏng (OIDC giả, ví dụ Keycloak/mock-IdP) | OIDC thật của trường |
| Bảo mật | RLS + RBAC + log sạch + quét secret | Thêm mã hóa cột, KMS, WORM audit, pentest, quy trình sự cố 72 giờ [S077] |
| Quan sát | JSON log + Prometheus/Grafana | Langfuse/Phoenix tự host có backup, cảnh báo, on-call |
| LLM | API ngoài + dữ liệu tổng hợp | Quyết định theo pháp chế: ZDR/self-host/cloud trong nước |
| Eval | Golden set 140 ca + gate xác định | Golden set mở rộng theo từng trường, theo dõi trôi chỉ số, red-team định kỳ |

---

## 6. Web mô phỏng cổng sinh viên

### 6.1 Kiến trúc tối thiểu

```
Browser
  └─ portal-web (Next.js, App Router)
       ├─ /login            (mock OIDC: chọn 1 trong 7+ tài khoản giả -> phiên)
       ├─ /ho-so, /bang-diem, /ren-luyen, /thong-bao   (trang cổng, đọc từ sis-mock)
       ├─ /api/pp/*         (BFF: gắn JWT -> proxy tới pp-api; chỉ route này nhìn thấy khóa ký)
       └─ <pathplanner-widget>  (Web Component, gọi /api/pp/*)
  └─ sis-mock (FastAPI) + Postgres schema `sis`
       bảng: student, program_enrollment, term, course_result, conduct_record, announcement, advisor_assignment
```

`sis-mock` **cố ý có API kiểu "SIS" khác với canonical model của harness** (tên field, thang điểm, mã kỳ khác) để buộc adapter làm việc thật; nếu chỉ trả đúng canonical thì không thử được khả năng tích hợp.

### 6.2 Tận dụng `mvp/` và `mvp-demo/`

| Dùng lại | Cách dùng | Không dùng |
|---|---|---|
| `mvp-demo/data/accounts.json` (7 tài khoản giả, `is_simulated`, kịch bản STR-*) | Seed trực tiếp cho `sis-mock` | `localStorage`, store trình duyệt |
| `record-source.js` (SRS-01..09, `Result<T>`) | Đặc tả hợp đồng adapter + test hợp đồng (chuyển thành OpenAPI/pytest) | Cài đặt `file://` |
| `announcements.json`, `catalog-versions.json` | Seed thông báo giả và chuỗi `catalog_version` (kịch bản "thay đổi khung") | Hiển thị thông báo ngay vào prompt |
| `rules.json` | Mẫu `rules.<trường>.json` | Hằng số hard-code trong `planner.js` (INTERNSHIP=COMP4870, HARD_MAX=22, hè 9 TC) |
| `tool-schema.json` (19 tool, envelope, mã lỗi) | Giữ nguyên làm hợp đồng tool; thêm trường `trace_id` | Chat rule-based (`chat.js`) |
| `planner.js` (`validate`), `solver.js`, `mvp-demo/tests/oracle.js`, `mvp/tests/planner.test.js` | **Oracle** để đối chiếu solver CP-SAT và validator Python; kịch bản STR-A..J thành golden set | Chạy JS trong production: chọn Python vì cùng stack với LangGraph/OR-Tools [I] |
| `mvp/data/bscs.json` (65 môn), `data/processed` | Catalog BSCS đã khóa tay; chunk RAG | Dữ liệu BSCS thô (0 tiên quyết) |

Khoảng trống: JS hiện **chưa có backend**; nhóm phải quyết định **port sang Python** (khuyến nghị, JS làm oracle) hay **gọi JS từ Node** (không khuyến nghị: chia đôi stack).

### 6.3 Tạo dữ liệu SV giả nhưng thực tế

Nguyên tắc: **không dùng dữ liệu SV thật, cả dạng đã ẩn danh**; mọi bản ghi `is_simulated=true`, mã `DEMO-` khác định dạng MSSV thật, tên có hậu tố "(giả)" như `mvp-demo` đang làm.

Quy trình [I/P]:
1. **Hồ sơ theo "persona"** (tân SV, đúng tiến độ, nợ môn, đổi hướng giữa chừng, đã học hè, sắp cảnh báo học vụ…), tái dùng 7 kịch bản của mvp-demo và mở rộng ~30–50 persona cho kiểm tải/đa dạng.
2. **Sinh bảng điểm từ khung đào tạo:** duyệt môn theo đồ thị tiên quyết (`data/processed/prerequisites.csv`) để mọi môn đã học đều hợp lệ tiên quyết; chọn tải tín chỉ theo quy chế của trường mô phỏng; điểm lấy từ phân phối tham số (giả định, ghi rõ) có tương quan theo SV (năng lực ẩn) để có nợ môn/GPA thực tế.
3. **Rèn luyện:** điểm theo kỳ có tương quan nhẹ với GPA; **thang và xếp loại cấu hình theo trường** vì chưa có nguồn về thang chuẩn (mục 2.2).
4. **Thông báo:** kịch bản có chủ đích (đổi tiên quyết, mở môn hè, đổi hạn đăng ký, **và thông báo độc hại để test prompt injection**), nhãn "GIẢ LẬP".
5. **Tên giả:** ghép từ danh sách họ/đệm/tên tự tạo; Faker locale `vi_VN`: **Không tìm thấy bằng chứng chắc chắn** trong phiên này (kiểm tra tại chỗ, vì Faker sẽ im lặng quay về `en_US` nếu locale không có, theo kết quả tìm kiếm thứ cấp).
6. Seed **tất định** (`seed=...`) để test lặp lại; tách "dữ liệu seed" khỏi "dữ liệu runtime".
7. Kiểm: chạy `validate()` trên mọi lịch sử học giả; nhãn "MÔ PHỎNG" trên mọi màn hình (đã nêu ở addendum §1; đặc biệt nếu mô phỏng giao diện `sv.dut.udn.vn`, tránh nhầm với hệ thống thật, rủi ro đã nêu ở BA).

### 6.4 Nhúng widget

- Cổng chèn `<script type="module" src="/pp/widget.js">` và `<pathplanner-widget tenant="demo-school" locale="vi">`.
- Widget gọi **cùng origin** `/api/pp/v1/...`; BFF dùng phiên cổng → JWT 5 phút → `pp-api`. Không có `Authorization` trong JS; không CORS.
- Widget chỉ **hiển thị** (plan, giải thích, trạng thái duyệt) và **gửi ý định** (mục tiêu, thời hạn, đổi hướng). Mọi quyết định nằm server.
- Theme bằng CSS custom properties để khớp giao diện từng trường; Shadow DOM tránh đè CSS cổng.
- Chế độ iframe cho cổng khó sửa: trang `/embed` + CSP `frame-ancestors <origin cổng>` bằng header + `postMessage` chỉ chấp nhận `event.origin` allowlist [D-s S072].

---

## 7. Hiệu năng, chi phí, độ tin cậy

### 7.1 Ước lượng tải (đợt đăng ký môn) [I, giả định mở]

Giả định: 5.000 SV hoạt động; cửa sổ đăng ký 30 phút đầu có 20% dùng PathPlanner = 1.000 run / 1.800 s ≈ **0,56 run/s trung bình; đỉnh ~10× ≈ 5–6 run/s** (đăng ký thường dồn vào vài phút đầu). Solver ~2 s/run (**số minh họa của harness-flow, chưa đo**) và một lõi mỗi solve → nhu cầu đỉnh ≈ 11–12 lõi-giây/giây.

Hệ quả: cần **hàng đợi + giới hạn đồng thời**, không để API giữ kết nối chờ; plan cache (hồ sơ giống nhau); 8 lõi cho worker là đủ nếu chấp nhận hàng chờ vài giây ở đỉnh. Replan hàng loạt khi catalog đổi: 3.000 SV × 2 s = 6.000 lõi-giây ≈ 12,5 phút trên 8 lõi, **không gọi LLM**.
Chưa biết [Không tìm thấy bằng chứng]: giới hạn tốc độ (rate limit) thực tế của nhà cung cấp LLM cho tài khoản của nhóm; số SV đồng thời thực của trường pilot.

### 7.2 Chiến lược độ tin cậy

| Cơ chế | Thiết kế |
|---|---|
| Timeout theo tầng | Tổng run ≤ 15 s (ngân sách harness-flow) gồm: LLM #1 ≤ 3 s, retrieval ≤ 1 s, solver ≤ 10 s (hard kill ngoài tiến trình), LLM #2 ≤ 6 s [P]; vượt → trả kết quả tốt nhất hiện có kèm cờ |
| Retry | Chỉ cho lỗi tạm thời (LLM timeout, 5xx), tối đa 2 lần, backoff + jitter. **Không retry** khi solver vô nghiệm (kết luận toán học, đúng như harness-flow) |
| Circuit breaker | Quanh LiteLLM: mở sau N lỗi liên tiếp trong cửa sổ, nửa mở thăm dò; trạng thái xuất ra metric |
| Fallback LLM | LiteLLM `fallbacks` (model phụ) [D-s S054] → nếu vẫn lỗi: **chế độ không-LLM** |
| **Chế độ không-LLM** | Bước 4 (hiểu mục tiêu): form có cấu trúc thay vì văn bản tự do (SV chọn hướng/số kỳ/hè); bước 8 (giải thích): **template xác định** sinh từ dữ liệu solver (tiên quyết, kỳ, tín chỉ, trích dẫn chunk) và ghi `explanation_status="template"`. **Plan luôn hợp lệ vì nó do solver + validator sinh**, LLM chỉ là lớp trình bày |
| Backpressure | Rate limit theo SV (ví dụ 20 lần/ngày, harness-flow) và theo tenant; 429 kèm `Retry-After`; hàng đợi có ưu tiên (SV sắp đăng ký > replan hàng loạt) |
| Bền vững | Checkpoint Postgres để resume sau crash, HITL không giữ kết nối [D S052/S053]; idempotency key |
| Suy giảm có kiểm soát | Khi SIS lỗi: dùng snapshot gần nhất + cảnh báo độ tươi; khi vector DB lỗi: graph tiên quyết + SQL (đường không-LLM) |

### 7.3 Chi phí LLM mỗi plan (giả định nêu rõ)

Giá từ S032 (truy cập 2026-11-17): Sonnet 5.5 $2/MTok vào, $10/MTok ra, cache read $0,10; Haiku 5.5 (prompt ≤100k) $0,10 vào, $0,50 ra; Batch API −50%. Chưa kiểm lại ngày 2026-11-20.

Giả định [P]: bước hiểu mục tiêu: 1.200 token vào/150 ra (Haiku); bước giải thích: 3.500 vào/800 ra (Sonnet); tổng 5.650 token < ngân sách 6.000 của harness-flow; 20% run có 1 retry giải thích.

| Phương án | Tính | Chi phí/plan |
|---|---|---|
| Haiku (hiểu) + Sonnet (giải thích) | 0,000195 + 0,015 (+20% retry ≈ 0,003) | **≈ US$0,018** |
| Cả hai Haiku | 0,000195 + 0,00075 | **≈ US$0,001** |
| Sonnet + prompt caching phần tĩnh ~1.500 token | tiết kiệm ≈ 1.500 × (2 − 0,10)/10⁶ ≈ 0,0029 | ≈ US$0,015 |

Quy mô: pilot 30 SV × 10 run = 300 run ≈ **US$5** (Sonnet) hoặc US$0,3 (Haiku); đợt đăng ký 5.000 SV × 3 run = 15.000 run ≈ **US$270** hoặc ≈ US$15; golden set 140 ca ≈ US$2,5/lần. Con số BA đã đưa (US$0,26/phiên chat) tính cho **phiên hội thoại nhiều lượt**, không mâu thuẫn với con số mỗi plan này.
Chưa tính: chi phí hạ tầng, GPU nếu self-host, embedding (chạy cục bộ: chi phí tính toán, không phí API).

### 7.4 SLO đề xuất [P, cần đo lại khi có số thật]

| SLI | SLO (pilot) |
|---|---|
| Tính đúng: plan **được xuất bản** vi phạm bất biến (validator) | **0** (bất biến thiết kế; sự cố nếu ≠ 0) |
| Trích dẫn bịa lọt ra người dùng (`EXPLAIN.citation_fabricated` không bị out-guard bắt) | **0** trong golden set + red-team |
| Độ trễ plan không giải thích, p95 | ≤ 5 s ngoài giờ đỉnh; ≤ 12 s trong giờ đỉnh |
| Độ trễ plan có giải thích, p95 | ≤ 15 s (khớp ngân sách harness-flow) |
| Khả dụng trong cửa sổ đăng ký | 99,5% (chấp nhận suy giảm sang chế độ không-LLM, tính là "khả dụng") |
| Tỷ lệ chế độ không-LLM | Theo dõi; cảnh báo > 5% |
| Thời gian từ khi thông báo được duyệt đến khi plan mới `proposed` cho SV bị ảnh hưởng | ≤ 24 giờ |
| Sự cố lộ dữ liệu chéo SV/tenant | 0 |

---

## 8. Lộ trình triển khai

### 8.1 Giai đoạn và tiêu chí hoàn thành (đo được) [P]

**G0 – Demo/đồ án (web mô phỏng + harness trên dữ liệu giả)**
- Dựng backend Python: FastAPI, LangGraph + PostgresSaver, CP-SAT, validator, RAG, compose chạy một lệnh.
- Hoàn thành khi: (1) `docker compose up` đến trạng thái healthy ≤ 10 phút trên máy sạch; (2) 5 kịch bản harness-flow chạy đúng với mã lỗi đúng taxonomy; (3) **100%** plan solver qua validator trên ≥ 1.920 tổ hợp tham số (sweep của `mvp/`); solver CP-SAT khớp oracle JS trên bộ STR-A..J; (4) golden set ≥ 140 ca, gate CI xanh; (5) test RLS "đọc chéo" pass; (6) widget nhúng được vào web mô phỏng bằng BFF, **không** token ở JS (kiểm tay + test); (7) 1 vòng "thông báo → duyệt → catalog_version → replan" chạy hết.

**G1 – Pilot 1 trường**
- Điều kiện vào: pháp chế đã duyệt DPIA (và CTIA nếu LLM ngoài); khóa dữ liệu 1 chương trình (nguồn, tiên quyết, requirement groups) có người ký; Q1–Q12 của BA đã được trường trả lời.
- Làm: adapter thật mức 1/2 (mục 2.2), OIDC thật, quan sát (Langfuse hoặc tương đương), runbook sự cố, nhóm 30 SV + cố vấn.
- Hoàn thành khi: SLO mục 7.4 đạt 4 tuần liên tiếp; **0** sự cố lộ dữ liệu; tỷ lệ plan bị cố vấn sửa/từ chối được đo và có ngưỡng chấp nhận do cố vấn đặt (mặc định đề xuất ≤ 30% sửa ở tháng đầu, giảm dần) [P]; có ≥ 20 ca mới từ sửa của cố vấn đưa vào golden set; chi phí thực/plan trong ±30% ước tính mục 7.3.

**G2 – Multi-school**
- Làm: tách `tenant config`, thư viện adapter + **bộ test hợp đồng**, Helm chart, integration kit (proxy, CSP, widget), quy trình onboarding trường.
- Hoàn thành khi: trường thứ 2 lên được với **0 thay đổi lõi** (chỉ thêm adapter + config + rules + catalog); thời gian onboarding đo được (mục tiêu ≤ 10 người-ngày không tính chờ trường; con số là [P], giá trị tham chiếu của BA cho DUT là 15–20 người-ngày với kiến trúc hiện tại); cùng bộ eval chạy được cho cả hai trường; không có cấu hình trường nào là hằng số trong mã (kiểm bằng grep/test).

### 8.2 Rủi ro chính và cách giảm

| Rủi ro | Giảm thiểu |
|---|---|
| **Dữ liệu sai hoặc thiếu** (khung BSCS Cohort 5 chưa có source ID; BSCS thô 0 tiên quyết; quy tắc áp dụng khi đổi khung chưa có căn cứ) | Stage "khóa dữ liệu" trước G1; mọi quy chế có nguồn + người ký; plan luôn kèm `catalog_version` |
| **Pháp lý/gửi dữ liệu ra ngoài** | Tối thiểu hóa; hai tầng dữ liệu; DPIA/CTIA sớm; phương án self-host dự phòng; không dùng dữ liệu thật cho đến khi pháp chế duyệt |
| **SIS trường không có API** | Ba mức adapter (mục 2.2); thỏa thuận export định kỳ; nhập tay có đồng ý làm dự phòng |
| **LLM tiếng Việt kém/bịa** | LLM chỉ ở 2 đầu, out-guard, template dự phòng, golden set tiếng Việt, LLM-as-Judge có hiệu chuẩn người (S042) |
| **Prompt injection qua thông báo** | Mục 3.5; người duyệt; không dùng thông báo thô trong prompt |
| **Phụ thuộc công cụ đổi hướng** (Promptfoo→OpenAI, Langfuse→ClickHouse; OTel GenAI chưa stable; arq maintenance) [S066, S063, S065, S074] | Ghim phiên bản, lớp bọc mỏng quanh tracing/eval/queue, tránh tính năng riêng nhà cung cấp |
| **Solver treo hoặc vượt thời gian** | Tiến trình riêng + hard kill; unsat core; oracle JS để kiểm chéo |
| **Gánh nặng vận hành cho nhóm sinh viên** | Giữ stack ở mức tối thiểu của G0; tùy chọn `obs` tách profile; không cố làm multi-tenant dùng chung |
| **Mô phỏng bị nhầm là hệ thống chính thức** | Nhãn "MÔ PHỎNG" mọi màn hình, không sao chép giao diện/dữ liệu thật |
| **Mâu thuẫn giữa quyết định trường demo** (VinUni vs DUT) | Chốt D1 ngay; `rules.<trường>.json` để đổi trường không đổi mã |

### 8.3 Việc cần kiểm chứng trước khi triển khai (còn mở)

Xác nhận `FORCE ROW LEVEL SECURITY` và hành vi RLS với connection pool trên trang postgresql.org; đọc README pgvector bản mới; xếp hạng thật của các embedding tiếng Việt (bảng VN-MTEB, S059) và mini-benchmark riêng; tài liệu SSE/EventSource (MDN) và khả năng nginx; điều khoản retention áp cho model cụ thể (S076); giấy phép Phoenix; văn bản gốc NĐ 356/2025 (số Điều); đọc PDF chính sách dữ liệu của VinUni (S038).

### 8.4 Quyết định cần người dùng chốt

| # | Quyết định | Lựa chọn | Đề xuất |
|---|---|---|---|
| D1 | Trường mô phỏng cổng: **VinUni BSCS** (BA khuyến nghị) hay **DUT** (addendum, có người đang dựng cổng) | VinUni / DUT / cả hai, VinUni trước | Chốt sớm; kiến trúc `rules.<trường>.json` cho phép cả hai |
| D2 | LLM: API ngoài (dữ liệu giả) → pilot thế nào; hay self-host | Ngoài/self-host/hai tầng | Hai tầng; quyết định pilot sau tư vấn pháp chế |
| D3 | Port logic JS sang Python (CP-SAT) hay giữ JS | Port, JS làm oracle / giữ JS | Port |
| D4 | Cách nhúng chính | Web Component+BFF / iframe / SDK | Web Component+BFF; iframe dự phòng |
| D5 | Triển khai multi-school | Silo / schema-per-tenant / RLS dùng chung | Silo trước |
| D6 | Observability ở đồ án | Log+OTel đơn giản / Langfuse | Đơn giản; Langfuse ở pilot |
| D7 | Hàng đợi | Celery / RQ / Postgres-queue | Theo kinh nghiệm nhóm (không dùng arq) |
| D8 | Cơ chế đổi `catalog_version` do ai duyệt | Phòng Đào tạo / cố vấn trưởng / quản trị | Hỏi trường; luôn có người duyệt |
| D9 | Thời hạn lưu trữ log/prompt/plan | Mặc định đề xuất mục 3.4 | Xác nhận với pháp chế |
| D10 | Ngưỡng chấp nhận pilot (tỷ lệ cố vấn sửa, SLO) | Mặc định mục 8.1 | Xác nhận với cố vấn |
| D11 | Nguồn thông báo nào được phép thu thập, bằng cách nào | Webhook/RSS/polling công khai | Chỉ nguồn trường cho phép; không scrape vùng đăng nhập |
| D12 | Ngân sách LLM cho đồ án/pilot | Ví dụ ≤ US$500 như BA ước tính | Theo mục 7.3 |

### 8.5 Quyết định đã chốt (user, 2026-11-20)

Bản này ghi lại các quyết định của user sau khi báo cáo được reviewer kiểm tra. Mục "Đề xuất" ở bảng 8.4 giữ nguyên làm lịch sử.

| # | Quyết định | Trạng thái |
|---|---|---|
| D1 | Trường demo: **DUT, ngành CNTT Việt–Nhật** (user hiểu cổng SV DUT, có dữ liệu CTĐT gồm bắt buộc/tự chọn/tiên quyết và nhiều định hướng). Dữ liệu ngành này được nhập/khóa tay; dòng DUT trong CSV chung không đủ dùng (75% `requirement=unknown`, thiếu mã môn, theo `data/README.md`). | Đã chốt |
| D2 | LLM trên **AWS Bedrock** (tài khoản mới, mục tiêu ~US$200 credit). Chưa kiểm: model Claude nào và vùng nào có trên Bedrock, giá Bedrock (mục 7.3 dùng giá API Anthropic), điều khoản lưu dữ liệu của Bedrock. Với dữ liệu giả, chưa vướng mục 3.7. | Nhiều khả năng; cần kiểm trước khi dựng |
| D3 | Port sang Python (CP-SAT), JS làm oracle | Theo đề xuất |
| D4 | Web Component + BFF (Next.js của web mô phỏng) | Theo đề xuất |
| D5 | Chỉ 1 trường: bỏ multi-tenant, Helm, schema-per-tenant. Giữ phân quyền SV/cố vấn và 1 file cấu hình `rules.dut.json`. | Đã chốt |
| D6 | Log JSON (`run_id`, `trace_id`) + bảng `run_spans`; không Langfuse | Đã chốt |
| D7 | MVP: process pool trong API + bảng job Postgres (bỏ Redis). Khi cần replan hàng loạt: RQ. Không dùng arq (S074). Đây là đánh giá của người viết [I], không có so sánh chính thức. | Đề xuất, chờ xác nhận |
| D8 | `catalog_version` là phiên bản của toàn bộ ảnh chụp catalog + quy chế, không phải một quyết định đơn lẻ. Nguồn: thông báo của Phòng Đào tạo. Người duyệt ở đồ án: vai trò quản trị catalog (nhóm đồ án), so thông báo gốc với bản trích xuất; bản ghi version lưu URL thông báo gốc. | Đã chốt hướng |
| D9 | Log/prompt giữ 15–30 ngày. Plan: bản mới nhất đang dùng, kèm 2–3 bản trước hoặc các bản cố vấn đã duyệt (cần cho replan "đổi ít nhất" và truy vết). Nhật ký quyết định cố vấn (không chứa nội dung) giữ lâu hơn. Ca đáng giữ được ẩn danh và chép sang golden set trước khi log hết hạn. TTL cấu hình được. Thời hạn theo luật: không tìm thấy bằng chứng. | Đã chốt hướng |
| D10 | Ngưỡng nghiệm thu pilot | Hoãn (đang dựng MVP) |
| D11 | Thông báo DUT nằm ở trang đầu web sinh viên, không cần đăng nhập → polling có kiểm soát khả thi (allowlist nguồn, tôn trọng robots.txt, rate limit, `body_hash`). Vẫn không scrape khu vực cần đăng nhập. Trong web mô phỏng có thể dùng mục thông báo riêng để demo tái lập được. | Đã chốt |
| D12 | Ngân sách ~US$200 nếu lấy được credit AWS; chưa tính chi tiết. Đặt trần chi phí theo từng lần chạy (Budget Manager) và theo tháng (AWS Budgets). | Hoãn chi tiết |

**Hệ quả cần làm khi cập nhật báo cáo ở lần sau:** các mục 5.3 (K8s/multi-tenant), 4 (hàng Queue/Langfuse) và 8.1 (G2) không còn trong phạm vi; mục 3.6 và 7.3 cần đối chiếu lại với Bedrock; mục 8.2 rủi ro "Mâu thuẫn VinUni vs DUT" được đóng. Các điểm reviewer nêu (ngân sách thời gian 15 giây, 8 lõi, CSRF/replay, `thread_id`, 72 giờ) vẫn còn mở.

---

## Nguồn

Nguồn **mới** (S052–S078), truy cập 2026-11-20, chi tiết trạng thái đọc ở `research/sources/registry.md`:
S052 LangGraph persistence [D] · S053 LangGraph durable execution [D-s] · S054 LiteLLM proxy [D-s] · S055 OR-Tools CP-SAT solver limits [D-s] · S056 pgvector README mirror [D-s] · S057 bge-m3 [D] · S058 bge-reranker-v2-m3 [D] · S059 VN-MTEB [abstract] · S060 Presidio languages [D] · S061 OWASP LLM01 [D] · S062 Langfuse self-hosting [D-s] · S063 ClickHouse/Langfuse [D-s] · S064 Arize Phoenix [D-s] · S065 OTel GenAI semconv [D-s] · S066 Promptfoo CI/CD [D-s] · S067 PostgreSQL CREATE POLICY (mirror) [D-s] · S068 OneRoster 1.2 [D-s] · S069 LTI 1.3 Advantage [D-s] · S070 OpenID Connect Core [D-s] · S071 RFC 8693 [D-s] · S072 CSP frame-ancestors [D-s] · S073 Kubernetes multi-tenancy [D-s] · S074 arq README [D] · S075 trivy-action [D-s] · S076 Anthropic data retention [D, đọc một phần] · S077 EY tóm tắt NĐ 356/2025 [D, thứ cấp] · S078 PwC data protection [snippet].

Nguồn **cũ** dùng lại: S024 (Student Guide, `sis.vinuni.edu.vn`), S032 (giá/data residency Anthropic), S033 (tool use), S034 (Citations), S035–S037 (luật dữ liệu/AI), S038–S039 (VinUni PDP, GenAI), S040 (LLM-Modulo), S042 (LLM-as-Judge), S043–S044 (RAG advising cục bộ), S046, S050 (DUT, cổng SV).

Nguồn **không đăng ký** (chỉ là kết quả tìm kiếm thứ cấp, không dùng làm bằng chứng tính năng): bài so sánh SSE/WebSocket, so sánh Celery/RQ/arq, hướng dẫn Faker, các blog LiteLLM/Langfuse/Phoenix.

## Những chỗ chưa chắc hoặc không tìm thấy bằng chứng

- Tiếng Việt: bge-m3/bge-reranker không nêu tiếng Việt trên model card; chưa đọc bảng VN-MTEB; full-text search tiếng Việt trong Postgres chưa kiểm chứng.
- Presidio: không có tiếng Việt sẵn; không tìm được công cụ NER tiếng Việt đáng tin để thay.
- Model open-weight tự host đạt chất lượng tiếng Việt cho nhiệm vụ này: Không tìm thấy bằng chứng.
- LangSmith, DeepEval, Ragas, SAML, problem+json, Faker `vi_VN`, Sentry, Celery vs RQ: chưa tra nguồn chính thức.
- Pháp lý: chỉ nguồn thứ cấp; không tìm thấy bằng chứng về phân loại điểm số SV, dữ liệu người chưa thành niên, thời hạn lưu trữ, cloud trong nước; Luật AI chưa kiểm tra.
- Chính sách retention của Anthropic áp cho Sonnet 5.5/Haiku 5.5 chưa xác nhận (S076 đọc một phần).
- Số phiên bản các công cụ: cố ý không nêu (không xác minh).
- Mọi số về hiệu năng (solver ~2 s, tải đỉnh) là **ước tính/minh họa**, chưa đo.
- SIS của trường Việt Nam dùng OneRoster/LTI: Không tìm thấy bằng chứng.
