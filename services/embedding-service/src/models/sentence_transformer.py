"""
Code embedding generation using Sentence Transformers
"""

from typing import List, Union
import torch
from sentence_transformers import SentenceTransformer
import numpy as np
import re


class CodeEmbedder:
    """Generate embeddings for code using sentence transformers"""

    def __init__(
        self,
        model_name: str = "microsoft/graphcodebert-base",
        device: str = None,
        batch_size: int = 32
    ):
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = SentenceTransformer(model_name, device=self.device)
        self.batch_size = batch_size

        # Warm up model
        self.model.encode(["warm up"], show_progress_bar=False)

    def embed_single(self, text: str) -> np.ndarray:
        """Generate embedding for a single text"""
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False
        )
        return embedding

    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for multiple texts"""
        embeddings = self.model.encode(
            texts,
            batch_size=self.batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings

    def preprocess_code(self, code_element: dict) -> str:
        """Preprocess code element for embedding"""
        components = []

        # Element type and name
        components.append(f"{code_element.get('type', 'code')}: {code_element.get('name', '')}")

        # Signature
        if signature := code_element.get('signature'):
            components.append(signature)

        # Docstring
        if docstring := code_element.get('docstring'):
            components.append(docstring)

        # Normalized code
        if code := code_element.get('content'):
            normalized = self._normalize_code(code)
            components.append(normalized)

        return " [SEP] ".join(components)

    @staticmethod
    def _normalize_code(code: str) -> str:
        """Normalize code for better embedding"""
        # Remove excessive whitespace
        code = ' '.join(code.split())

        # Replace string literals
        code = re.sub(r'"[^"]*"', '"STRING"', code)
        code = re.sub(r"'[^']*'", "'STRING'", code)

        # Replace number literals
        code = re.sub(r'\b\d+\b', 'NUM', code)

        return code


if __name__ == "__main__":
    embedder = CodeEmbedder()

    code_elements = [
        {
            'type': 'function',
            'name': 'authenticateUser',
            'signature': 'public boolean authenticateUser(String username, String password)',
            'docstring': 'Authenticates user credentials against the database',
            'content': 'public boolean authenticateUser(String username, String password) { ... }'
        },
        {
            'type': 'function',
            'name': 'validateEmail',
            'signature': 'private boolean validateEmail(String email)',
            'docstring': 'Validates email format using regex',
            'content': 'private boolean validateEmail(String email) { ... }'
        }
    ]

    # Preprocess
    texts = [embedder.preprocess_code(elem) for elem in code_elements]

    # Generate embeddings
    embeddings = embedder.embed_batch(texts)

    print(f"Generated {len(embeddings)} embeddings")
    print(f"Embedding dimension: {embeddings[0].shape}")

    # Calculate similarity
    from sklearn.metrics.pairwise import cosine_similarity
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    print(f"Similarity between functions: {similarity:.4f}")
