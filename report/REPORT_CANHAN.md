# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Đức Thịnh (MSSV 2A202602468)
**Nhóm:** [Tên nhóm]
**Ngày:** 2026-09-20

> **Nộp 1 bản / sinh viên.** Phần nhóm (lựa chọn tài liệu, thiết kế chiến lược, bộ câu hỏi đánh giá, demo) nộp chung 1 bản trong `REPORT_NHOM.md`. Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**
> Hai vector embedding chỉ về gần cùng một hướng, tức là hai đoạn văn bản có nghĩa gần nhau theo cách mô hình biểu diễn. Cosine đo góc giữa hai vector (từ -1 đến 1), không đo độ dài.

**Ví dụ có độ tương tự CAO:**
- Câu A: "Khách hàng được đổi trả sản phẩm trong 7 ngày."
- Câu B: "Người mua có thể trả hàng trong vòng một tuần."
- Tại sao tương đồng: hai câu khác từ vựng gần như hoàn toàn (khách hàng/người mua, đổi trả/trả hàng, 7 ngày/một tuần) nhưng cùng nghĩa. Điểm đo được bằng `text-embedding-3-small` là **0.59**, cao hơn hẳn cặp không liên quan bên dưới.

**Ví dụ có độ tương tự THẤP:**
- Câu A: "Khách hàng được đổi trả sản phẩm trong 7 ngày."
- Câu B: "Hôm nay trời nắng đẹp, thích hợp đi picnic."
- Tại sao khác: hai câu khác chủ đề hoàn toàn, không chung khái niệm nào. Điểm đo được là **0.27**.

**Tại sao độ tương tự cosine (cosine similarity) được ưu tiên hơn khoảng cách Euclid (Euclidean distance) cho text embeddings?**
> Cosine chỉ so hướng của vector nên không bị ảnh hưởng bởi độ dài vector, còn Euclid bị lệch khi hai vector cùng hướng nhưng khác độ lớn. Với embedding, thông tin ngữ nghĩa nằm ở hướng, nên cosine phản ánh đúng "giống nghĩa" hơn.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, chunk_size=500, overlap=50. Bao nhiêu chunks?**
> Phép tính: `step = chunk_size - overlap = 450`; `ceil((10000 - 50) / 450) = ceil(22.11) = 23`.
> Đáp án: **23 chunk**. Đã kiểm lại bằng `FixedSizeChunker(chunk_size=500, overlap=50).chunk("a" * 10000)` → 23.

