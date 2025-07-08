import os
from typing import List, Tuple
import re

class ContextIndexer:
    def __init__(self):
        self.text_chunks = []
        self.index = None

    def _read_files(self, file_paths: List[str]) -> List[Tuple[str, str]]:
        """
        Reads and splits files into (source, chunk) tuples.
        """
        chunks = []
        for path in file_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # Split into lines or paragraphs for context granularity
                        for i, para in enumerate(content.split('\n\n')):
                            if para.strip():
                                chunks.append((f"{os.path.basename(path)}:{i}", para.strip()))
                except Exception as e:
                    print(f"Warning: Could not read {path}: {e}")
        return chunks

    def build_index(self, file_paths: List[str]):
        """
        Build a simple text-based index from the given files.
        """
        self.text_chunks = self._read_files(file_paths)
        if not self.text_chunks:
            print("Warning: No content to index.")
            return
        print(f"Indexed {len(self.text_chunks)} text chunks")

    def query_index(self, query: str, top_k: int = 3) -> List[str]:
        """
        Query the index for top_k relevant chunks using simple text matching.
        """
        if not self.text_chunks:
            return []
        
        # Simple keyword-based search
        query_words = set(re.findall(r'\w+', query.lower()))
        scored_chunks = []
        
        for chunk_id, chunk_text in self.text_chunks:
            chunk_words = set(re.findall(r'\w+', chunk_text.lower()))
            # Calculate simple overlap score
            overlap = len(query_words.intersection(chunk_words))
            if overlap > 0:
                scored_chunks.append((overlap, chunk_text))
        
        # Sort by score and return top_k
        scored_chunks.sort(reverse=True)
        return [chunk for score, chunk in scored_chunks[:top_k]] 