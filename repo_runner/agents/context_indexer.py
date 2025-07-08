import os
import faiss
from typing import List, Tuple
from sentence_transformers import SentenceTransformer

class ContextIndexer:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.text_chunks = []

    def _read_files(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Reads and splits files into (source, chunk) tuples.
        """
        chunks = []
        for path in file_paths:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # Split into lines or paragraphs for context granularity
                    for i, para in enumerate(content.split('\n\n')):
                        if para.strip():
                            chunks.append((f"{os.path.basename(path)}:{i}", para.strip()))
        return chunks

    def build_index(self, file_paths: List[str]):
        """
        Build a FAISS index from the given files.
        """
        self.text_chunks = self._read_files(file_paths)
        if not self.text_chunks:
            raise ValueError("No content to index.")
        texts = [chunk[1] for chunk in self.text_chunks]
        embeddings = self.model.encode(texts, show_progress_bar=False)
        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(embeddings)

    def query_index(self, query: str, top_k: int = 3) -> List[str]:
        """
        Query the FAISS index for top_k relevant chunks.
        """
        if self.index is None or not self.text_chunks:
            raise ValueError("Index not built.")
        query_emb = self.model.encode([query])
        D, I = self.index.search(query_emb, top_k)
        return [self.text_chunks[i][1] for i in I[0] if i < len(self.text_chunks)]

# Example usage:
# indexer = ContextIndexer()
# indexer.build_index(['.env', 'README.md', 'requirements.txt', 'logs/error.log'])
# context = indexer.query_index('ModuleNotFoundError') 