# Checklist yêu cầu — Lab 07 (K4-L3B)

Tổng hợp từ [`day7-lab-data-foundations.md`](day7-lab-data-foundations.md) và các file mà nó dẫn tới. Mọi mục đều lấy nguyên từ các file nguồn; mục nào không có trong nguồn thì ghi rõ. Trạng thái kiểm tra ngày 2026-09-20.

## 0. Link và file được dẫn tới

### Link ngoài (đã kiểm tra)

| Link | Dẫn từ | Kết quả kiểm tra |
| --- | --- | --- |
| https://github.com/VinUni-AI20k/K4-L3B-Data-Foundations | Mục 2, starter repo lớp L3B (lớp của bạn) | HTTP 200 |
| https://github.com/VinUni-AI20k/K4-L3A-Data-Foundations | Mục 2, starter repo lớp L3A | HTTP 200 |
| https://aistudio.google.com/apikey | Phụ lục B, lấy Gemini API key | Chuyển tới trang đăng nhập Google (bình thường) |

Link vlearn để nộp bài: file nguồn **không cung cấp URL cụ thể**, chỉ ghi "nộp link repo GitHub trên vlearn". Hãy hỏi giảng viên hoặc trợ giảng.

### File nội bộ trong repo

| File | Vai trò theo file nguồn | Tồn tại |
| --- | --- | --- |
| [`docs/DATA_COLLECTION.md`](docs/DATA_COLLECTION.md) | Chuẩn chấm cho deliverable #2 (dữ liệu) | Có |
| [`K4_VARIANT.md`](K4_VARIANT.md) | Ràng buộc riêng của L3B | Có |
| [`docs/SCORING.md`](docs/SCORING.md) | Thang điểm | Có |
| [`docs/EVALUATION.md`](docs/EVALUATION.md) | Tiêu chí đánh giá retrieval | Có |
| [`exercises.md`](exercises.md) | Bài tập, công thức chunking | Có |
| [`report/REPORT_CANHAN.md`](report/REPORT_CANHAN.md) | Báo cáo cá nhân (mẫu) | Có |
| [`report/REPORT_NHOM.md`](report/REPORT_NHOM.md) | Báo cáo nhóm (mẫu) | Có |
| [`scripts/fetch_public_pages.py`](scripts/fetch_public_pages.py) | Crawler mẫu | Có |
| [`scripts/urls.example.csv`](scripts/urls.example.csv) | CSV mẫu cho crawler | Có |
| [`.python-version`](.python-version) | Phiên bản Python chuẩn (3.11) | Có |
| [`requirements-local.txt`](requirements-local.txt) | Embedder local (Phụ lục B) | Có |
| `data/urls.csv` | Bạn tự tạo từ `urls.example.csv` | **Chưa có** (cần tạo) |
| `data/<ten-chu-de>/sources.csv` | Deliverable #2 | **Chưa có** (`data/ecommerce/` chưa có file này) |
| `bench.py` | Deliverable #3 | **Chưa có** (bạn tự viết) |
| `ket_qua_benchmark.txt` | Deliverable #3 | **Chưa có** (sinh ra khi chạy `bench.py`) |

Các mục "Chưa có" là sản phẩm bạn phải tạo, không phải lỗi của repo.

## 1. Lộ trình và checkpoint

Mốc thời gian tính tương đối từ lúc lớp bắt đầu (0:00).

| Giai đoạn | Thời gian | Checkpoint |
| --- | --- | --- |
| 1. Dữ liệu | 0:00–1:00 | CP1 0:20 · CP2 1:00 |
| 2. Code cá nhân | 1:00–2:30 | CP3 1:45 · CP4 2:30 |
| 3. Chiến lược | 2:30–3:00 | CP5 3:00 |
| 4. So sánh | 3:00–3:25 | CP6 3:25 |
| 5. Demo & nộp | 3:25–4:00 | CP7 4:00 |

## 2. Deliverable

