from __future__ import annotations

class OntologyTextEncoder:
    """
    Thin wrapper around the shared embedding model so ontology training/inference
    can later swap in a stronger encoder without touching callers.
    """

    def __init__(self, embeddings=None):
        if embeddings is None:
            from common.models import get_embeddings

            embeddings = get_embeddings()
        self.embeddings = embeddings

    def encode(self, text: str) -> list[float]:
        return self.embeddings.embed_query(text)

    def encode_many(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        try:
            return self.embeddings.embed_documents(texts)
        except Exception:
            return [self.encode(text) for text in texts]
