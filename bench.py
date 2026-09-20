"""Benchmark 5 câu hỏi của nhóm trên corpus Shopee (data/ecommerce).

Chạy:  python bench.py            # có gọi LLM để agent trả lời (cần OPENAI_API_KEY)
       python bench.py --no-llm   # chỉ đo truy xuất
       USE_CHROMA=1 python bench.py   # dùng backend ChromaDB thay vì in-memory

Kết quả được in ra màn hình và ghi vào ket_qua_benchmark.txt.
Mỗi thành viên chỉ đổi đúng dòng CHUNKER bên dưới.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

from src.agent import KnowledgeBaseAgent
from src.chunking import SentenceChunker
from src.embeddings import OPENAI_EMBEDDING_MODEL, OpenAIEmbedder, _mock_embed
from src.models import Document
from src.store import EmbeddingStore

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data" / "ecommerce"
CACHE_FILE = ROOT / ".bench_cache" / "embeddings.json"
OUTPUT_FILE = ROOT / "ket_qua_benchmark.txt"
TOP_K = 3

# ---- Dòng duy nhất mỗi thành viên đổi -------------------------------------
CHUNKER = SentenceChunker(max_sentences_per_chunk=3)
# ----------------------------------------------------------------------------

# (câu hỏi, metadata_filter, [(doc_id gold, chuỗi đặc trưng phải có trong chunk)])
QUERIES = [
    (
        "Đơn hàng thực phẩm đông lạnh đã giao thành công 2 ngày trước, tôi đổi ý không muốn dùng nữa thì trả hàng được không?",
        None,
        [
            ("quy-dinh-chung-tra-hang-hoan-tien-buyer", "tươi sống & đông lạnh"),
            ("san-pham-han-che-tra-hang", "không áp dụng lý do"),
        ],
    ),
    (
        "Shop Voucher do Người bán phát hành có được hoàn lại khi yêu cầu Trả hàng/Hoàn tiền được chấp nhận không?",
        {"audience": "seller"},
        [("quy-dinh-chung-tra-hang-hoan-tien-seller", "không được hoàn lại trong bất cứ trường hợp nào")],
    ),
    (
        "Tôi trả hàng bằng hình thức “Tự sắp xếp”, đơn không thuộc Shopee Mall, địa chỉ của tôi khác tỉnh với Người bán — được hỗ trợ phí trả hàng bao nhiêu và trong bao lâu?",
        None,
        [("phuong-thuc-phi-gui-hang-hoan-tra", "40,000 Shopee Xu")],
    ),
    (
        "Khi gửi bằng chứng cho yêu cầu Trả hàng/Hoàn tiền, ảnh và video được phép dung lượng tối đa bao nhiêu, và nếu Shopee yêu cầu bổ sung thì tôi có bao lâu?",
        None,
        [("chuan-bi-bang-chung-tra-hang", "5MB/ảnh")],
    ),
    (
        "Đơn hàng thanh toán bằng thẻ tín dụng thì bao lâu nhận được tiền hoàn, so với Ví ShopeePay?",
        None,
        [("thoi-gian-nhan-tien-hoan", "7 - 14 ngày làm việc")],
    ),
]


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for s in self.streams:
            s.write(text)

    def flush(self):
        for s in self.streams:
            s.flush()


class CachedEmbedder:
    """Cache embedding theo hash nội dung để chạy lại không tốn thêm tiền."""

    def __init__(self, inner, name: str) -> None:
        self.inner = inner
        self.name = name
        self._backend_name = getattr(inner, "_backend_name", name)
        self.hits = 0
        self.calls = 0
        try:
            self.cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            self.cache = {}

    def __call__(self, text: str) -> list[float]:
        key = hashlib.sha256(f"{self.name}\n{text}".encode()).hexdigest()
        if key in self.cache:
            self.hits += 1
            return self.cache[key]
        self.calls += 1
        self.cache[key] = self.inner(text)
        return self.cache[key]

    def save(self) -> None:
        CACHE_FILE.parent.mkdir(exist_ok=True)
        CACHE_FILE.write_text(json.dumps(self.cache), encoding="utf-8")


def parse_front_matter(text: str) -> tuple[dict, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not match:
        return {}, text.strip()
    meta = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, text[match.end():].strip()


def load_documents() -> list[Document]:
    docs: list[Document] = []
    for path in sorted(DATA_DIR.glob("*.md")):
        meta, body = parse_front_matter(path.read_text(encoding="utf-8"))
        if "example.com" in meta.get("source_url", ""):
            continue  # file template khởi động, không thuộc corpus
        # Chunk NGOÀI store: mỗi chunk là một Document riêng, mang đủ metadata.
        for i, chunk in enumerate(CHUNKER.chunk(body)):
            docs.append(
                Document(
                    id=f"{path.stem}#{i}",
                    content=chunk,
                    metadata={**meta, "doc_id": path.stem, "chunk_index": i},
                )
            )
    return docs


def make_embedder():
    provider = os.getenv("EMBEDDING_PROVIDER", "mock").strip().lower()
    if provider == "openai":
        return CachedEmbedder(OpenAIEmbedder(), OPENAI_EMBEDDING_MODEL)
    print(f"!! EMBEDDING_PROVIDER={provider!r}: dùng mock embedding, số liệu bị chi phối bởi mock.")
    return CachedEmbedder(_mock_embed, "mock")


def make_llm():
    from openai import OpenAI

    client = OpenAI()

    def llm(prompt: str) -> str:
        r = client.chat.completions.create(
            model="gpt-4o-mini", temperature=0, messages=[{"role": "user", "content": prompt}]
        )
        return r.choices[0].message.content

    return llm


def is_gold(record: dict, golds: list[tuple[str, str]]) -> bool:
    return any(
        record["metadata"].get("doc_id") == doc_id and marker in record["content"] for doc_id, marker in golds
    )


def grade(ranked: list[dict], golds: list[tuple[str, str]]) -> tuple[int, int | None, bool]:
    """Trả (điểm 0-2, hạng tốt nhất của chunk gold trên toàn bộ xếp hạng, có đúng doc_id trong top-3)."""
    best = next((i for i, r in enumerate(ranked, 1) if is_gold(r, golds)), None)
    doc_hit = any(r["metadata"].get("doc_id") in {d for d, _ in golds} for r in ranked[:TOP_K])
    points = 2 if best == 1 else 1 if best is not None and best <= TOP_K else 0
    return points, best, doc_hit


def show_top(label: str, results: list[dict], golds: list[tuple[str, str]]) -> None:
    print(f"  {label}")
    for i, r in enumerate(results, 1):
        flag = "GOLD" if is_gold(r, golds) else "    "
        head = r["content"][:70].replace("\n", " ")
        print(f"    #{i} {r['score']:.4f} {flag} {r['metadata']['doc_id']} ({len(r['content'])} ký tự) | {head}")


def main() -> int:
    load_dotenv(ROOT / ".env")
    use_llm = "--no-llm" not in sys.argv
    with open(OUTPUT_FILE, "w", encoding="utf-8") as fh:
        sys.stdout = Tee(sys.__stdout__, fh)
        try:
            return run(use_llm)
        finally:
            sys.stdout = sys.__stdout__


def run(use_llm: bool) -> int:
    docs = load_documents()
    embedder = make_embedder()
    use_chroma = os.getenv("USE_CHROMA") == "1"
    store = EmbeddingStore(collection_name="bench_store", embedding_fn=embedder, use_chroma=use_chroma)
    store.add_documents(docs)
    embedder.save()

    n_files = len({d.metadata["doc_id"] for d in docs})
    print(f"Chunker: {CHUNKER.__class__.__name__} {vars(CHUNKER)}")
    print(f"Embedding: {embedder._backend_name} | backend: {'ChromaDB' if use_chroma else 'in-memory'}")
    print(f"Đã nạp {len(docs)} chunk từ {n_files} file (embedding: {embedder.calls} gọi API, {embedder.hits} từ cache)")

    agent = KnowledgeBaseAgent(store, make_llm()) if use_llm and os.getenv("OPENAI_API_KEY") else None
    total = 0
    for n, (query, meta_filter, golds) in enumerate(QUERIES, 1):
        print(f"\n=== Câu {n}: {query}")
        print(f"  gold: {golds}")
        search = lambda k: (
            store.search_with_filter(query, top_k=k, metadata_filter=meta_filter)
            if meta_filter
            else store.search(query, top_k=k)
        )
        ranked = search(store.get_collection_size())
        points, best, doc_hit = grade(ranked, golds)
        total += points
        show_top(f"top-3 {'(filter ' + str(meta_filter) + ')' if meta_filter else '(không filter)'}", ranked[:TOP_K], golds)
        print(f"  Mức 1 (đúng doc_id gold trong top-3): {'có' if doc_hit else 'không'}")
        print(f"  Mức 2 (chunk gold chứa '{golds[0][1]}...'): hạng tốt nhất = {best} -> {points}/2 điểm")
        if meta_filter:  # A/B bắt buộc: cùng câu hỏi, bỏ filter
            unfiltered = store.search(query, top_k=store.get_collection_size())
            show_top("A/B: top-3 KHÔNG filter", unfiltered[:TOP_K], golds)
            wrong = [r["metadata"]["doc_id"] for r in unfiltered[:TOP_K] if r["metadata"].get("audience") != meta_filter["audience"]]
            print(f"  A/B: {len(wrong)}/{TOP_K} chunk trong top-3 không lọc thuộc audience khác ({', '.join(wrong) or '-'})")
        if agent:
            answer = agent.answer(query, top_k=TOP_K) if not meta_filter else answer_with_filter(agent, query, meta_filter)
            print(f"  Agent: {answer}")
    print(f"\nTỔNG: {total}/{2 * len(QUERIES)} điểm truy xuất")
    return 0


def answer_with_filter(agent: KnowledgeBaseAgent, query: str, meta_filter: dict) -> str:
    """KnowledgeBaseAgent.answer chỉ gọi store.search; khi cần filter thì tạm thay bằng search_with_filter."""
    original = agent.store.search
    agent.store.search = lambda q, top_k=5: agent.store.search_with_filter(q, top_k=top_k, metadata_filter=meta_filter)
    try:
        return agent.answer(query, top_k=TOP_K)
    finally:
        agent.store.search = original


if __name__ == "__main__":
    raise SystemExit(main())
