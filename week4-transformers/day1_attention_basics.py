"""
Day 1: Attention Mechanism from Scratch
========================================
Understanding the fundamental Query-Key-Value mechanism that powers all transformers.

Learning Goals:
--------------
1. Implement attention mechanism from scratch (no PyTorch nn.MultiheadAttention)
2. Understand Q, K, V transformations
3. See how attention scores are computed
4. Visualize attention weights

Run: python day1_attention_basics.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    The core attention mechanism.

    Args:
        Q: Query matrix (batch, seq_len, d_k)
        K: Key matrix   (batch, seq_len, d_k)
        V: Value matrix (batch, seq_len, d_v)
        mask: Optional mask (batch, seq_len, seq_len) - 0 where we can attend, -inf where we can't

    Returns:
        output: Attended values (batch, seq_len, d_v)
        attention_weights: Attention probabilities (batch, seq_len, seq_len)
    """
    # Step 1: Compute attention scores (Q @ K^T)
    d_k = Q.size(-1)
    scores = torch.matmul(Q, K.transpose(-2, -1))  # (batch, seq_len, seq_len)

    # Step 2: Scale by sqrt(d_k) to prevent gradients from exploding
    scores = scores / math.sqrt(d_k)

    # Step 3: Apply mask if provided (for causal attention)
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # Step 4: Apply softmax to get attention probabilities
    attention_weights = F.softmax(scores, dim=-1)  # (batch, seq_len, seq_len)

    # Step 5: Apply attention to values
    output = torch.matmul(attention_weights, V)  # (batch, seq_len, d_v)

    return output, attention_weights


class SimpleAttention(nn.Module):
    """
    Single-head attention mechanism.
    """
    def __init__(self, d_model):
        """
        Args:
            d_model: Dimension of the model (e.g., 512)
        """
        super().__init__()
        self.d_model = d_model

        # Linear transformations for Q, K, V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

    def forward(self, query, key, value, mask=None):
        """
        Args:
            query: Query embeddings (batch, seq_len, d_model)
            key: Key embeddings (batch, seq_len, d_model)
            value: Value embeddings (batch, seq_len, d_model)
            mask: Optional attention mask

        Returns:
            output: Attention output (batch, seq_len, d_model)
            attention_weights: Attention probabilities (batch, seq_len, seq_len)
        """
        # Transform inputs to Q, K, V
        Q = self.W_q(query)  # (batch, seq_len, d_model)
        K = self.W_k(key)    # (batch, seq_len, d_model)
        V = self.W_v(value)  # (batch, seq_len, d_model)

        # Apply attention
        output, attention_weights = scaled_dot_product_attention(Q, K, V, mask)

        return output, attention_weights


def demonstrate_attention():
    """
    Demonstrate attention mechanism with a concrete example.
    """
    print("=" * 80)
    print("ATTENTION MECHANISM DEMONSTRATION")
    print("=" * 80)

    # Setup
    batch_size = 1
    seq_len = 4
    d_model = 8

    # Create a simple sentence embedding (imagine: "The cat sat there")
    # We'll create embeddings where position 2 ("sat") should attend to position 1 ("cat")
    torch.manual_seed(42)
    sentence_embeddings = torch.randn(batch_size, seq_len, d_model)

    print(f"\n1. Input Embeddings Shape: {sentence_embeddings.shape}")
    print(f"   (batch={batch_size}, seq_len={seq_len}, d_model={d_model})")

    # Create attention module
    attention = SimpleAttention(d_model)

    # Apply self-attention (query = key = value = input)
    print("\n2. Applying Self-Attention...")
    output, attention_weights = attention(
        query=sentence_embeddings,
        key=sentence_embeddings,
        value=sentence_embeddings
    )

    print(f"\n3. Output Shape: {output.shape}")
    print(f"   (same as input - each position is now contextualized)")

    print(f"\n4. Attention Weights Shape: {attention_weights.shape}")
    print(f"   (batch={batch_size}, seq_len={seq_len}, seq_len={seq_len})")

    # Visualize attention matrix
    print("\n5. Attention Matrix (who attends to whom):")
    print("   Rows = Query positions, Columns = Key positions")
    print("   Each row sums to 1.0 (softmax property)")
    print()
    attention_matrix = attention_weights[0].detach()

    # Print with labels
    positions = ["The", "cat", "sat", "there"]
    print(f"         {' '.join([f'{p:>6}' for p in positions])}")
    for i, pos in enumerate(positions):
        row = attention_matrix[i]
        print(f"{pos:>6}: {' '.join([f'{val:6.3f}' for val in row])}")

    print("\n6. Interpretation:")
    print("   - Each row shows where that word 'looks' (attends to)")
    print("   - Higher values = stronger attention")
    print("   - In self-attention, each word attends to ALL words (including itself)")

    # Verify softmax property
    row_sums = attention_matrix.sum(dim=1)
    print(f"\n7. Verification - Each row sums to 1.0:")
    for i, pos in enumerate(positions):
        print(f"   {pos}: {row_sums[i]:.6f}")


def demonstrate_causal_attention():
    """
    Demonstrate causal (masked) attention used in GPT.
    """
    print("\n\n" + "=" * 80)
    print("CAUSAL ATTENTION (GPT-STYLE)")
    print("=" * 80)

    batch_size = 1
    seq_len = 4
    d_model = 8

    # Create input
    torch.manual_seed(42)
    sentence_embeddings = torch.randn(batch_size, seq_len, d_model)

    # Create causal mask (lower triangular matrix)
    # 1 where we can attend, 0 where we cannot
    causal_mask = torch.tril(torch.ones(seq_len, seq_len))

    print("\n1. Causal Mask (1=can attend, 0=cannot):")
    print(causal_mask)
    print("\n   This prevents positions from attending to future positions!")

    # Apply attention with mask
    attention = SimpleAttention(d_model)
    output, attention_weights = attention(
        query=sentence_embeddings,
        key=sentence_embeddings,
        value=sentence_embeddings,
        mask=causal_mask
    )

    # Visualize
    print("\n2. Causal Attention Matrix:")
    positions = ["The", "cat", "sat", "there"]
    attention_matrix = attention_weights[0].detach()

    print(f"         {' '.join([f'{p:>6}' for p in positions])}")
    for i, pos in enumerate(positions):
        row = attention_matrix[i]
        print(f"{pos:>6}: {' '.join([f'{val:6.3f}' for val in row])}")

    print("\n3. Notice the pattern:")
    print("   - 'The' (pos 0): Only attends to itself (can't see future)")
    print("   - 'cat' (pos 1): Attends to 'The' and 'cat' (no future)")
    print("   - 'sat' (pos 2): Attends to 'The', 'cat', 'sat' (no future)")
    print("   - 'there' (pos 3): Attends to all previous (full context)")
    print("\n   This is AUTOREGRESSIVE - essential for text generation!")


def main():
    """
    Run all demonstrations.
    """
    # Demonstrate basic attention
    demonstrate_attention()

    # Demonstrate causal attention
    demonstrate_causal_attention()

    print("\n\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Attention is Q @ K^T / sqrt(d_k), then softmax, then @ V
2. Attention weights tell us "who attends to whom"
3. Self-attention: Q=K=V (every word attends to every word)
4. Causal attention: Mask prevents looking at future positions
5. This simple mechanism powers ALL modern language models!

Next: Day 2 - Multi-Head Attention (multiple attention patterns in parallel)
""")


if __name__ == "__main__":
    main()
