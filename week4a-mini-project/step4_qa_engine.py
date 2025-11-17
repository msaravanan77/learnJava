"""
Step 4: Complete QA Engine
===========================
Combine all components into end-to-end QA system.

This step:
- Integrates document processor, encoder, and answer extractor
- Handles multi-document search
- Ranks and returns answers
- Provides complete question-answering pipeline

Run: python step4_qa_engine.py
"""

import torch
import os
from typing import List, Tuple, Dict
from step1_document_processor import DocumentProcessor
from step2_build_encoder import BERTEncoder, SimpleTokenizer
from step3_answer_extractor import AnswerExtractor


class QuestionAnsweringEngine:
    """
    Complete end-to-end Question Answering system.
    """
    def __init__(self, document_processor: DocumentProcessor,
                 qa_model: AnswerExtractor,
                 tokenizer: SimpleTokenizer):
        """
        Args:
            document_processor: Processes and stores documents
            qa_model: Answer extraction model
            tokenizer: Tokenizer for encoding text
        """
        self.doc_processor = document_processor
        self.qa_model = qa_model
        self.tokenizer = tokenizer
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

        # Move model to device
        self.qa_model = self.qa_model.to(self.device)
        self.qa_model.eval()

    def answer_question(self, question: str, top_k_chunks: int = 5,
                       max_answer_length: int = 30) -> List[Dict]:
        """
        Answer a question using the knowledge base.

        Args:
            question: User's question
            top_k_chunks: Number of document chunks to consider
            max_answer_length: Maximum answer length in tokens

        Returns:
            List of answer dictionaries with scores
        """
        # Step 1: Find relevant document chunks
        relevant_chunks = self.doc_processor.search_chunks(question, top_k=top_k_chunks)

        if not relevant_chunks:
            return [{
                'answer': 'No relevant documents found',
                'confidence': 0.0,
                'source': None
            }]

        # Step 2: Extract answers from each relevant chunk
        answers = []

        for chunk, retrieval_score in relevant_chunks:
            # Tokenize question-document pair
            token_ids, segment_ids, attention_mask = self.tokenizer.encode_pair(
                question, chunk.text, max_length=512
            )

            # Convert to tensors
            input_ids = torch.tensor([token_ids], device=self.device)
            segment_ids_t = torch.tensor([segment_ids], device=self.device)
            attention_mask_t = torch.tensor([attention_mask], device=self.device)

            # Extract answer
            answer_text, start_pos, end_pos, extraction_confidence = self.qa_model.extract_answer(
                input_ids, segment_ids_t, attention_mask_t,
                self.tokenizer, max_answer_length
            )

            # Combine retrieval and extraction scores
            combined_confidence = retrieval_score * extraction_confidence

            answers.append({
                'answer': answer_text,
                'confidence': combined_confidence,
                'extraction_confidence': extraction_confidence,
                'retrieval_score': retrieval_score,
                'source_document': chunk.doc_id,
                'source_chunk': chunk.chunk_id,
                'context': chunk.text[:200] + '...' if len(chunk.text) > 200 else chunk.text,
                'positions': (start_pos, end_pos)
            })

        # Step 3: Sort by confidence and return
        answers.sort(key=lambda x: x['confidence'], reverse=True)

        return answers

    def get_best_answer(self, question: str, top_k_chunks: int = 5) -> Dict:
        """
        Get the single best answer to a question.

        Args:
            question: User's question
            top_k_chunks: Number of chunks to consider

        Returns:
            Best answer dictionary
        """
        answers = self.answer_question(question, top_k_chunks)
        return answers[0] if answers else {
            'answer': 'Unable to find answer',
            'confidence': 0.0
        }

    def interactive_qa(self):
        """
        Interactive question-answering session.
        """
        print("\n" + "=" * 80)
        print("INTERACTIVE QA SESSION")
        print("=" * 80)
        print("Ask questions about the knowledge base. Type 'quit' to exit.")
        print("-" * 80)

        while True:
            question = input("\nYour question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question:
                continue

            # Get answer
            print("\nProcessing...")
            answer = self.get_best_answer(question)

            # Display result
            print(f"\n{'=' * 80}")
            print(f"Answer: {answer['answer']}")
            print(f"Confidence: {answer['confidence']:.3f}")
            print(f"Source: {answer.get('source_document', 'N/A')}")
            print(f"\nContext: {answer.get('context', 'N/A')}")
            print(f"{'=' * 80}")


def demonstrate_qa_engine():
    """
    Demonstrate the complete QA engine.
    """
    print("=" * 80)
    print("STEP 4: COMPLETE QA ENGINE DEMONSTRATION")
    print("=" * 80)

    # Step 1: Setup document processor
    print("\n1. Loading documents...")
    doc_processor = DocumentProcessor(max_chunk_length=512, chunk_overlap=50)

    # Check if sample documents exist, create if not
    sample_dir = "sample_documents"
    if not os.path.exists(sample_dir):
        print(f"   Creating sample documents...")
        os.makedirs(sample_dir)

        sample_docs = {
            "transformers.txt": """Transformers are a type of neural network architecture introduced in 2017.
The key innovation is the attention mechanism, which allows the model to focus on relevant parts of the input.
Unlike recurrent networks, transformers can process all tokens in parallel, making them much faster to train.
The transformer consists of an encoder and decoder. Modern language models like GPT and BERT are based on transformers.""",

            "attention.txt": """Attention is a mechanism that allows neural networks to focus on relevant information.
The attention mechanism computes a weighted sum of values, where weights are determined by query-key similarity.
Multi-head attention runs multiple attention mechanisms in parallel. Each head can learn different patterns.""",

            "bert.txt": """BERT stands for Bidirectional Encoder Representations from Transformers.
It is a language model developed by Google that uses only the encoder part of the transformer architecture.
BERT is pre-trained using masked language modeling, where random tokens are masked and predicted.
BERT is excellent for tasks like text classification, named entity recognition, and question answering."""
        }

        for filename, content in sample_docs.items():
            with open(os.path.join(sample_dir, filename), 'w') as f:
                f.write(content.strip())

    doc_processor.add_documents_from_directory(sample_dir)

    # Step 2: Create tokenizer
    print("\n2. Creating tokenizer...")
    tokenizer = SimpleTokenizer()

    # Build vocabulary from all documents
    all_texts = [chunk.text for chunk in doc_processor.chunks]
    tokenizer.fit(all_texts)

    # Step 3: Create QA model
    print("\n3. Creating QA model...")
    vocab_size = len(tokenizer.vocab)
    encoder = BERTEncoder(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        num_layers=2,
        d_ff=512
    )
    qa_model = AnswerExtractor(encoder)

    # Step 4: Create QA engine
    print("\n4. Creating QA engine...")
    qa_engine = QuestionAnsweringEngine(doc_processor, qa_model, tokenizer)

    print(f"   ✓ QA Engine ready!")
    print(f"   - Documents: {len(doc_processor.documents)}")
    print(f"   - Chunks: {len(doc_processor.chunks)}")
    print(f"   - Vocabulary: {vocab_size} tokens")

    # Step 5: Test with sample questions
    print("\n5. Testing with sample questions...")

    test_questions = [
        "What is attention?",
        "What does BERT stand for?",
        "How do transformers process tokens?",
        "What is multi-head attention?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n{'-' * 80}")
        print(f"Question {i}: {question}")

        # Get top 3 answers
        answers = qa_engine.answer_question(question, top_k_chunks=3)

        print(f"\nTop answer:")
        print(f"  Answer: '{answers[0]['answer']}'")
        print(f"  Confidence: {answers[0]['confidence']:.3f}")
        print(f"  Source: {answers[0]['source_document']}")
        print(f"  Context: {answers[0]['context'][:100]}...")

        if len(answers) > 1:
            print(f"\nAlternative answers:")
            for j, ans in enumerate(answers[1:3], 2):
                print(f"  {j}. '{ans['answer']}' (conf: {ans['confidence']:.3f})")

    print("\n" + "=" * 80)
    print("✓ Step 4 Complete: End-to-end QA engine working!")
    print("=" * 80)
    print("\nNOTE: This model is randomly initialized for demonstration.")
    print("For production use:")
    print("  1. Use pre-trained BERT weights")
    print("  2. Fine-tune on SQuAD or similar QA dataset")
    print("  3. Use proper WordPiece/BPE tokenizer")
    print("  4. Add re-ranking and answer verification")

    return qa_engine


if __name__ == "__main__":
    qa_engine = demonstrate_qa_engine()

    # Optionally run interactive mode
    print("\n" + "=" * 80)
    response = input("Would you like to try interactive QA? (y/n): ")
    if response.lower() in ['y', 'yes']:
        qa_engine.interactive_qa()
