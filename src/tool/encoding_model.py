from sentence_transformers import SentenceTransformer

class SentenceEmbeddingModelling:

    def __init__(self) -> None:
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

    def embed_text(self, text) -> list:
        return self.model.encode(text).tolist()
    

sentence_modelling = SentenceEmbeddingModelling()