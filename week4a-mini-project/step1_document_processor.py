"""
Step 1: Document Processor
===========================
Load, preprocess, and chunk documents for the QA system.

This step handles:
- Loading documents from various formats
- Text cleaning and normalization
- Splitting into manageable chunks
- Creating document database

Run: python step1_document_processor.py
"""

import os
import re
from typing import List, Dict, Tuple


class DocumentChunk:
    """Represents a chunk of a document."""
    def __init__(self, text: str, doc_id: str, chunk_id: int, start_char: int, end_char: int):
        self.text = text
        self.doc_id = doc_id
        self.chunk_id = chunk_id
        self.start_char = start_char
        self.end_char = end_char

    def __repr__(self):
        preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"Chunk({self.doc_id}, {self.chunk_id}, '{preview}')"


class DocumentProcessor:
    """
    Process documents for Question Answering system.
    """
    def __init__(self, max_chunk_length=512, chunk_overlap=50):
        """
        Args:
            max_chunk_length: Maximum characters per chunk
            chunk_overlap: Number of overlapping characters between chunks
        """
        self.max_chunk_length = max_chunk_length
        self.chunk_overlap = chunk_overlap
        self.documents = {}
        self.chunks = []

    def load_document(self, filepath: str) -> str:
        """
        Load a document from file.

        Args:
            filepath: Path to document file

        Returns:
            Document text
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        print(f"✓ Loaded: {filepath} ({len(text)} characters)")
        return text

    def clean_text(self, text: str) -> str:
        """
        Clean and normalize text.

        Args:
            text: Raw text

        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep punctuation
        text = re.sub(r'[^\w\s.,!?;:()\-\']', '', text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def chunk_text(self, text: str, doc_id: str) -> List[DocumentChunk]:
        """
        Split text into overlapping chunks.

        Args:
            text: Document text
            doc_id: Document identifier

        Returns:
            List of DocumentChunk objects
        """
        chunks = []
        chunk_id = 0
        start_char = 0

        while start_char < len(text):
            # Calculate end of chunk
            end_char = min(start_char + self.max_chunk_length, len(text))

            # If not at the end, try to break at sentence boundary
            if end_char < len(text):
                # Look for sentence ending punctuation
                last_period = text.rfind('.', start_char, end_char)
                last_question = text.rfind('?', start_char, end_char)
                last_exclaim = text.rfind('!', start_char, end_char)

                break_point = max(last_period, last_question, last_exclaim)

                if break_point > start_char:
                    end_char = break_point + 1  # Include the punctuation

            # Extract chunk text
            chunk_text = text[start_char:end_char].strip()

            if chunk_text:  # Only add non-empty chunks
                chunk = DocumentChunk(
                    text=chunk_text,
                    doc_id=doc_id,
                    chunk_id=chunk_id,
                    start_char=start_char,
                    end_char=end_char
                )
                chunks.append(chunk)
                chunk_id += 1

            # Move start position with overlap
            start_char = end_char - self.chunk_overlap

            # Avoid infinite loop
            if start_char <= 0:
                start_char = end_char

        return chunks

    def add_document(self, filepath: str, doc_id: str = None):
        """
        Add a document to the knowledge base.

        Args:
            filepath: Path to document
            doc_id: Optional document ID (uses filename if not provided)
        """
        if doc_id is None:
            doc_id = os.path.basename(filepath)

        # Load and clean
        text = self.load_document(filepath)
        text = self.clean_text(text)

        # Store original document
        self.documents[doc_id] = text

        # Create chunks
        doc_chunks = self.chunk_text(text, doc_id)
        self.chunks.extend(doc_chunks)

        print(f"  Created {len(doc_chunks)} chunks from {doc_id}")

    def add_documents_from_directory(self, directory: str):
        """
        Add all documents from a directory.

        Args:
            directory: Path to directory containing documents
        """
        if not os.path.exists(directory):
            print(f"Warning: Directory {directory} does not exist")
            return

        files = [f for f in os.listdir(directory) if f.endswith('.txt')]

        print(f"\nLoading {len(files)} documents from {directory}...")
        for filename in files:
            filepath = os.path.join(directory, filename)
            self.add_document(filepath)

    def get_chunk_by_id(self, doc_id: str, chunk_id: int) -> DocumentChunk:
        """Get a specific chunk."""
        for chunk in self.chunks:
            if chunk.doc_id == doc_id and chunk.chunk_id == chunk_id:
                return chunk
        return None

    def search_chunks(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Simple keyword-based search for relevant chunks.

        Args:
            query: Search query
            top_k: Number of top chunks to return

        Returns:
            List of (chunk, score) tuples
        """
        query_words = set(query.lower().split())
        scored_chunks = []

        for chunk in self.chunks:
            chunk_words = set(chunk.text.lower().split())

            # Simple overlap score
            overlap = len(query_words & chunk_words)
            score = overlap / max(len(query_words), 1)

            if score > 0:
                scored_chunks.append((chunk, score))

        # Sort by score descending
        scored_chunks.sort(key=lambda x: x[1], reverse=True)

        return scored_chunks[:top_k]

    def get_statistics(self) -> Dict:
        """Get statistics about the document collection."""
        total_chars = sum(len(doc) for doc in self.documents.values())
        total_chunks = len(self.chunks)
        avg_chunk_size = sum(len(c.text) for c in self.chunks) / max(total_chunks, 1)

        return {
            'num_documents': len(self.documents),
            'total_characters': total_chars,
            'num_chunks': total_chunks,
            'avg_chunk_size': avg_chunk_size,
            'max_chunk_length': self.max_chunk_length,
            'chunk_overlap': self.chunk_overlap
        }


def demonstrate_document_processing():
    """
    Demonstrate document processing functionality.
    """
    print("=" * 80)
    print("STEP 1: DOCUMENT PROCESSOR DEMONSTRATION")
    print("=" * 80)

    # Create processor
    processor = DocumentProcessor(max_chunk_length=512, chunk_overlap=50)

    # Check if sample documents exist
    sample_dir = "sample_documents"
    if not os.path.exists(sample_dir):
        print(f"\nCreating sample documents directory: {sample_dir}")
        os.makedirs(sample_dir)

        # Create sample documents
        sample_docs = {
            "transformers.txt": """
            Transformers are a type of neural network architecture introduced in 2017.
            The key innovation is the attention mechanism, which allows the model to focus
            on relevant parts of the input. Unlike recurrent networks, transformers can
            process all tokens in parallel, making them much faster to train.

            The transformer consists of an encoder and decoder. The encoder processes the
            input sequence and creates contextualized representations. The decoder generates
            the output sequence, attending to both previously generated tokens and the
            encoder output.

            Modern language models like GPT and BERT are based on the transformer architecture.
            GPT uses only the decoder part and is excellent for text generation. BERT uses
            only the encoder part and excels at understanding tasks like classification.
            """,
            "attention.txt": """
            Attention is a mechanism that allows neural networks to focus on relevant information.
            In the transformer, attention works through three components: queries, keys, and values.

            The attention mechanism computes a weighted sum of values, where the weights are
            determined by the similarity between queries and keys. This is called scaled
            dot-product attention and is computed as: softmax(QK^T / sqrt(d_k)) V.

            Multi-head attention runs multiple attention mechanisms in parallel. Each head can
            learn to focus on different aspects of the relationships in the data. The outputs
            are concatenated and linearly transformed.
            """,
            "bert.txt": """
            BERT (Bidirectional Encoder Representations from Transformers) is a language model
            developed by Google. It uses only the encoder part of the transformer architecture.

            BERT is pre-trained using masked language modeling, where random tokens are masked
            and the model learns to predict them. This bidirectional training allows BERT to
            build deep understanding of language context.

            BERT is excellent for tasks like text classification, named entity recognition,
            and question answering. It can be fine-tuned on specific tasks with relatively
            small amounts of labeled data.
            """
        }

        for filename, content in sample_docs.items():
            filepath = os.path.join(sample_dir, filename)
            with open(filepath, 'w') as f:
                f.write(content.strip())
            print(f"  Created: {filepath}")

    # Load documents
    processor.add_documents_from_directory(sample_dir)

    # Show statistics
    print("\n" + "-" * 80)
    print("DOCUMENT STATISTICS")
    print("-" * 80)
    stats = processor.get_statistics()
    for key, value in stats.items():
        print(f"{key:20s}: {value}")

    # Show some chunks
    print("\n" + "-" * 80)
    print("SAMPLE CHUNKS")
    print("-" * 80)
    for i, chunk in enumerate(processor.chunks[:3]):
        print(f"\nChunk {i + 1}:")
        print(f"  Document: {chunk.doc_id}")
        print(f"  Chunk ID: {chunk.chunk_id}")
        print(f"  Length: {len(chunk.text)} characters")
        print(f"  Text: {chunk.text[:200]}...")

    # Demonstrate search
    print("\n" + "-" * 80)
    print("SEARCH DEMONSTRATION")
    print("-" * 80)

    queries = [
        "What is attention?",
        "How does BERT work?",
        "transformer encoder decoder"
    ]

    for query in queries:
        print(f"\nQuery: '{query}'")
        results = processor.search_chunks(query, top_k=3)

        if results:
            print(f"Found {len(results)} relevant chunks:")
            for j, (chunk, score) in enumerate(results, 1):
                print(f"\n  {j}. Score: {score:.3f} | Doc: {chunk.doc_id}")
                print(f"     {chunk.text[:150]}...")
        else:
            print("  No relevant chunks found")

    print("\n" + "=" * 80)
    print("✓ Step 1 Complete: Documents processed and ready for encoding!")
    print("=" * 80)

    return processor


if __name__ == "__main__":
    processor = demonstrate_document_processing()
