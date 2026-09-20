from __future__ import annotations

from typing import Any, Callable

from .chunking import _dot
from .embeddings import _mock_embed
from .models import Document


class EmbeddingStore:
    """
    A vector store for text chunks.

    In-memory by default: the lab tests never need ChromaDB. Pass use_chroma=True
    to back the store with a ChromaDB collection instead (pip install chromadb);
    every public method keeps the same contract in both modes. Embeddings are
    always computed by embedding_fn and handed to Chroma, never by Chroma itself.
    The embedding_fn parameter allows injection of mock embeddings for tests.
    """

    def __init__(
        self,
        collection_name: str = "documents",
        embedding_fn: Callable[[str], list[float]] | None = None,
        use_chroma: bool = False,
        persist_dir: str | None = None,
    ) -> None:
        self._embedding_fn = embedding_fn or _mock_embed
        self._collection_name = collection_name
        self._use_chroma = use_chroma
        self._store: list[dict[str, Any]] = []
        self._collection = None
        self._next_index = 0
        if use_chroma:
            self._collection = self._open_chroma_collection(persist_dir)

    def _open_chroma_collection(self, persist_dir: str | None):
        import re

        import chromadb  # imported lazily so the in-memory path needs no dependency

        # Chroma names: 3-512 chars of [a-zA-Z0-9._-], starting and ending alphanumeric.
        name = re.sub(r"[^a-zA-Z0-9._-]", "-", self._collection_name).strip("._-")
        if len(name) < 3:
            name = f"{name}-store"

        if persist_dir:
            client = chromadb.PersistentClient(path=persist_dir)
        else:
            client = chromadb.EphemeralClient()
            # The ephemeral client is shared per process; start from an empty collection.
            try:
                client.delete_collection(name)
            except Exception:
                pass
        # "cosine" so that score = 1 - distance matches the in-memory dot product.
        return client.get_or_create_collection(
            name=name, metadata={"hnsw:space": "cosine"}
        )

    @staticmethod
    def _chroma_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
        # Chroma only accepts str/int/float/bool values.
        return {
            key: value if isinstance(value, (str, int, float, bool)) else str(value)
            for key, value in metadata.items()
            if value is not None
        }

    @staticmethod
    def _chroma_where(metadata_filter: dict | None) -> dict | None:
        if not metadata_filter:
            return None
        clauses = [{key: {"$eq": value}} for key, value in metadata_filter.items()]
        return clauses[0] if len(clauses) == 1 else {"$and": clauses}

    def _chroma_search(self, query: str, top_k: int, where: dict | None) -> list[dict[str, Any]]:
        total = self._collection.count()
        if total == 0 or top_k <= 0:
            return []
        result = self._collection.query(
            query_embeddings=[self._embedding_fn(query)],
            n_results=min(top_k, total),
            where=where,
            include=["documents", "metadatas", "distances"],
        )
        return [
            {"id": id_, "content": content, "metadata": metadata, "score": 1.0 - distance}
            for id_, content, metadata, distance in zip(
                result["ids"][0], result["documents"][0], result["metadatas"][0], result["distances"][0]
            )
        ]

    def _make_record(self, doc: Document) -> dict[str, Any]:
        # Copy so later edits by the caller do not leak into the store.
        metadata = dict(doc.metadata)
        # delete_document depends on doc_id; fall back to the document id if the caller set none.
        metadata.setdefault("doc_id", doc.id)
        record = {
            "id": doc.id,
            "content": doc.content,
            "metadata": metadata,
            "embedding": self._embedding_fn(doc.content),
            "index": self._next_index,
        }
        self._next_index += 1
        return record

    def _search_records(self, query: str, records: list[dict[str, Any]], top_k: int) -> list[dict[str, Any]]:
        if not records or top_k <= 0:
            return []
        # Vectors are normalized, so the dot product equals cosine similarity.
        query_embedding = self._embedding_fn(query)
        scored = [(_dot(query_embedding, r["embedding"]), r) for r in records]
        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [
            {
                "id": r["id"],
                "content": r["content"],
                "metadata": r["metadata"],
                "score": score,
            }
            for score, r in scored[:top_k]
        ]

    def add_documents(self, docs: list[Document]) -> None:
        """
        Embed each document's content and store it.

        For ChromaDB: upsert(ids, documents, embeddings, metadatas) into the collection.
        For in-memory: append dicts to self._store
        """
        if self._use_chroma:
            if not docs:
                return
            metadatas = []
            for doc in docs:
                metadata = dict(doc.metadata)
                metadata.setdefault("doc_id", doc.id)
                metadatas.append(self._chroma_metadata(metadata))
            self._collection.upsert(
                ids=[doc.id for doc in docs],
                documents=[doc.content for doc in docs],
                embeddings=[self._embedding_fn(doc.content) for doc in docs],
                metadatas=metadatas,
            )
            return
        for doc in docs:
            self._store.append(self._make_record(doc))

    def search(self, query: str, top_k: int = 5) -> list[dict[str, Any]]:
        """
        Find the top_k most similar documents to query.

        For in-memory: compute dot product of query embedding vs all stored embeddings.
        """
        if self._use_chroma:
            return self._chroma_search(query, top_k, None)
        return self._search_records(query, self._store, top_k)

    def get_collection_size(self) -> int:
        """Return the total number of stored chunks."""
        if self._use_chroma:
            return self._collection.count()
        return len(self._store)

    def search_with_filter(self, query: str, top_k: int = 3, metadata_filter: dict = None) -> list[dict]:
        """
        Search with optional metadata pre-filtering.

        First filter stored chunks by metadata_filter, then run similarity search.
        """
        if self._use_chroma:
            # Chroma applies `where` before the nearest-neighbour ranking.
            return self._chroma_search(query, top_k, self._chroma_where(metadata_filter))
        if not metadata_filter:
            candidates = self._store
        else:
            # Filter first, then rank: filtering after top-k could leave 0 results
            # even though matching chunks exist.
            candidates = [
                r
                for r in self._store
                if all(r["metadata"].get(key) == value for key, value in metadata_filter.items())
            ]
        return self._search_records(query, candidates, top_k)

    def delete_document(self, doc_id: str) -> bool:
        """
        Remove all chunks belonging to a document.

        Returns True if any chunks were removed, False otherwise.
        """
        if self._use_chroma:
            ids = self._collection.get(where={"doc_id": {"$eq": doc_id}}, include=[])["ids"]
            if not ids:
                return False
            self._collection.delete(ids=ids)
            return True
        before = len(self._store)
        self._store = [r for r in self._store if r["metadata"].get("doc_id") != doc_id]
        return len(self._store) < before
