"""Local sentence-transformer embeddings for Chroma."""

from functools import lru_cache

from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from sentence_transformers import SentenceTransformer

from app.config.settings import get_settings


class LocalEmbeddingFunction(EmbeddingFunction):
    """Chroma-compatible embedding function using sentence-transformers."""

    def __init__(self, model_name: str) -> None:
        self._model = SentenceTransformer(model_name)

    def __call__(self, input: Documents) -> Embeddings:
        embeddings = self._model.encode(input, show_progress_bar=False)
        return embeddings.tolist()


@lru_cache
def get_embedding_function() -> LocalEmbeddingFunction:
    settings = get_settings()
    return LocalEmbeddingFunction(settings.embedding_model)
