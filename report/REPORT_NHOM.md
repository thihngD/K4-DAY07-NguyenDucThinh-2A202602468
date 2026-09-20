# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** [Tên nhóm]
**Thành viên:** [Họ tên từng thành viên]
**Ngày:** [Ngày nộp]

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng/Hoàn tiền trên sàn thương mại điện tử Shopee Việt Nam (chủ đề bắt buộc của lớp L3B).

**Tại sao nhóm chọn chủ đề này?**
> Đây là chủ đề bắt buộc của lớp L3B (chính sách đổi trả, bảo hành, quy định người bán/người mua) và Shopee Trung tâm trợ giúp là nguồn chính thức, công khai, có `robots.txt` cho phép (`Allow: /`, kiểm tra ngày 2026-09-20). Các bài viết có cấu trúc rõ (tiêu đề, bước, trường hợp) nên phù hợp để so sánh chiến lược chunking.

### Danh sách tài liệu (Data Inventory)

> Số ký tự tính trên phần thân đã làm sạch, không gồm frontmatter. **Hiện mới có 4 tài liệu** (yêu cầu 5–10), sẽ bổ sung khi nhóm chốt thêm nguồn.

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Cách đóng gói đơn hàng hoàn trả (`shopee-dong-goi-hang-hoan-tra`) | https://help.shopee.vn/portal/4/article/79508 (đầy đủ trong `sources.csv`) | 2026-09-20 / not-stated | 3233 | audience=buyer, category=returns-policy, language=vi |
| 2 | Cách theo dõi tình trạng vận chuyển hàng hoàn trả (`shopee-theo-doi-van-chuyen-hoan-tra`) | https://help.shopee.vn/portal/4/article/189476 (đầy đủ trong `sources.csv`) | 2026-09-20 / not-stated | 685 | audience=buyer, category=returns-policy, language=vi |
| 3 | Hướng dẫn Người mua trả lời đề xuất Hoàn Tiền Ngay của Người bán (`shopee-hoan-tien-ngay`) | https://help.shopee.vn/portal/4/article/190387 (đầy đủ trong `sources.csv`) | 2026-09-20 / not-stated | 1059 | audience=buyer, category=returns-policy, language=vi |
| 4 | Quy trình Shopee xử lý yêu cầu Trả hàng/Hoàn tiền (`shopee-quy-trinh-xu-ly-yeu-cau`) | https://help.shopee.vn/portal/4/article/190242 (đầy đủ trong `sources.csv`) | 2026-09-20 / not-stated | 8023 | audience=buyer, category=returns-policy, language=vi |
| 5 | | | | | |

> Ghi chú: cột nguồn chỉ rút gọn tới mã bài viết; URL đầy đủ nằm trong `data/shopee-tra-hang/sources.csv` và frontmatter từng file. Bỏ tham số theo dõi `?previousPage=secondary category` khỏi URL gốc. Trang nguồn không nêu số hiệu phiên bản hay ngày hiệu lực nên `document_version` là `not-stated`.

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. (4 tài liệu hiện có; nhóm cần kiểm lại khi thêm nguồn.)
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

> Còn thiếu so với `docs/DATA_COLLECTION.md` mục 6: chưa đủ 5 tài liệu, và cả 4 tài liệu đều `audience: buyer` (bài "Quy trình Shopee xử lý yêu cầu" cũng viết cho người mua: xưng "bạn", nhắc Người bán ở ngôi thứ ba, nên gán `buyer` chứ không gán `both`) nên `metadata_filter` chưa có gì để lọc. Cần thêm ít nhất một tài liệu `audience: seller` (hoặc tách trang gộp hai đối tượng) trước CP2.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `shopee-hoan-tien-ngay` | Định danh ổn định, trùng tên file; `delete_document` và bench dùng để nhóm các chunk về file gốc |
| `source_url` | string (URL) | `https://help.shopee.vn/portal/4/article/190387-...` | Truy vết câu trả lời về nguồn gốc |
| `retrieved_at` | date `YYYY-MM-DD` | `2026-09-20` | Kiểm tra độ mới của dữ liệu |
| `document_version` | string | `not-stated` | Ghi nhận phiên bản nguồn; `not-stated` khi nguồn không nêu, không bịa số hiệu |
| `audience` | `buyer` / `seller` / `both` | `buyer` | Lọc theo đối tượng khi câu hỏi không nêu rõ người hỏi (chỉ có tác dụng khi corpus có ≥ 2 giá trị) |
| `category` | string | `returns-policy` | Lọc theo loại chính sách |
| `language` | string | `vi` | Lọc theo ngôn ngữ |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

