# Báo Cáo Nhóm — Lab 7: Embedding &amp; Vector Store

**Nhóm:** Studo.h (T114)
**Thành viên:** Văn Quốc Dũng
**Ngày:** 20/09/2026

> **Nộp 1 bản / nhóm.** Phần cá nhân (hướng tiếp cận, kết quả riêng, dự đoán…) mỗi thành viên nộp riêng trong `REPORT_CANHAN.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) &amp; Lý Do Chọn

**Chủ đề:** Chính sách Trả hàng/Hoàn tiền trên Shopee (help.shopee.vn) — đúng phạm vi K4-L3B (đổi trả / bảo hành / quy định người mua–người bán thương mại điện tử).

**Tại sao nhóm chọn chủ đề này?**

> Nhóm lấy bộ FAQ chính thức của Shopee vì đây là nguồn công khai, có cấu trúc mục/điều khoản, và chứa số liệu có thể kiểm chứng (thời hạn 15 ngày / 24 giờ, phản hồi 3–5 ngày làm việc, điều kiện “Đổi ý”, danh mục hạn chế trả hàng, phí hoàn trả, SPayLater). Các trang phủ trọn luồng người mua: điều kiện → bằng chứng → gửi yêu cầu → đóng gói/vận chuyển → theo dõi → nhận tiền hoàn, nên phù hợp để so sánh chunking và gắn metadata `audience`/`category`. Không dùng trang sau đăng nhập hay dữ liệu nội bộ.

**Cách thu thập:** Sao chép `scripts/urls.example.csv` thành `data/urls.csv` (11 URL Help Center), kiểm tra `https://help.shopee.vn/robots.txt` (`User-Agent: *` / `Allow: /`), rồi chạy crawler mẫu của repo:

```bash
python scripts/fetch_public_pages.py data/urls.csv --output-dir data/ecommerce --delay 1.0 --timeout 30 --overwrite
```

Kết quả crawl: **11 saved, 0 skipped**. Sau đó tách bài 188931 (`audience: both`) thành **2 file** `buyer` / `seller` theo `day7-lab-data-foundations.md`: nếu để chung một file thì `metadata_filter={"audience":"buyer"}` không lọc được vì hai đáp án nằm cùng tài liệu. Mỗi file `.md` UTF-8 có YAML front matter; kiểm kê tại `data/ecommerce/sources.csv`. User-Agent: `Day7DataFoundationsCourse/1.0 (+educational-lab)`. `document_version` để `not-stated` vì nguồn không nêu số hiệu phiên bản.

### Danh sách tài liệu (Data Inventory)

Corpus dùng cho benchmark: **12 file** trong `data/ecommerce/` (11 URL Help Center; bài 188931 tách thành 2 audience). Không tính 2 file khởi động `return-refund-policy.md` / `seller-warranty-policy.md` vì vẫn là template `example.com`. Số ký tự = phần nội dung sau front matter.