**Nếu độ chồng chéo (overlap) tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn độ chồng chéo nhiều hơn?**
> Số chunk tăng lên **25** (`ceil(9900 / 400) = ceil(24.75)`, kiểm lại bằng code cũng ra 25), vì mỗi chunk chỉ tiến thêm 400 ký tự thay vì 450. Overlap lớn giúp một câu hay một thông tin nằm ngay ranh giới hai chunk vẫn xuất hiện trọn vẹn ở ít nhất một chunk, đổi lại tốn thêm chunk, chi phí embedding và có nội dung trùng lặp.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận của bạn khi lập trình (implement) các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk`** — hướng tiếp cận:
> Dùng `re.split(r"(?<=[.!?])\s+", text)`: lookbehind cắt *sau* dấu câu nên dấu `.`, `!`, `?` vẫn nằm lại trong câu (nếu dùng `[.!?]\s+` thì dấu câu bị nuốt). Sau đó strip từng câu, bỏ câu rỗng và gom mỗi `max_sentences_per_chunk` câu thành một chunk. Text rỗng hoặc toàn khoảng trắng trả `[]`.
> **Edge case chưa xử lý:** chữ viết tắt bị cắt sai. Đã kiểm: `"TS. Nguyễn Văn A giảng dạy."` bị tách thành `"TS."` và `"Nguyễn Văn A giảng dạy."`. Số thập phân như `3.5` thì không bị cắt vì sau dấu chấm không có khoảng trắng.

**`RecursiveChunker.chunk` / `_split`** — hướng tiếp cận:
> Thử separator theo thứ tự `["\n\n", "\n", ". ", " ", ""]`, cắt bằng ranh giới lớn trước. `_split` làm hai chiều: (1) đệ quy xuống, mảnh nào vẫn dài hơn `chunk_size` thì gọi lại với danh sách separator còn lại; (2) gom lên, các mảnh nhỏ liền kề được nối lại tới sát `chunk_size` để tránh chunk vụn. Separator được giữ lại ở cuối mảnh phía trước nên không mất chữ.
> **Base case:** (a) đoạn đã ngắn hơn hoặc bằng `chunk_size` thì trả về luôn; (b) hết separator (`separators=[]`) thì cắt cứng theo `chunk_size`; (c) separator là `""` thì cũng cắt cứng theo `chunk_size`. Thử với 30 dòng ngắn và `chunk_size=100` cho 3 chunk (98, 98, 88 ký tự), không ra chunk vụn.

### Lớp EmbeddingStore

**`add_documents` + `search`** — hướng tiếp cận:
> Bỏ hẳn nhánh ChromaDB, chỉ dùng list in-memory. `_make_record` chuẩn hóa mỗi `Document` thành record gồm `id`, `content`, `metadata` (copy, không dùng lại object của người gọi), `embedding` và luôn có `metadata["doc_id"]` (mặc định lấy `doc.id` nếu người gọi không đặt). `search` nhúng câu truy vấn rồi tính dot product với từng record; vì vector đã chuẩn hóa nên dot product bằng cosine. Kết quả sắp giảm dần theo `score`, cắt `top_k`, và bỏ `embedding` khỏi output.

**`search_with_filter` + `delete_document`** — hướng tiếp cận:
> `search_with_filter` lọc **trước** (giữ record có mọi cặp key/value trong `metadata_filter` khớp) rồi mới search trên tập đã lọc; nếu lọc sau top-k thì các slot có thể bị tài liệu sai chiếm hết và trả về 0 kết quả dù vẫn còn tài liệu hợp lệ. Cả `search` và `search_with_filter` đều đi qua `_search_records` nên không thể lệch nhau. `delete_document` giữ lại các record có `metadata["doc_id"]` khác `doc_id`, trả `True` nếu số record giảm.

### Tác tử KnowledgeBaseAgent

**`answer`** — hướng tiếp cận:
> Truy xuất top-k bằng `store.search`, sau đó dựng prompt gồm hướng dẫn, phần NGỮ CẢNH và câu hỏi. Mỗi chunk được đánh số `[1] [2] [3]` kèm nguồn (`source`, hoặc `doc_id`, hoặc `id`) và prompt yêu cầu trích dẫn số đoạn, nhờ đó truy vết được câu trả lời về đúng chunk. Prompt ràng buộc chỉ dùng ngữ cảnh, không có thì nói rõ là không tìm thấy. Nếu store không trả kết quả nào thì trả câu thông báo ngay, không gọi `llm_fn`.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

```
# Output của: pytest tests/ -v (rút gọn tiền tố tests/test_solution.py::)
TestProjectStructure::test_root_main_entrypoint_exists PASSED
TestProjectStructure::test_src_package_exists PASSED
TestClassBasedInterfaces::test_chunker_classes_exist PASSED
TestClassBasedInterfaces::test_mock_embedder_exists PASSED
TestFixedSizeChunker::test_chunks_respect_size PASSED
TestFixedSizeChunker::test_correct_number_of_chunks_no_overlap PASSED
TestFixedSizeChunker::test_empty_text_returns_empty_list PASSED
TestFixedSizeChunker::test_no_overlap_no_shared_content PASSED
TestFixedSizeChunker::test_overlap_creates_shared_content PASSED
TestFixedSizeChunker::test_returns_list PASSED
TestFixedSizeChunker::test_single_chunk_if_text_shorter PASSED
TestSentenceChunker::test_chunks_are_strings PASSED
TestSentenceChunker::test_respects_max_sentences PASSED
TestSentenceChunker::test_returns_list PASSED
TestSentenceChunker::test_single_sentence_max_gives_many_chunks PASSED
TestRecursiveChunker::test_chunks_within_size_when_possible PASSED
TestRecursiveChunker::test_empty_separators_falls_back_gracefully PASSED
TestRecursiveChunker::test_handles_double_newline_separator PASSED
TestRecursiveChunker::test_returns_list PASSED
TestEmbeddingStore::test_add_documents_increases_size PASSED
TestEmbeddingStore::test_add_more_increases_further PASSED
TestEmbeddingStore::test_initial_size_is_zero PASSED
TestEmbeddingStore::test_search_results_have_content_key PASSED
TestEmbeddingStore::test_search_results_have_score_key PASSED
TestEmbeddingStore::test_search_results_sorted_by_score_descending PASSED
TestEmbeddingStore::test_search_returns_at_most_top_k PASSED
TestEmbeddingStore::test_search_returns_list PASSED
TestKnowledgeBaseAgent::test_answer_non_empty PASSED
TestKnowledgeBaseAgent::test_answer_returns_string PASSED
TestComputeSimilarity::test_identical_vectors_return_1 PASSED
TestComputeSimilarity::test_opposite_vectors_return_minus_1 PASSED
TestComputeSimilarity::test_orthogonal_vectors_return_0 PASSED
TestComputeSimilarity::test_zero_vector_returns_0 PASSED
TestCompareChunkingStrategies::test_counts_are_positive PASSED
TestCompareChunkingStrategies::test_each_strategy_has_count_and_avg_length PASSED
TestCompareChunkingStrategies::test_returns_three_strategies PASSED
TestEmbeddingStoreSearchWithFilter::test_filter_by_department PASSED
TestEmbeddingStoreSearchWithFilter::test_no_filter_returns_all_candidates PASSED
TestEmbeddingStoreSearchWithFilter::test_returns_at_most_top_k PASSED
TestEmbeddingStoreDeleteDocument::test_delete_reduces_collection_size PASSED
TestEmbeddingStoreDeleteDocument::test_delete_returns_false_for_nonexistent_doc PASSED
TestEmbeddingStoreDeleteDocument::test_delete_returns_true_for_existing_doc PASSED
============================= 42 passed in 0.07s ==============================
```

**Số lượng bài test vượt qua (pass):** 42 / 42

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Dự đoán được ghi trước khi chạy `compute_similarity()`. Điểm thực tế đo bằng embedder thật `text-embedding-3-small` (OpenAI). Quy ước khi chấm: **cao** là từ 0.5 trở lên, **thấp** là dưới 0.4, khoảng 0.4–0.5 là trung bình.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|------|-----------|-----------|---------|--------------|-------|
| 1 | Khách hàng được đổi trả sản phẩm trong 7 ngày. | Người mua có thể trả hàng trong vòng một tuần. | cao | 0.5916 | Đúng |
| 2 | Khách hàng được đổi trả sản phẩm trong 7 ngày. | Hôm nay trời nắng đẹp, thích hợp đi picnic. | thấp | 0.2679 | Đúng |
| 3 | Người bán phải xử lý yêu cầu hoàn tiền trong 30 ngày. | Người mua được hoàn tiền trong 7 ngày. | cao | 0.6595 | Đúng |
| 4 | The cat sat on the mat. | Mèo ngồi trên tấm thảm. | cao | 0.4233 | Sai một phần (chỉ trung bình) |
| 5 | Sản phẩm được phép đổi trả. | Sản phẩm không được phép đổi trả. | cao | 0.8881 | Đúng (nhưng cao hơn tôi nghĩ) |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**
> Cặp 5 bất ngờ nhất: hai câu có nghĩa **ngược nhau** ("được phép" và "không được phép") lại có điểm cao nhất (0.89), cao hơn cả cặp đồng nghĩa ở cặp 1 (0.59). Embedding biểu diễn *chủ đề và từ vựng* nhiều hơn logic phủ định, nên với corpus chính sách, một truy vấn có thể lấy nhầm điều khoản trái ngược với điều khoản cần tìm. Cặp 4 (Anh–Việt cùng nghĩa) chỉ được 0.42, cho thấy khác ngôn ngữ vẫn làm điểm thấp hơn so với cùng ngôn ngữ.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Chạy **5 câu hỏi đánh giá của nhóm** trên mã nguồn cá nhân của bạn trong gói `src`. **5 câu hỏi này phải trùng với các thành viên cùng nhóm** (xem `REPORT_NHOM.md`).

> **CHƯA ĐIỀN.** Mục này cần 5 câu hỏi chung của nhóm và bộ tài liệu thật (chưa có; `data/ecommerce/` mới chỉ có 2 file mẫu dùng `https://example.com`) cùng `bench.py`. Điền sau CP5–CP6.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? (Relevant) | Câu trả lời của Agent (tóm tắt) |
|---|-------|--------------------------------|-------|-----------|------------------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| 4 | | | | | |
| 5 | | | | | |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** __ / 5

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác (qua demo):**
> *Điền sau buổi demo.*

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Khởi động (Warm-up) | / 5 |
| Hướng tiếp cận của tôi (My Approach) | / 10 |
| Hoàn thiện code (Core Implementation — tests) | / 30 |
| Dự đoán độ tương tự (Similarity Predictions) | / 5 |
| Kết quả truy xuất của tôi (Competition Results) | / 10 |
| **Tổng phần cá nhân** | **/ 60** |
