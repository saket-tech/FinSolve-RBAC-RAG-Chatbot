"""Chroma vector store indexing and retrieval."""

from functools import lru_cache

import chromadb
from chromadb.api.models.Collection import Collection

from app.config.settings import Settings, get_settings
from app.rag.embeddings import get_embedding_function
from app.rag.loader import DocumentChunk, load_all_documents


def _get_client(settings: Settings) -> chromadb.PersistentClient:
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(settings.chroma_dir))


def get_or_create_collection(settings: Settings | None = None) -> Collection:
    settings = settings or get_settings()
    client = _get_client(settings)
    embedding_fn = get_embedding_function()
    return client.get_or_create_collection(
        name=settings.collection_name,
        embedding_function=embedding_fn,
        metadata={"hnsw:space": "cosine"},
    )


def build_index(settings: Settings | None = None, reset: bool = False) -> int:
    """Ingest all documents into Chroma. Returns number of chunks indexed."""
    settings = settings or get_settings()
    client = _get_client(settings)

    if reset and settings.collection_name in [c.name for c in client.list_collections()]:
        client.delete_collection(settings.collection_name)

    collection = get_or_create_collection(settings)
    documents = load_all_documents(settings)

    if not documents:
        return 0

    ids = [f"doc_{i}" for i in range(len(documents))]
    collection.upsert(
        ids=ids,
        documents=[d.content for d in documents],
        metadatas=[
            {"department": d.department, "source": d.source}
            for d in documents
        ],
    )
    return len(documents)


@lru_cache
def get_collection() -> Collection:
    return get_or_create_collection()


def retrieve_documents(
    query: str,
    allowed_departments: list[str],
    top_k: int | None = None,
) -> list[dict]:
    """Retrieve relevant chunks filtered by RBAC departments."""
    settings = get_settings()
    top_k = top_k or settings.top_k
    collection = get_collection()

    if not allowed_departments:
        return []

    # Chroma metadata filter for allowed departments
    where_filter = {"department": {"$in": allowed_departments}}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter,
        include=["documents", "metadatas", "distances"],
    )

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]

    retrieved: list[dict] = []
    for doc, meta, distance in zip(documents, metadatas, distances):
        retrieved.append(
            {
                "content": doc,
                "source": meta.get("source", "unknown"),
                "department": meta.get("department", "unknown"),
                "score": round(1 - distance, 4) if distance is not None else None,
            }
        )
    return retrieved
