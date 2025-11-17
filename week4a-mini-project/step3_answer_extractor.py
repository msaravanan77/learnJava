"""
Step 3: Answer Extractor
=========================
Extract answer spans from encoded documents using attention.

This step:
- Adds answer span prediction heads
- Predicts start and end positions of answers
- Extracts answer text from documents
- Computes confidence scores

Run: python step3_answer_extractor.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from step2_build_encoder import BERTEncoder, SimpleTokenizer


class AnswerExtractor(nn.Module):
    """
    Answer span extraction using BERT encoder.
    Predicts start and end positions of the answer in the document.
    """
    def __init__(self, encoder: BERTEncoder):
        super().__init__()

        self.encoder = encoder
        d_model = encoder.d_model

        # Linear layers for start and end position prediction
        self.start_classifier = nn.Linear(d_model, 1)
        self.end_classifier = nn.Linear(d_model, 1)

    def forward(self, input_ids, segment_ids=None, attention_mask=None):
        """
        Args:
            input_ids: (batch, seq_len) - Token IDs
            segment_ids: (batch, seq_len) - Segment IDs
            attention_mask: (batch, seq_len) - Attention mask

        Returns:
            start_logits: (batch, seq_len) - Start position logits
            end_logits: (batch, seq_len) - End position logits
        """
        # Encode with BERT
        encoded = self.encoder(input_ids, segment_ids, attention_mask)  # (batch, seq_len, d_model)

        # Predict start and end positions
        start_logits = self.start_classifier(encoded).squeeze(-1)  # (batch, seq_len)
        end_logits = self.end_classifier(encoded).squeeze(-1)      # (batch, seq_len)

        # Mask out padding tokens
        if attention_mask is not None:
            start_logits = start_logits.masked_fill(attention_mask == 0, float('-inf'))
            end_logits = end_logits.masked_fill(attention_mask == 0, float('-inf'))

        return start_logits, end_logits

    def extract_answer(self, input_ids, segment_ids, attention_mask, tokenizer,
                       max_answer_length=30):
        """
        Extract the answer span from a question-document pair.

        Args:
            input_ids: Token IDs tensor (1, seq_len)
            segment_ids: Segment IDs tensor (1, seq_len)
            attention_mask: Attention mask tensor (1, seq_len)
            tokenizer: Tokenizer for decoding
            max_answer_length: Maximum answer length in tokens

        Returns:
            answer_text: Extracted answer
            start_pos: Start position
            end_pos: End position
            confidence: Confidence score (0-1)
        """
        self.eval()

        with torch.no_grad():
            # Get logits
            start_logits, end_logits = self(input_ids, segment_ids, attention_mask)

            # Get probabilities
            start_probs = F.softmax(start_logits, dim=-1)
            end_probs = F.softmax(end_logits, dim=-1)

            # Find best start and end positions
            start_pos = torch.argmax(start_probs, dim=-1).item()
            end_pos = torch.argmax(end_probs, dim=-1).item()

            # Ensure end >= start
            if end_pos < start_pos:
                end_pos = start_pos

            # Ensure answer is not too long
            if end_pos - start_pos + 1 > max_answer_length:
                end_pos = start_pos + max_answer_length - 1

            # Ensure answer is in document segment (segment_id == 1)
            segment_ids_list = segment_ids[0].tolist()
            while start_pos < len(segment_ids_list) and segment_ids_list[start_pos] != 1:
                start_pos += 1

            if start_pos >= len(segment_ids_list):
                return "No answer found", 0, 0, 0.0

            # Extract answer tokens
            answer_token_ids = input_ids[0, start_pos:end_pos + 1].tolist()

            # Decode to text
            answer_words = []
            for token_id in answer_token_ids:
                if token_id in tokenizer.inv_vocab:
                    word = tokenizer.inv_vocab[token_id]
                    if word not in ['[CLS]', '[SEP]', '[PAD]']:
                        answer_words.append(word)

            answer_text = ' '.join(answer_words)

            # Compute confidence score
            confidence = (start_probs[0, start_pos].item() + end_probs[0, end_pos].item()) / 2

            return answer_text, start_pos, end_pos, confidence


def demonstrate_answer_extraction():
    """
    Demonstrate answer extraction.
    """
    print("=" * 80)
    print("STEP 3: ANSWER EXTRACTION DEMONSTRATION")
    print("=" * 80)

    # Create tokenizer and vocabulary
    print("\n1. Creating tokenizer and vocabulary...")
    tokenizer = SimpleTokenizer()

    sample_texts = [
        "what is attention mechanism in transformers",
        "how does bert work for question answering",
        "attention allows neural networks to focus on relevant parts of the input when processing sequences",
        "bert uses bidirectional encoder to understand context from both directions",
        "transformers process all tokens in parallel using attention",
        "the attention mechanism computes weighted sum of values based on query-key similarity"
    ]

    tokenizer.fit(sample_texts)

    # Create encoder
    print("\n2. Creating BERT encoder...")
    vocab_size = len(tokenizer.vocab)
    encoder = BERTEncoder(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=4,
        num_layers=2,
        d_ff=512,
        max_position=512
    )

    # Create answer extractor
    print("\n3. Creating answer extractor...")
    qa_model = AnswerExtractor(encoder)

    total_params = sum(p.numel() for p in qa_model.parameters())
    print(f"   Total parameters: {total_params:,}")

    # Test questions and documents
    print("\n4. Testing answer extraction...")

    test_cases = [
        {
            "question": "What does attention allow?",
            "document": "Attention allows neural networks to focus on relevant parts of the input when processing sequences"
        },
        {
            "question": "How does BERT work?",
            "document": "BERT uses bidirectional encoder to understand context from both directions"
        },
        {
            "question": "What mechanism computes weighted sum?",
            "document": "The attention mechanism computes weighted sum of values based on query-key similarity"
        }
    ]

    for i, test in enumerate(test_cases, 1):
        question = test["question"]
        document = test["document"]

        print(f"\n{'-' * 80}")
        print(f"Test Case {i}:")
        print(f"Question: {question}")
        print(f"Document: {document}")

        # Tokenize
        token_ids, segment_ids, attention_mask = tokenizer.encode_pair(
            question, document, max_length=128
        )

        # Convert to tensors
        input_ids = torch.tensor([token_ids])
        segment_ids_t = torch.tensor([segment_ids])
        attention_mask_t = torch.tensor([attention_mask])

        # Extract answer
        answer, start, end, confidence = qa_model.extract_answer(
            input_ids, segment_ids_t, attention_mask_t, tokenizer
        )

        print(f"\nExtracted Answer: '{answer}'")
        print(f"Position: [{start}, {end}]")
        print(f"Confidence: {confidence:.3f}")

        # Show token-level detail
        print(f"\nToken-level detail:")
        tokens = []
        for j, tid in enumerate(token_ids):
            if attention_mask[j] == 0:
                break
            token = tokenizer.inv_vocab.get(tid, '[UNK]')
            marker = " <--" if start <= j <= end else ""
            print(f"  Pos {j:2d}: {token:15s} (segment: {segment_ids[j]}){marker}")

    print("\n" + "=" * 80)
    print("✓ Step 3 Complete: Answer extractor working!")
    print("=" * 80)
    print("\nNOTE: This is a randomly initialized model for demonstration.")
    print("In practice, you would:")
    print("  1. Pre-train on large corpus (like BERT)")
    print("  2. Fine-tune on QA dataset (like SQuAD)")
    print("  3. Achieve 80-90% accuracy on test set")

    return qa_model, tokenizer


if __name__ == "__main__":
    qa_model, tokenizer = demonstrate_answer_extraction()
