from typing import Callable

from .store import EmbeddingStore


class KnowledgeBaseAgent:
    """
    An agent that answers questions using a vector knowledge base.

    Retrieval-augmented generation (RAG) pattern:
        1. Retrieve top-k relevant chunks from the store.
        2. Build a prompt with the chunks as context.
        3. Call the LLM to generate an answer.
    """

    def __init__(self, store: EmbeddingStore, llm_fn: Callable[[str], str]) -> None:
        self.store = store
        self.llm_fn = llm_fn

    def answer(self, question: str, top_k: int = 3) -> str:
        results = self.store.search(question, top_k=top_k)
        if not results:
            # Nothing to ground on: do not waste an LLM call or let it guess.
            return "Không tìm thấy thông tin liên quan trong cơ sở tri thức."

        context_blocks = []
        for i, r in enumerate(results, start=1):
            meta = r.get("metadata", {})
            source = meta.get("source") or meta.get("doc_id") or r.get("id")
            context_blocks.append(f"[{i}] (nguồn: {source})\n{r['content']}")
        context = "\n\n".join(context_blocks)

        prompt = (
            "Bạn là trợ lý trả lời câu hỏi dựa trên tài liệu.\n"
            "Chỉ dùng thông tin trong phần NGỮ CẢNH bên dưới. "
            "Nếu ngữ cảnh không có câu trả lời, hãy nói rõ là không tìm thấy thông tin, không được suy đoán.\n"
            "Khi trả lời, trích dẫn số đoạn dùng, ví dụ [1].\n\n"
            f"NGỮ CẢNH:\n{context}\n\n"
            f"CÂU HỎI: {question}\n\n"
            "TRẢ LỜI:"
        )
        return self.llm_fn(prompt)