| #   | Tên tài liệu                                                     | Nguồn (Source URL)                                                                               | Ngày lấy / Phiên bản    | Số ký tự | Metadata đã gán                                                                                                |
| --- | ---------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------- | -------- | -------------------------------------------------------------------------------------------------------------- |
| 1   | Những điều cần biết về Trả hàng do Đổi ý/không còn nhu cầu       | [https://help.shopee.vn/portal/4/article/204305](https://help.shopee.vn/portal/4/article/204305) | 2026-09-20 / not-stated | 7371     | `doc_id=doi-y-khong-con-nhu-cau`; `audience=buyer`; `category=returns-policy`; `language=vi`                   |
| 2a  | Quy định Trả hàng/Hoàn tiền dành cho Người mua                   | [https://help.shopee.vn/portal/4/article/188931](https://help.shopee.vn/portal/4/article/188931) | 2026-09-20 / not-stated | 5886     | `doc_id=quy-dinh-chung-tra-hang-hoan-tien-buyer`; `audience=buyer`; `category=returns-policy`; `language=vi`   |
| 2b  | Quy định Trả hàng/Hoàn tiền dành cho Người bán                   | [https://help.shopee.vn/portal/4/article/188931](https://help.shopee.vn/portal/4/article/188931) | 2026-09-20 / not-stated | 1472     | `doc_id=quy-dinh-chung-tra-hang-hoan-tien-seller`; `audience=seller`; `category=returns-policy`; `language=vi` |
| 3   | Sản phẩm hạn chế trả hàng là gì                                  | [https://help.shopee.vn/portal/4/article/79465](https://help.shopee.vn/portal/4/article/79465)   | 2026-09-20 / not-stated | 1463     | `doc_id=san-pham-han-che-tra-hang`; `audience=buyer`; `category=restricted-returns`; `language=vi`             |
| 4   | Hướng dẫn chuẩn bị bằng chứng khi yêu cầu Trả hàng/Hoàn tiền     | [https://help.shopee.vn/portal/4/article/79467](https://help.shopee.vn/portal/4/article/79467)   | 2026-09-20 / not-stated | 3469     | `doc_id=chuan-bi-bang-chung-tra-hang`; `audience=buyer`; `category=return-evidence`; `language=vi`             |
| 5   | Hướng dẫn gửi yêu cầu Trả hàng/Hoàn tiền                         | [https://help.shopee.vn/portal/4/article/79233](https://help.shopee.vn/portal/4/article/79233)   | 2026-09-20 / not-stated | 2518     | `doc_id=gui-yeu-cau-tra-hang-hoan-tien`; `audience=buyer`; `category=return-request`; `language=vi`            |
| 6   | Các phương thức gửi hàng hoàn trả và phí hoàn trả                | [https://help.shopee.vn/portal/4/article/189477](https://help.shopee.vn/portal/4/article/189477) | 2026-09-20 / not-stated | 5930     | `doc_id=phuong-thuc-phi-gui-hang-hoan-tra`; `audience=buyer`; `category=return-shipping`; `language=vi`        |
| 7   | Cách đóng gói đơn hàng hoàn trả                                  | [https://help.shopee.vn/portal/4/article/79508](https://help.shopee.vn/portal/4/article/79508)   | 2026-09-20 / not-stated | 3618     | `doc_id=dong-goi-don-hang-hoan-tra`; `audience=buyer`; `category=return-packaging`; `language=vi`              |
| 8   | Cách theo dõi tình trạng vận chuyển hàng hoàn trả                | [https://help.shopee.vn/portal/4/article/189476](https://help.shopee.vn/portal/4/article/189476) | 2026-09-20 / not-stated | 975      | `doc_id=theo-doi-van-chuyen-hang-hoan-tra`; `audience=buyer`; `category=return-tracking`; `language=vi`        |
| 9   | Hướng dẫn Người mua trả lời đề xuất Hoàn Tiền Ngay của Người bán | [https://help.shopee.vn/portal/4/article/190387](https://help.shopee.vn/portal/4/article/190387) | 2026-09-20 / not-stated | 1360     | `doc_id=tra-loi-de-xuat-hoan-tien-ngay`; `audience=buyer`; `category=instant-refund`; `language=vi`            |
| 10  | Làm sao để kiểm tra tiền đã hoàn vào SPayLater hay chưa          | [https://help.shopee.vn/portal/4/article/164831](https://help.shopee.vn/portal/4/article/164831) | 2026-09-20 / not-stated | 5933     | `doc_id=kiem-tra-hoan-tien-spaylater`; `audience=buyer`; `category=refund-spaylater`; `language=vi`            |
| 11  | Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn              | [https://help.shopee.vn/portal/4/article/189473](https://help.shopee.vn/portal/4/article/189473) | 2026-09-20 / not-stated | 3898     | `doc_id=thoi-gian-nhan-tien-hoan`; `audience=buyer`; `category=refund-timeline`; `language=vi`                 |


**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ. (`robots.txt` cho phép; không đăng nhập; không CAPTCHA; chỉ HTML Help Center.)
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata. (`retrieved_at=2026-09-20`; `document_version=not-stated`; khớp 1-1 với `data/ecommerce/sources.csv`.)

**Ghi chú cho retrieval:** `audience` có 2 giá trị (`buyer` / `seller`). File buyer giữ thời hạn gửi yêu cầu (24 giờ / 15 ngày / 20 ngày) và hoàn mã Shopee/Xu; file seller giữ Shop Voucher **không được Shopee hoàn** và quyết định hàng hạn chế trả. Cùng nguồn 188931 nhưng đáp án khác nhau — `metadata_filter={"audience": "buyer"}` (hoặc `"seller"`) mới tách được. Không bịa thời hạn xử lý 30 ngày cho seller vì nguồn không nêu. `category` tách các bước trong luồng trả hàng (policy, evidence, shipping, refund).

### Cấu trúc Metadata (Metadata Schema)


| Trường metadata    | Kiểu              | Ví dụ giá trị                                           | Tại sao hữu ích cho truy xuất (retrieval)?                                                                                                                                                   |
| ------------------ | ----------------- | ------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `doc_id`           | string (slug)     | `quy-dinh-chung-tra-hang-hoan-tien-buyer`               | Định danh ổn định khi ingest / `delete_document()`; trùng tên file.                                                                                                                          |
| `title`            | string            | `Thời gian nhận tiền hoàn và cách kiểm tra tiền hoàn`   | Giúp người đọc/agent nhận đúng văn bản nguồn khi trích dẫn.                                                                                                                                  |
| `source_url`       | URL               | `https://help.shopee.vn/portal/4/article/188931`        | Truy vết gold answer về đúng trang Shopee, không dùng link tìm kiếm.                                                                                                                         |
| `retrieved_at`     | date `YYYY-MM-DD` | `2026-09-20`                                            | Kiểm tra độ mới của corpus khi chính sách Help Center đổi.                                                                                                                                   |
| `document_version` | string            | `not-stated`                                            | Chừa chỗ cho ngày hiệu lực; không bịa số hiệu nếu nguồn không nêu.                                                                                                                           |
| `audience`         | enum              | `buyer` | `seller`                                      | Lọc đúng đối tượng. Câu benchmark không nêu người hỏi cần `metadata_filter={"audience": "buyer"}` (hoặc `"seller"`) kẻo lẫn thời hạn 15 ngày của buyer với quy định Shop Voucher của seller. |
| `category`         | string            | `returns-policy`, `return-evidence`, `refund-spaylater` | Lọc theo bước quy trình (điều kiện / bằng chứng / vận chuyển / hoàn tiền) khi câu hỏi cùng chủ đề “trả hàng”.                                                                                |
| `language`         | string            | `vi`                                                    | Đánh dấu corpus tiếng Việt; tránh lẫn tài liệu mẫu tiếng Anh trong `data/`.                                                                                                                  |


---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

> Mỗi thành viên thử **một chiến lược khác nhau** trên cùng bộ tài liệu; nhóm tổng hợp và so sánh ở đây.

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:


| Tài liệu | Chiến lược (Strategy)            | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?                               |
| -------- | -------------------------------- | -------------- | ----------------- | ------------------------------------------------------ |
| 12 tài liệu trong `data/ecommerce/` | FixedSizeChunker (`fixed_size`) | 98 | 477,97 ký tự/chunk | Không giữ được ngữ cảnh, đôi lúc cắt ngang câu trả lời |
|          | SentenceChunker (`by_sentences`, 3 câu/chunk) | 80 | 529,10 ký tự/chunk | Giữ trọn câu nhưng chunk to và không đều (min 51 / max 2.361); 5 chunk >1.000 ký tự nuốt cả bảng/danh sách nên loãng ngữ cảnh |
|          | RecursiveChunker (`recursive`)   |                |                   |                                                        |


Kết quả FixedSize: `chunk_size=500`, `overlap=50`, chạy trên phần nội dung sau YAML front matter và bỏ khoảng trắng ở đầu/cuối. Tổng 42.541 ký tự nội dung tạo 98 chunk; độ dài trung bình = tổng độ dài các chunk / 98 = **477,97 ký tự** (tính cả phần overlap). Chunk cuối mỗi tài liệu thường ngắn hơn 500 ký tự nên trung bình thấp hơn kích thước tối đa.

### Chiến lược của từng thành viên

> Mỗi thành viên điền một khối dưới đây (copy thêm nếu nhóm có nhiều hơn 3 người).

**Thành viên 1 — Văn Quốc Dũng**

- **Loại chiến lược:** FixedSize (`FixedSizeChunker`, `chunk_size=500`, `overlap=50`)
- **Mô tả &amp; lý do chọn cho chủ đề này:** Làm baseline để so sánh retrieval với Sentence/Recursive/heading của thành viên khác là công bằng. 
- **Code snippet (nếu custom):** Không custom — dùng `FixedSizeChunker` có sẵn trong `src/chunking.py`:

```python
from src.chunking import FixedSizeChunker

chunker = FixedSizeChunker(chunk_size=500, overlap=50)
chunks = chunker.chunk(body)  # body = phần markdown sau front matter
```

**Thành viên 2 — [Nguyễn Đức Thịnh]**

- **Loại chiến lược:** Sentence-Based Chunking (`SentenceChunker`, built-in, không custom).
- **Mô tả &amp; lý do chọn cho chủ đề này:** Tách văn bản bằng `re.split(r"(?<=[.!?])\s+", text)` (giữ nguyên dấu câu) rồi gom `max_sentences_per_chunk = 3` câu thành một chunk, nên không bao giờ cắt ngang câu như FixedSize. Nhóm chọn chiến lược này vì đáp án của bộ Shopee thường là một câu quy định trọn vẹn (“Shop Voucher … sẽ không được hoàn lại trong bất cứ trường hợp nào”, “Hình ảnh: Không quá 5MB/ảnh”), nên ranh giới câu là ranh giới ngữ nghĩa tự nhiên.
- **Số liệu thực đo trên corpus 12 file (`data/ecommerce/`, 42.541 ký tự):**


| Cấu hình | Số chunk | Độ dài TB | Min / Max | Chunk >1.000 ký tự | Chunk <50 ký tự |
| -------- | -------- | --------- | --------- | ------------------ | --------------- |
| `SentenceChunker(1)` | 229 | 184,19 | 2 / 2.093 | 2 | 38 |
| `SentenceChunker(2)` | 117 | 361,46 | 49 / 2.102 | 5 | 1 |
| **`SentenceChunker(3)` (dùng)** | **80** | **529,10** | **51 / 2.361** | **5** | **0** |
| `SentenceChunker(5)` | 51 | 830,53 | 51 / 2.652 | 13 | 0 |

  Điểm yếu lớn nhất với dữ liệu Shopee: bảng và danh sách gạch đầu dòng bị crawl thành các dòng ngắn **không có dấu chấm cuối dòng**, nên regex không thấy ranh giới câu và cả bảng dính thành một “câu” dài (max 2.361 ký tự, vượt xa mức 500 của FixedSize/Recursive). Ngược lại `n=1` sinh 38 chunk dưới 50 ký tự (tiêu đề, dòng “Bước 1/2/3”) nên vụn. `n=3` là điểm cân bằng: không còn chunk vụn, trung bình 529 ký tự gần với 500 của hai chiến lược còn lại nên so sánh công bằng.
- **Code snippet (nếu custom):** Không custom — dùng `SentenceChunker` có sẵn trong `src/chunking.py`:

```python
from src.chunking import SentenceChunker

CHUNKER = SentenceChunker(max_sentences_per_chunk=3)
chunks = CHUNKER.chunk(body)  # body = phần markdown sau front matter
```

- **Kết quả benchmark (embedding thật `text-embedding-3-small`, `top_k=3`, `EmbeddingStore` in-memory, câu 2 dùng `metadata_filter={"audience": "seller"}`):** **5/10**. Chunk “đúng” = chunk thuộc tài liệu gold **và** chứa số liệu/câu trả lời (không chỉ đúng tài liệu).


| # | Kết quả | Hạng chunk gold tốt nhất | Nhận xét |
| - | ------- | ------------------------ | -------- |
| 1 | 0/2 | 11 | Câu multi-hop (cần 2 tài liệu). Top-3 toàn chunk `doi-y-khong-con-nhu-cau` / `phuong-thuc-phi-gui-hang-hoan-tra` vì trùng từ “đổi ý”; chunk mốc 24 giờ và chunk “không áp dụng lý do Đổi ý” đều nằm ngoài top-3. |
| 2 | 2/2 | 1 | Chunk Shop Voucher (246 ký tự) đứng đầu, score 0,718. Filter `seller` loại chunk buyer (hạng 2 khi không lọc, score 0,667) nên top-3 chỉ còn nội dung người bán. |
| 3 | 2/2 | 1 | Chunk “40,000 Shopee Xu” đứng đầu (score 0,746), nhưng dài 951 ký tự do dính cả đoạn phụ. |
| 4 | 0/2 | 28 | Top-2 là đúng tài liệu `chuan-bi-bang-chung-tra-hang` nhưng là chunk đầu bài (không chứa “5MB”); câu “Hình ảnh: Không quá 5MB/ảnh” nằm trong chunk khác, hạng 28/80. |
| 5 | 1/2 | 3 | Chunk gold (1.839 ký tự — cả bảng dính thành một chunk) xếp hạng 3, sát nút hai chunk cùng tài liệu (0,715 / 0,714 / 0,710); có đáp án nhưng không ở top-1. |

  **Kết luận cá nhân:** Sentence chunking thắng ở câu chứa một câu quy định rõ ràng (câu 2, 3) và thua ở câu multi-hop (1) và câu có đáp án nằm giữa danh sách/bảng (4, 5), đúng với điểm yếu regex nêu ở trên. Lưu ý: embedding của mình là OpenAI, còn benchmark của Khánh dùng Gemini, nên điểm giữa hai thành viên chưa so sánh tuyệt đối được.

**Thành viên 3 — Lương Sỹ Khánh**

- **Loại chiến lược:** Recursive (`RecursiveChunker`, `chunk_size=500`, separators mặc định `["\n\n", "\n", ". ", " ", ""]`)
- **Mô tả &amp; lý do chọn cho chủ đề này:** Cắt ở ranh giới "to" trước — `\n\n` là ranh giới giữa các mục của bài Help Center — nên mỗi chunk thường trọn một mục (`1.2. Thời gian tối đa...`, `2.2. Phí vận chuyển trả hàng`), chỉ khi mảnh vẫn quá 500 ký tự mới hạ xuống `\n` rồi `". "`. Chọn cho chủ đề này vì corpus Shopee là văn bản quy định phân mục rõ, đáp án luôn nằm gọn trong một mục; cắt cứng theo độ dài sẽ chẻ đôi bảng thời hạn 24 giờ / 15 ngày / 20 ngày. Bước **gom lên** quan trọng không kém bước đệ quy xuống: các file này đầy dòng ngắn (bullet, "Bước 1/2/3"), không gom thì sinh hàng trăm chunk vụn 5–10 ký tự và retrieval hỏng hẳn.
- **Số liệu thực đo trên corpus 12 file:** 107 chunk, độ dài min 50 / max 496 / **trung bình 396 ký tự** — sát trần 500, tức bước gom hoạt động đúng.
- **Code snippet (nếu custom):** Không custom class, nhưng phần `_split` / `_merge` trong `src/chunking.py` là tự viết (starter chỉ có `NotImplementedError`):

```python
def _split(self, current_text: str, remaining_separators: list[str]) -> list[str]:
    text = current_text
    if not text:
        return []
    if len(text) <= self.chunk_size:              # base case 1: đã vừa
        return [text]
    if not remaining_separators or remaining_separators[0] == "":
        return self._hard_split(text)             # base case 2: hết separator
    separator, rest = remaining_separators[0], remaining_separators[1:]
    parts = [p for p in text.split(separator) if p]
    if len(parts) <= 1:                           # base case 3: separator vắng mặt
        return self._split(text, rest)
    pieces = []
    for part in parts:                            # đệ quy xuống
        if len(part) <= self.chunk_size:
            pieces.append(part)
        else:
            pieces.extend(self._split(part, rest))
    return self._merge(pieces, separator)         # gom lên sát chunk_size
```

Cấu hình dùng trong `bench.py` (dòng duy nhất mỗi thành viên đổi):

```python
CHUNKER = RecursiveChunker(chunk_size=500)
```

- **Kết quả benchmark (embedding thật `gemini-embedding-001`, `top_k=3`):** **6/10** — câu 2, 3, 4 đạt 2/2 (gold ở top-1 và ngữ cảnh chứa đáp án); câu 1 và câu 5 được 0/2. Chi tiết phân tích lỗi ở mục 3.

**Thành viên 4 — [Tên]**

- **Loại chiến lược:**
- **Mô tả &amp; lý do chọn:**
- **Code snippet (nếu custom):**

### So Sánh Giữa Các Thành Viên


| Thành viên         | Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
| ------------------ | --------------------- | -------------------- | --------- | -------- |
| Văn Quốc Dũng      | FixedSize (500/50)    |                      |           |          |
| Nguyễn Đức Thịnh   | Sentence (3 câu/chunk) | **5/10** | Không cắt ngang câu; câu quy định ngắn, rõ (Shop Voucher, phí 40.000 Xu) lên top-1 (câu 2, 3). Filter `audience=seller` loại chunk buyer khỏi top-3 ở câu 2. | Bảng/danh sách không có dấu chấm nên dính thành chunk tới 2.361 ký tự (5 chunk >1.000), làm loãng ngữ cảnh; câu 1 (multi-hop) và câu 4 (“5MB” hạng 28/80) trượt khỏi top-3. |
| Lương Sỹ Khánh     | Recursive (500)       | **6/10**              | Giữ trọn mục quy định nên 3/5 câu đạt top-1 kèm đủ số liệu (40.000 Xu, 5MB/100MB, Shop Voucher); chunk đều (avg 396/500), không có mảnh vụn. | Bảng bị crawl thành text phẳng thì cắt ở `\n\n` sinh chunk toàn số liệu mất tiêu đề cột — câu 5 vì vậy rơi xuống hạng 15/107. Câu multi-hop (câu 1) không ăn được vì 2 chunk cùng một tài liệu chiếm hết top-3. |
| Đào Quang Thái Anh | Semantic Chunking     |                      |           |          |


**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**

> *Viết 2-3 câu — đây là phần được đánh giá cao nhất (khả năng suy nghĩ &amp; giải thích):*

---

## 3. Câu hỏi đánh giá &amp; Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá &amp; Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.


| #   | Câu hỏi (Query)                                                                                                                                                       | Câu trả lời chuẩn (Gold Answer)                                                                                                                                                                                                                                                                                                                                                       | Chunk nào chứa thông tin?                                                                                                                                                                                                                   |
| --- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | Đơn hàng thực phẩm đông lạnh đã giao thành công 2 ngày trước, tôi đổi ý không muốn dùng nữa thì trả hàng được không?                                                  | **Không.** Hai lý do: (a) với đơn thực phẩm tươi sống &amp; đông lạnh, thời hạn gửi yêu cầu Trả hàng/Hoàn tiền chỉ **24 giờ** kể từ khi đơn cập nhật ‘Giao hàng thành công’ (trừ lý do Chưa nhận được hàng) — đã quá hạn; (b) thực phẩm tươi sống/đông lạnh thuộc **danh sách hạn chế trả hàng**, Shopee **không áp dụng** lý do “Đổi ý (Sản phẩm còn nguyên tem, nhãn mác, bao bì)”. | Đa tài liệu: `quy-dinh-chung-tra-hang-hoan-tien-buyer` §1.2 (mốc 24 giờ) + `san-pham-han-che-tra-hang` (nhóm “Thực phẩm &amp; Hàng mau hỏng”, câu “không áp dụng lý do Đổi ý”)                                                              |
| 2   | **(cần lọc metadata)** Shop Voucher do Người bán phát hành có được hoàn lại khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận không?                                      | **Không.** Shop Voucher (mã do Người bán phát hành) và Mã miễn phí vận chuyển **không được hoàn lại trong bất cứ trường hợp nào**. Người mua có thể tự liên hệ Người bán; việc hoàn (nếu có) là thỏa thuận giữa hai bên, Shopee không hoàn tự động. Khác với Mã giảm giá do Shopee phát hành (có thể được hoàn theo quy định riêng, trong vòng 48 giờ không kể T7/CN/lễ).             | `quy-dinh-chung-tra-hang-hoan-tien-seller` §3 + §4. Cần `metadata_filter={"audience": "seller"}`: file buyer cùng `source_url` 188931 có bảng “Hoàn lại Mã giảm giá/Shopee Xu” nói **mã giảm giá sẽ được hoàn**, dễ bị lấy nhầm làm đáp án. |
| 3   | Tôi trả hàng bằng hình thức “Tự sắp xếp”, đơn không thuộc Shopee Mall, địa chỉ của tôi khác tỉnh với Người bán — được hỗ trợ phí trả hàng bao nhiêu và trong bao lâu? | Được hoàn **40.000 Shopee Xu** (cùng tỉnh/thành phố thì 25.000 Xu), trong vòng **3–5 ngày làm việc** (không kể Thứ 7, Chủ nhật, Ngày lễ &amp; Tết) sau khi yêu cầu được chấp nhận hoàn tiền và đáp ứng đủ điều kiện hỗ trợ phí trả hàng. Đơn thuộc Shopee Mall thì Shopee hoàn lại khoản phí này (không phải dưới dạng Xu).                                                           | `phuong-thuc-phi-gui-hang-hoan-tra` §2.2 “Phí vận chuyển trả hàng”                                                                                                                                                                          |
| 4   | Khi gửi bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, ảnh và video được phép dung lượng tối đa bao nhiêu, và nếu Shopee yêu cầu bổ sung thì tôi có bao lâu?              | Hình ảnh **tối đa 5MB/ảnh**; video **tối đa 100MB/video và tối đa 1 phút**. File lớn hơn thì tải lên YouTube/Google Drive ở chế độ công khai rồi gửi đường dẫn trong phần chú thích. Nếu Shopee cần thêm bằng chứng, phải bổ sung **trong vòng 24 giờ**, sau đó Shopee chỉ xem xét trên bằng chứng đã có.                                                                             | `chuan-bi-bang-chung-tra-hang` §4 “Quy định về bằng chứng”                                                                                                                                                                                  |
| 5   | Đơn hàng thanh toán bằng thẻ tín dụng thì bao lâu nhận được tiền hoàn, so với Ví ShopeePay?                                                                           | Thẻ tín dụng/ghi nợ (kể cả qua Apple Pay / Google Pay): **7–14 ngày làm việc** tùy ngân hàng, hoàn về đúng thẻ đã thanh toán. Ví ShopeePay: **24 giờ** (với điều kiện ví hoạt động bình thường). Mốc thời gian tính từ khi Shopee chấp nhận hoàn tiền.                                                                                                                                | `thoi-gian-nhan-tien-hoan` — Bảng 1 “Phương thức hoàn tiền và thời gian hoàn tiền” (các dòng Thẻ tín dụng/ghi nợ, Ví ShopeePay)                                                                                                             |


**Ghi chú thiết kế bộ câu hỏi:** 5 câu phủ 5 bước khác nhau của luồng (điều kiện → quy định người bán → phí trả hàng → bằng chứng → nhận tiền hoàn) và 4 dạng truy xuất khác nhau: **đa tài liệu** (1), **cần lọc metadata** (2), **số liệu có điều kiện** (3), **giới hạn kỹ thuật** (4), **tra bảng** (5). Mọi gold answer đều trích được nguyên văn từ `data/ecommerce/`, không câu nào cần suy diễn ngoài nguồn.

### Tổng hợp chất lượng truy xuất của nhóm

> Cách chấm (theo `docs/SCORING.md`): **2 điểm/câu** — top-3 chứa chunk liên quan + agent trả lời đúng (2), có liên quan nhưng thiếu/không ở top-1 (1), không có trong top-3 (0).


| #   | Câu hỏi | Chiến lược tốt nhất cho câu này | Có chunk liên quan trong top-3? | Ghi chú |
| --- | ------- | ------------------------------- | ------------------------------- | ------- |
| 1   |         |                                 |                                 |         |
| 2   |         |                                 |                                 |         |
| 3   |         |                                 |                                 |         |
| 4   |         |                                 |                                 |         |
| 5   |         |                                 |                                 |         |


**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**

> *Viết 2-3 câu:*

---

## 4. Thuyết trình (Demo) &amp; Bài học nhóm — Nhóm (5 điểm)

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**

> *Liệt kê 2-3 ý:*

**Bài học rút ra khi so sánh trong nhóm:**

> *Viết 2-3 câu — cùng tài liệu nhưng chiến lược khác nhau dẫn tới khác biệt gì?*

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**

> *Viết 2-3 câu:*

---

## Tự Đánh Giá (Phần Nhóm)


| Tiêu chí                                 | Điểm tự đánh giá |
| ---------------------------------------- | ---------------- |
| Lựa chọn tài liệu (Document Set Quality) | / 10             |
| Thiết kế chiến lược (Strategy Design)    | / 15             |
| Chất lượng truy xuất (Retrieval Quality) | / 10             |
| Thuyết trình (Demo)                      | / 5              |
| **Tổng phần nhóm**                       | **/ 40**         |

