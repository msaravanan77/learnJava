"""
Step 2: Build BERT-style Encoder
=================================
Build the transformer encoder using components from Week 4.

This step:
- Creates a BERT-style encoder from scratch
- Adds embeddings (token + position + segment)
- Implements the encoding pipeline
- Encodes questions and documents

Run: python step2_build_encoder.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math
from typing import List, Tuple


class BERTEmbeddings(nn.Module):
    """
    BERT-style embeddings: Token + Position + Segment.
    """
    def __init__(self, vocab_size, d_model, max_position=512, dropout=0.1):
        super().__init__()

        self.token_embeddings = nn.Embedding(vocab_size, d_model)
        self.position_embeddings = nn.Embedding(max_position, d_model)
        self.segment_embeddings = nn.Embedding(2, d_model)  # 0 for question, 1 for document

        self.layer_norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)

        # Initialize position IDs
        self.register_buffer("position_ids", torch.arange(max_position).expand((1, -1)))

    def forward(self, input_ids, segment_ids=None):
        """
        Args:
            input_ids: (batch, seq_len) - Token IDs
            segment_ids: (batch, seq_len) - Segment IDs (0 or 1)

        Returns:
            (batch, seq_len, d_model) - Combined embeddings
        """
        batch_size, seq_len = input_ids.shape

        # Token embeddings
        token_emb = self.token_embeddings(input_ids)

        # Position embeddings
        position_ids = self.position_ids[:, :seq_len]
        position_emb = self.position_embeddings(position_ids)

        # Segment embeddings
        if segment_ids is None:
            segment_ids = torch.zeros_like(input_ids)
        segment_emb = self.segment_embeddings(segment_ids)

        # Combine all embeddings
        embeddings = token_emb + position_emb + segment_emb

        embeddings = self.layer_norm(embeddings)
        embeddings = self.dropout(embeddings)

        return embeddings


class MultiHeadAttention(nn.Module):
    """Multi-head attention from Week 4."""
    def __init__(self, d_model, num_heads, dropout=0.1):
        super().__init__()
        assert d_model % num_heads == 0

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads

        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def forward(self, query, key, value, mask=None):
        batch_size = query.size(0)

        # Linear projections and split heads
        Q = self.W_q(query).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        K = self.W_k(key).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)
        V = self.W_v(value).view(batch_size, -1, self.num_heads, self.d_k).transpose(1, 2)

        # Scaled dot-product attention
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        attended = torch.matmul(attention_weights, V)

        # Combine heads
        attended = attended.transpose(1, 2).contiguous().view(batch_size, -1, self.d_model)

        return self.W_o(attended)


class FeedForward(nn.Module):
    """Feed-forward network from Week 4."""
    def __init__(self, d_model, d_ff, dropout=0.1):
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.dropout(x)
        x = self.linear2(x)
        return x


class TransformerEncoderBlock(nn.Module):
    """Single transformer encoder block."""
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Self-attention
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # Feed-forward
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))

        return x


class BERTEncoder(nn.Module):
    """
    Complete BERT-style encoder for QA system.
    """
    def __init__(self, vocab_size, d_model=768, num_heads=12, num_layers=12,
                 d_ff=3072, max_position=512, dropout=0.1):
        """
        Args:
            vocab_size: Vocabulary size
            d_model: Model dimension (768 for BERT-base)
            num_heads: Number of attention heads (12 for BERT-base)
            num_layers: Number of encoder blocks (12 for BERT-base)
            d_ff: Feed-forward dimension (3072 for BERT-base)
            max_position: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()

        self.d_model = d_model

        # Embeddings
        self.embeddings = BERTEmbeddings(vocab_size, d_model, max_position, dropout)

        # Encoder blocks
        self.encoder_blocks = nn.ModuleList([
            TransformerEncoderBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

    def forward(self, input_ids, segment_ids=None, attention_mask=None):
        """
        Args:
            input_ids: (batch, seq_len) - Token IDs
            segment_ids: (batch, seq_len) - Segment IDs
            attention_mask: (batch, seq_len) - Attention mask (1 for real tokens, 0 for padding)

        Returns:
            (batch, seq_len, d_model) - Contextualized embeddings
        """
        # Get embeddings
        x = self.embeddings(input_ids, segment_ids)

        # Prepare attention mask
        if attention_mask is not None:
            # Convert to (batch, 1, 1, seq_len) for broadcasting
            attention_mask = attention_mask.unsqueeze(1).unsqueeze(2)

        # Pass through encoder blocks
        for block in self.encoder_blocks:
            x = block(x, attention_mask)

        return x


class SimpleTokenizer:
    """
    Simple word-based tokenizer for demonstration.
    In production, use WordPiece/BPE tokenizers.
    """
    def __init__(self):
        self.vocab = {}
        self.inv_vocab = {}

        # Special tokens
        self.pad_token = '[PAD]'
        self.cls_token = '[CLS]'
        self.sep_token = '[SEP]'
        self.unk_token = '[UNK]'

        self.pad_id = 0
        self.cls_id = 1
        self.sep_id = 2
        self.unk_id = 3

        self._add_special_tokens()

    def _add_special_tokens(self):
        """Add special tokens to vocabulary."""
        special_tokens = [self.pad_token, self.cls_token, self.sep_token, self.unk_token]
        for i, token in enumerate(special_tokens):
            self.vocab[token] = i
            self.inv_vocab[i] = token

    def fit(self, texts: List[str]):
        """Build vocabulary from texts."""
        vocab_idx = len(self.vocab)

        for text in texts:
            words = text.lower().split()
            for word in words:
                if word not in self.vocab:
                    self.vocab[word] = vocab_idx
                    self.inv_vocab[vocab_idx] = word
                    vocab_idx += 1

        print(f"Vocabulary size: {len(self.vocab)}")

    def encode(self, text: str, max_length: int = 512) -> Tuple[List[int], List[int]]:
        """
        Encode text to token IDs.

        Returns:
            (token_ids, attention_mask)
        """
        words = text.lower().split()
        token_ids = [self.cls_id]  # Start with [CLS]

        for word in words:
            if len(token_ids) >= max_length - 1:  # Leave room for [SEP]
                break
            token_ids.append(self.vocab.get(word, self.unk_id))

        token_ids.append(self.sep_id)  # End with [SEP]

        # Create attention mask (1 for real tokens)
        attention_mask = [1] * len(token_ids)

        # Pad to max_length
        while len(token_ids) < max_length:
            token_ids.append(self.pad_id)
            attention_mask.append(0)

        return token_ids, attention_mask

    def encode_pair(self, text_a: str, text_b: str, max_length: int = 512):
        """
        Encode a pair of texts (question + document).

        Returns:
            (token_ids, segment_ids, attention_mask)
        """
        words_a = text_a.lower().split()
        words_b = text_b.lower().split()

        token_ids = [self.cls_id]
        segment_ids = [0]

        # Add text_a
        for word in words_a:
            if len(token_ids) >= max_length - 2:  # Room for [SEP]s
                break
            token_ids.append(self.vocab.get(word, self.unk_id))
            segment_ids.append(0)

        token_ids.append(self.sep_id)
        segment_ids.append(0)

        # Add text_b
        for word in words_b:
            if len(token_ids) >= max_length - 1:  # Room for final [SEP]
                break
            token_ids.append(self.vocab.get(word, self.unk_id))
            segment_ids.append(1)

        token_ids.append(self.sep_id)
        segment_ids.append(1)

        # Attention mask
        attention_mask = [1] * len(token_ids)

        # Pad
        while len(token_ids) < max_length:
            token_ids.append(self.pad_id)
            segment_ids.append(0)
            attention_mask.append(0)

        return token_ids, segment_ids, attention_mask


def demonstrate_encoder():
    """
    Demonstrate the BERT encoder.
    """
    print("=" * 80)
    print("STEP 2: BERT ENCODER DEMONSTRATION")
    print("=" * 80)

    # Create tokenizer and build vocabulary
    print("\n1. Creating tokenizer...")
    tokenizer = SimpleTokenizer()

    sample_texts = [
        "what is attention mechanism",
        "transformers use attention to process sequences",
        "BERT is a bidirectional encoder",
        "attention allows models to focus on relevant information"
    ]

    tokenizer.fit(sample_texts)

    # Create encoder (mini version for demo)
    print("\n2. Creating BERT encoder...")
    vocab_size = len(tokenizer.vocab)
    encoder = BERTEncoder(
        vocab_size=vocab_size,
        d_model=256,      # Smaller for demo (BERT-base: 768)
        num_heads=8,      # (BERT-base: 12)
        num_layers=4,     # (BERT-base: 12)
        d_ff=1024,        # (BERT-base: 3072)
        max_position=512
    )

    total_params = sum(p.numel() for p in encoder.parameters())
    print(f"   Model parameters: {total_params:,}")

    # Encode a question-document pair
    print("\n3. Encoding question-document pair...")

    question = "What is attention?"
    document = "Attention is a mechanism that allows models to focus on relevant parts."

    print(f"\n   Question: '{question}'")
    print(f"   Document: '{document}'")

    # Tokenize
    token_ids, segment_ids, attention_mask = tokenizer.encode_pair(question, document, max_length=128)

    print(f"\n   Token IDs: {token_ids[:20]}... (length: {sum(attention_mask)})")
    print(f"   Segment IDs: {segment_ids[:20]}...")
    print(f"   Attention mask: {attention_mask[:20]}...")

    # Convert to tensors
    input_ids = torch.tensor([token_ids])
    segment_ids_t = torch.tensor([segment_ids])
    attention_mask_t = torch.tensor([attention_mask])

    # Encode
    print("\n4. Running through encoder...")
    encoder.eval()
    with torch.no_grad():
        encoded = encoder(input_ids, segment_ids_t, attention_mask_t)

    print(f"   Output shape: {encoded.shape}")
    print(f"   (batch=1, seq_len={sum(attention_mask)}, d_model=256)")

    # Show some embeddings
    print("\n5. Sample contextualized embeddings:")
    print(f"   [CLS] token: {encoded[0, 0, :5].tolist()}... (first 5 dims)")
    print(f"   First word:  {encoded[0, 1, :5].tolist()}...")

    print("\n" + "=" * 80)
    print("✓ Step 2 Complete: Encoder built and ready to encode Q&A pairs!")
    print("=" * 80)

    return encoder, tokenizer


if __name__ == "__main__":
    encoder, tokenizer = demonstrate_encoder()