| # | Nộp gì | Ai | Điểm | Xong |
| --- | --- | --- | --- | --- |
| 1 | `src/` hoàn thiện, `pytest tests/ -v` → 42 passed | Mỗi người | 30 | [x] |
| 2 | `data/<chu-de>/` — 5–10 tài liệu `.md` + `sources.csv` | Nhóm | 10 | [ ] |
| 3 | `bench.py` + `ket_qua_benchmark.txt` | Mỗi người | nền cho #4, #5 | [x] |
| 4 | `report/REPORT_CANHAN.md` | Mỗi người | 60 (gồm #1) | [x] |
| 5 | `report/REPORT_NHOM.md` | Nhóm | 40 (gồm #2) | [ ] |
| 6 | Repo GitHub `K4-DAY07-HoVaTen-MSSV` + link vlearn | Mỗi người | điều kiện chấm | [ ] |

## 3. Checklist theo checkpoint

### CP1 — 0:20 · Setup

- [x] Python 3.11, venv (`.venv/`), `pip install -r requirements.txt` (xong ngày 2026-09-20)
- [x] `pytest tests/ -v` → **31 failed, 11 passed** trên 42 test, lỗi là `NotImplementedError` (đã khớp baseline)
- [ ] Fork đúng repo lớp (L3B) trước khi clone, để có remote GitHub riêng để push

### CP2 — 1:00 · Dữ liệu

Nguồn: [`docs/DATA_COLLECTION.md`](docs/DATA_COLLECTION.md) mục 6 và [`K4_VARIANT.md`](K4_VARIANT.md).

- [ ] 5–10 file `.md` cùng chủ đề (chính sách đổi trả / bảo hành / quy định người bán–người mua trên TMĐT), `doc_id` không trùng
- [ ] Mỗi file có đủ metadata: `doc_id`, `title`, `source_url`, `retrieved_at`, `document_version`, `audience`
- [ ] `doc_id` trùng tên file (script kiểm tra ở CP2 so `doc_id` với `p.stem`)
- [ ] Có thêm ít nhất một trường lọc khác ngoài `audience` (ví dụ `category`, `language`)
- [ ] `audience` có ít nhất 2 giá trị khác nhau (`buyer` / `seller` / `both`)
- [ ] `sources.csv` khớp 1-1 với các file; header: `doc_id,file_path,title,source_url,retrieved_at,document_version,license_or_permission`
- [ ] `document_version` chỉ ghi số hiệu khi nguồn nêu; nếu không thì `"not-stated"`, không bịa
- [ ] `source_url` là URL trang gốc, không phải link tìm kiếm; `retrieved_at` dạng `YYYY-MM-DD`
- [ ] Trang gộp thông tin buyer và seller thì tách thành nhiều file, mỗi file một `audience`
- [ ] Đã làm sạch (bỏ menu, banner, footer, danh sách sản phẩm), đã đọc lại từng file, không bị tự dịch sang tiếng Anh
- [ ] Đã đọc `robots.txt` và điều khoản; trang bị cấm thì đổi nguồn. Không đăng nhập, không vượt CAPTCHA, không dùng dữ liệu cá nhân
- [ ] Crawl cách nhau ≥ 1 giây/request (crawler mẫu đã làm sẵn)
- [ ] Chạy script kiểm tra CP2 (có trong file lab, mục "CHECKPOINT 2"), mọi dòng `OK`
- [ ] Điền Data Inventory và Metadata Schema vào `REPORT_NHOM.md` mục 1

Lưu ý thực tế:
- Hai file trong `data/ecommerce/` (`return-refund-policy.md`, `seller-warranty-policy.md`) dùng `source_url: https://example.com/...`. Chính file ghi đây là **template mẫu**, phải thay bằng nguồn công khai thật trước khi làm benchmark. Chúng cũng chưa có `sources.csv`.
- Lỗi crawler đã biết: `LookupError: unknown encoding` khi server trả charset lạ. Bỏ URL đó khỏi CSV rồi chạy tiếp.

### CP3 — 1:45 · `chunking.py`

- [x] Warm-up: cosine similarity (câu cao khác từ vựng nhưng cùng nghĩa, câu thấp, vì sao cosine hơn Euclid) → REPORT_CANHAN mục 1
- [x] Warm-up: bài toán chunking 10.000 ký tự / 500 / 50, kiểm lại bằng `FixedSizeChunker`, và trả lời khi overlap = 100 → REPORT_CANHAN mục 1
- [x] `SentenceChunker.chunk`: tách theo `". "`, `"! "`, `"? "`, `".\n"`, giữ dấu câu, text rỗng trả `[]`
- [x] `RecursiveChunker.chunk` / `_split`: separator `["\n\n", "\n", ". ", " ", ""]`, có cả đệ quy xuống và gom lên, xử lý `separators=[]`
- [x] `compute_similarity`: trả `0.0` khi vector độ dài 0
- [x] `ChunkingStrategyComparator.compare`: đúng 3 key `fixed_size`, `by_sentences`, `recursive`, mỗi key có `count`, `avg_length`, `chunks`; chặn chia 0
- [x] Giữ nguyên chữ ký hàm (`def ...`), chỉ thay phần `TODO` / `raise NotImplementedError`
- [x] `pytest tests/ -k "Chunker or Similarity or Compare" -v` → **23 passed**
- [x] Ghi edge case chưa xử lý (chữ viết tắt, số thập phân) vào báo cáo

### CP4 — 2:30 · `store.py`, `agent.py` (mốc quan trọng nhất)

- [x] `EmbeddingStore`: `_make_record`, `_search_records`, `add_documents`, `search`, `get_collection_size`, `search_with_filter`, `delete_document`
- [x] Mặc định dùng in-memory (`_use_chroma = False`). ChromaDB chỉ là backend tùy chọn (`use_chroma=True`, cần `pip install chromadb`), đã kiểm chứng cho kết quả giống in-memory; 42 test không đụng tới nó
- [x] `_make_record` copy metadata và luôn có `metadata['doc_id']`
- [x] `search` và `search_with_filter` dùng chung `_search_records`; kết quả bỏ `embedding`
- [x] `search_with_filter` lọc **trước** rồi mới search
- [x] `delete_document` xóa mọi chunk có `doc_id` khớp, trả `True`/`False`
- [x] `KnowledgeBaseAgent.answer`: truy xuất top-k → prompt có ngữ cảnh đánh số `[1] [2] [3]` kèm nguồn → gọi `llm_fn`
- [x] Prompt yêu cầu chỉ dùng ngữ cảnh; store rỗng thì trả thông báo, không crash, không gọi LLM
- [x] `pytest tests/ -v` → **42 passed**; `python main.py "Chunking là gì?"` chạy hết. Dòng `Skipping missing file: data/customer_support_playbook.txt` là bình thường
- [x] Dán output `pytest tests/ -v` vào REPORT_CANHAN mục 3

Hiện trạng (2026-09-20): 0 chỗ `NotImplementedError` trong `src/`, 42/42 test pass.

### CP5 — 3:00 · Chiến lược và benchmark

- [ ] Nhóm chốt đúng 5 benchmark query, đa dạng dạng hỏi, kèm gold answer trích được từ tài liệu (không suy đoán chính sách) → REPORT_NHOM mục 3
- [ ] Ít nhất 1 query **cần** `metadata_filter={"audience": "buyer"}` (hoặc `"seller"`) mới đúng
- [ ] Baseline: `ChunkingStrategyComparator().compare()` trên 2–3 tài liệu, bỏ frontmatter trước → REPORT_NHOM mục 2
- [ ] Mỗi thành viên một chiến lược chunking khác nhau, không trùng
- [ ] Ít nhất 1 thành viên chunk theo heading/section (khi cắt section dài phải gắn lại tiêu đề vào từng mảnh)
- [x] `bench.py`: đọc file `.md`, tách frontmatter, chunk **ngoài** store, mỗi chunk thành `Document(id=f"{stem}#{i}", ...)`
- [x] `metadata['doc_id']` = tên file gốc; frontmatter trải vào **mọi** chunk
- [x] Mỗi người chỉ đổi một dòng chọn chunker
- [x] `python bench.py` in số chunk đã nạp và top-3 (score, doc_id) cho 5 câu

### CP6 — 3:25 · Chạy, so sánh, phân tích lỗi

- [x] Dùng embedder thật nếu được (Phụ lục B); nếu dùng mock thì ghi rõ trong báo cáo là số liệu bị chi phối bởi mock
- [x] Chấm hai mức: theo `doc_id` gold **và** theo chuỗi đặc trưng có trong ngữ cảnh truy xuất
- [x] Thang mỗi câu: 2đ (gold ở top-1 và ngữ cảnh có đáp án), 1đ (top-2/3), 0đ (vắng hoặc ngữ cảnh không trả lời được)
- [ ] A/B bắt buộc: câu cần filter chạy có/không `metadata_filter`, trên cả 3 chiến lược, ghi top-3 từng lần. Nếu hai lần giống hệt thì sửa câu hỏi hoặc cách tách theo `audience` (mới làm xong cho chiến lược Sentence của Thịnh: câu 2, top-3 khác nhau giữa có và không filter; còn thiếu Fixed và Recursive)
- [x] Ít nhất 1 failure case, đủ 3 phần: câu hỏi nào hỏng, vì sao, đề xuất sửa
- [x] `ket_qua_benchmark.txt` của riêng mình; điền bảng top-3 vào REPORT_CANHAN mục 5
- [ ] Bảng so sánh giữa các thành viên và failure case vào REPORT_NHOM mục 2 và mục 4 (theo file lab)

### CP7 — 4:00 · Demo và nộp

- [ ] Demo 6–8 phút, mọi thành viên đều nói phần chiến lược của mình; terminal đã mở sẵn `bench.py` chạy được
- [x] `pytest tests/ -v` → 42 passed, không còn `raise NotImplementedError`
- [ ] `data/<chu-de>/` 5–10 tài liệu đủ metadata, `sources.csv` khớp 1-1
- [ ] Ít nhất 1 query dùng `metadata_filter` theo `audience`
- [ ] Ít nhất 1 thành viên chunk theo heading/section
- [ ] Hai báo cáo điền đủ, output pytest là thật
- [ ] `bench.py` + `ket_qua_benchmark.txt` đã commit
- [ ] `git status` không thấy `.venv/` hay `.env` (đã nằm trong `.gitignore`); kiểm tra lại repo GitHub sau khi push, không để lộ key
- [ ] Repo đặt tên `K4-DAY07-HoVaTen-MSSV` (họ tên liền, không dấu), nộp **link repo** trên vlearn (không nộp zip)

## 4. Báo cáo cần điền

### `REPORT_CANHAN.md` (60 điểm, mỗi người một bản)

| Mục | Nội dung | Điểm |
| --- | --- | --- |
| 1 | Khởi động (cosine, chunking math) | 5 |
| 2 | Hướng tiếp cận (chunking, store, agent) | 10 |
| 3 | Hoàn thiện code, dán output pytest, số test pass / 42 | 30 |
| 4 | Dự đoán độ tương tự: 5 cặp câu, dự đoán vs thực tế, phản ngẫm | 5 |
| 5 | Kết quả truy xuất của tôi (5 câu của nhóm) | 10 |

### `REPORT_NHOM.md` (40 điểm, cả nhóm một bản)

| Mục | Nội dung | Điểm |
| --- | --- | --- |
| 1 | Lựa chọn tài liệu (Data Inventory, governance checklist, Metadata Schema) | 10 |
| 2 | Thiết kế chiến lược (Baseline, chiến lược từng người, so sánh) | 15 |
| 3 | 5 câu hỏi đánh giá + chất lượng truy xuất, tác dụng của filter | 10 |
| 4 | Thuyết trình và bài học nhóm | 5 |

## 5. Ràng buộc riêng của L3B ([`K4_VARIANT.md`](K4_VARIANT.md))

- [ ] Mỗi tài liệu có `audience` (`buyer` / `seller` / `both`) và ít nhất một trường hữu ích khác
- [ ] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version`; chỉ dùng chính sách công khai hoặc được phép chia sẻ
- [ ] Ít nhất 1 trong 5 query cần `metadata_filter` theo `audience`
- [ ] Ít nhất 1 thành viên chunk theo heading/section
- [ ] Gold answer trích được từ tài liệu nhóm thu thập

## 6. Điểm bất nhất giữa các file nguồn (cần lưu ý)

1. **Số mục báo cáo trong `exercises.md` lệch với mẫu thật.** `exercises.md` bảo ghi vào "Phần 2 (Lựa chọn tài liệu)", "Phần 4 (Hướng tiếp cận)", "Phần 5 (Dự đoán độ tương tự)", "Phần 6", "Phần 7". Các mẫu trong `report/` không đánh số như vậy: REPORT_CANHAN có 5 mục, REPORT_NHOM có 4 mục (xem mục 4 ở trên). Nên theo số mục trong file lab và trong mẫu report.
2. **Vị trí file lab.** README ghi file lab ở `../codelabs/day7-lab-data-foundations.md`, nhưng file thật nằm ở thư mục gốc repo (`day7-lab-data-foundations.md`). Đường dẫn trong README không tồn tại.
3. **Số test.** README ghi "Hơn 30 tests", còn file lab và `requirements.txt` ghi 42 test. Baseline `31 failed, 11 passed` cộng lại đúng 42.
4. **`docs/INSTRUCTOR_GUIDE.md`.** README liệt kê file này trong cấu trúc thư mục, nhưng file không có trong repo (commit `9e16211` đã gitignore và gỡ khỏi repo public).
5. **Python.** File lab nói 3.11 là chuẩn, 3.10+ vẫn chạy được. Máy này dùng Python 3.11.9 nên khớp.
6. **`preparationTipIds`** trong frontmatter của file lab (`huong-dan-cai-vs-code-va-git`, ...) chỉ là ID nội dung, không có URL trong file nguồn, nên không đưa vào danh sách link.

## 7. Thang điểm ([`docs/SCORING.md`](docs/SCORING.md))

**Cá nhân (60):** Code 30 · Hướng tiếp cận 10 · Kết quả truy xuất 10 · Warm-up 5 · Dự đoán similarity 5.

**Nhóm (40):** Thiết kế chiến lược 15 · Chất lượng bộ tài liệu 10 · Chất lượng truy xuất 10 · Demo 5.

Mỗi câu benchmark tối đa 2 điểm: 2 (top-3 có chunk liên quan và agent trả lời đúng), 1 (có chunk liên quan nhưng thiếu chi tiết hoặc không ở top-1), 0 (không có chunk liên quan trong top-3).

Nguyên tắc chấm: chiến lược (15 điểm) được đánh giá cao hơn hiệu suất truy xuất (10 điểm), tức là khả năng suy nghĩ và giải thích quan trọng hơn điểm số thuần túy.

## 8. Tiêu chí tự đánh giá retrieval ([`docs/EVALUATION.md`](docs/EVALUATION.md))

- [ ] **Retrieval Precision:** top-3 có ít nhất 2 kết quả liên quan trực tiếp; score có phân biệt được kết quả tốt và nhiễu
- [ ] **Chunk Coherence:** so `count` / `avg_length` giữa 3 chiến lược, đánh giá chunk có trọn ý không
- [ ] **Metadata Utility:** so top-3 giữa `search()` và `search_with_filter()`; filter có quá chặt làm mất kết quả tốt không
- [ ] **Grounding Quality:** câu trả lời của agent dựa trên ngữ cảnh truy xuất; chỉ ra được chunk nào dùng để trả lời (Source Traceability)
- [ ] **Data Strategy Impact:** bộ tài liệu và chiến lược chunking/metadata phù hợp chủ đề; so sánh điểm giữa các thành viên

## 9. Embedder OpenAI (đang dùng ở máy này)

Theo Phụ lục B của file lab:

- [x] `pip install openai` (đã cài `openai` 3.16.2)
- [x] `.env` có `EMBEDDING_PROVIDER` và `OPENAI_API_KEY`
- [ ] `.env` có `OPENAI_EMBEDDING_MODEL=text-embedding-3-small` (file lab liệt kê biến này, chưa xác minh trong `.env`; nếu thiếu thì code dùng mặc định `text-embedding-3-small`)
- [x] Smoke test `OpenAIEmbedder` trả vector 1536 chiều
- [x] Nên cache embedding theo hash nội dung trong `bench.py` để chạy lại không tốn thêm tiền (file lab khuyến nghị)
- [ ] `openai` chưa có trong `requirements.txt` (file lab nói phần bắt buộc chỉ cần `pytest` và `python-dotenv`)