Chạy trên phần thân (đã bỏ frontmatter), `chunk_size=200`. `fixed_size` dùng overlap = 20 (`chunk_size // 10`), `by_sentences` dùng 3 câu/chunk.

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| `shopee-dong-goi-hang-hoan-tra` (3233 ký tự) | FixedSizeChunker (`fixed_size`) | 18 | 198.5 | Không: cắt giữa câu/giữa từ tại ranh giới cứng, dù có overlap |
| | SentenceChunker (`by_sentences`) | 8 | 401.5 | Khá: chunk trọn câu nhưng độ dài rất không đều (lớn nhất 870 ký tự) |
| | RecursiveChunker (`recursive`) | 22 | 145.0 | Tốt nhất: cắt theo đoạn/dòng trước nên giữ được từng ý |
| `shopee-quy-trinh-xu-ly-yeu-cau` (8023 ký tự) | FixedSizeChunker (`fixed_size`) | 45 | 197.8 | Không: cắt giữa câu, kể cả giữa hàng của bảng tiêu chí |
| | SentenceChunker (`by_sentences`) | 12 | 666.6 | Kém: chunk trung bình gấp ~3 lần `chunk_size`, gộp nhiều mục khác nhau |
| | RecursiveChunker (`recursive`) | 55 | 144.1 | Tốt: bám theo dòng/đoạn |
| `shopee-hoan-tien-ngay` (1059 ký tự) | FixedSizeChunker (`fixed_size`) | 6 | 193.2 | Không: cắt giữa câu |
| | SentenceChunker (`by_sentences`) | 1 | 1058.0 | Không tách được: cả bài thành 1 chunk (xem phân tích bên dưới) |
| | RecursiveChunker (`recursive`) | 7 | 149.6 | Tốt: mỗi bước/trường hợp là một chunk |
| `shopee-theo-doi-van-chuyen-hoan-tra` (685 ký tự) | FixedSizeChunker (`fixed_size`) | 4 | 186.2 | Không: cắt giữa câu |
| | SentenceChunker (`by_sentences`) | 2 | 341.5 | Trung bình: chunk lớn (tối đa 579 ký tự) |
| | RecursiveChunker (`recursive`) | 5 | 135.2 | Tốt |

> **Phát hiện từ baseline:** các bài Shopee viết theo dạng tiêu đề và bước ("Bước 1: ...", "Trường hợp 1: ...") và phần lớn dòng **không kết thúc bằng dấu `.`**. `SentenceChunker` chỉ cắt sau `.`/`!`/`?` nên không nhận ra những dòng này là câu riêng và dồn nhiều dòng vào một "câu" rất dài. Kết quả là chunk to, không đều, và trong `shopee-hoan-tien-ngay` cả bài thành đúng 1 chunk.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Nguyễn Đức Thịnh**
- **Loại chiến lược:** Sentence-Based Chunking (`SentenceChunker`, built-in, không custom).
- **Mô tả & lý do chọn cho chủ đề này:** Tách văn bản bằng `re.split(r"(?<=[.!?])\s+", text)` (giữ nguyên dấu câu) rồi gom `max_sentences_per_chunk` câu thành một chunk, mỗi chunk là một đơn vị trọn câu để giữ ngữ nghĩa. Số liệu baseline cho thấy điểm yếu với dữ liệu Shopee: các bài viết theo dạng tiêu đề/bước không có dấu chấm cuối dòng nên chunk to và không đều (xem phân tích ở trên). *(Phần lý do chọn ban đầu cần thành viên tự viết lại theo ý của mình.)*
- **Code snippet (nếu custom):** không có, dùng `SentenceChunker` trong `src/chunking.py`.

**Thành viên 2 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

**Thành viên 3 — [Tên]**
- **Loại chiến lược:**
- **Mô tả & lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên

| Thành viên | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------|----------|----------------------|-----------|----------|
| | | | | |
| | | | | |
| | | | | |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ & giải thích):*

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
| 5 | | | |

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).

| # | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
|---|---------|-------------------------------|-------------------------------|---------|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) & Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**
> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | / 10 |
| Thiết kế chiến lược (Strategy Design) | / 15 |
| Chất lượng truy xuất (Retrieval Quality) | / 10 |
| Thuyết trình (Demo) | / 5 |
| **Tổng phần nhóm** | **/ 40** |
