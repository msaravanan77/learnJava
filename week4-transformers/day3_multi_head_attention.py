"""
Day 3: Multi-Head Attention
============================
Understanding why we use multiple attention heads in parallel.

Learning Goals:
--------------
1. Implement multi-head attention from scratch
2. Understand why multiple heads are better than one
3. See how different heads learn different patterns
4. Combine heads back together

Run: python day3_multi_head_attention.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class MultiHeadAttention(nn.Module):
    """
    Multi-Head Attention layer as used in Transformers.
    """
    def __init__(self, d_model, num_heads, dropout=0.1):
        """
        Args:
            d_model: Model dimension (e.g., 512)
            num_heads: Number of attention heads (e.g., 8)
            dropout: Dropout probability
        """
        super().__init__()
        assert d_model % num_heads == 0, "d_model must be divisible by num_heads"

        self.d_model = d_model
        self.num_heads = num_heads
        self.d_k = d_model // num_heads  # Dimension per head

        # Linear layers for Q, K, V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)

        # Output projection
        self.W_o = nn.Linear(d_model, d_model)

        self.dropout = nn.Dropout(dropout)

    def split_heads(self, x):
        """
        Split the last dimension into (num_heads, d_k).

        Args:
            x: (batch, seq_len, d_model)
        Returns:
            (batch, num_heads, seq_len, d_k)
        """
        batch_size, seq_len, d_model = x.shape
        x = x.view(batch_size, seq_len, self.num_heads, self.d_k)
        return x.transpose(1, 2)  # (batch, num_heads, seq_len, d_k)

    def combine_heads(self, x):
        """
        Combine heads back together.

        Args:
            x: (batch, num_heads, seq_len, d_k)
        Returns:
            (batch, seq_len, d_model)
        """
        batch_size, num_heads, seq_len, d_k = x.shape
        x = x.transpose(1, 2)  # (batch, seq_len, num_heads, d_k)
        return x.contiguous().view(batch_size, seq_len, self.d_model)

    def forward(self, query, key, value, mask=None):
        """
        Args:
            query, key, value: (batch, seq_len, d_model)
            mask: Optional mask (batch, 1, seq_len, seq_len)

        Returns:
            output: (batch, seq_len, d_model)
            attention_weights: (batch, num_heads, seq_len, seq_len)
        """
        batch_size = query.size(0)

        # 1. Linear projections
        Q = self.W_q(query)  # (batch, seq_len, d_model)
        K = self.W_k(key)
        V = self.W_v(value)

        # 2. Split into multiple heads
        Q = self.split_heads(Q)  # (batch, num_heads, seq_len, d_k)
        K = self.split_heads(K)
        V = self.split_heads(V)

        # 3. Scaled dot-product attention for each head
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        # Apply attention to values
        attended = torch.matmul(attention_weights, V)  # (batch, num_heads, seq_len, d_k)

        # 4. Combine heads
        attended = self.combine_heads(attended)  # (batch, seq_len, d_model)

        # 5. Final linear projection
        output = self.W_o(attended)

        return output, attention_weights


def demonstrate_multi_head_patterns():
    """
    Show how different heads learn different attention patterns.
    """
    print("=" * 80)
    print("MULTI-HEAD ATTENTION: Different Heads Learn Different Patterns")
    print("=" * 80)

    # Setup
    d_model = 64
    num_heads = 4
    seq_len = 6
    batch_size = 1

    # Sentence: "The quick brown fox jumps high"
    sentence = ["The", "quick", "brown", "fox", "jumps", "high"]

    print(f"\nSentence: {' '.join(sentence)}")
    print(f"\nConfiguration:")
    print(f"  d_model = {d_model}")
    print(f"  num_heads = {num_heads}")
    print(f"  d_k (per head) = {d_model // num_heads}")

    # Create input embeddings
    torch.manual_seed(42)
    embeddings = torch.randn(batch_size, seq_len, d_model)

    # Create multi-head attention
    mha = MultiHeadAttention(d_model, num_heads)

    # Apply
    output, attention_weights = mha(embeddings, embeddings, embeddings)

    print(f"\n" + "-" * 80)
    print("ATTENTION PATTERNS FOR EACH HEAD")
    print("-" * 80)

    # Visualize each head's attention pattern
    attn = attention_weights[0].detach()  # (num_heads, seq_len, seq_len)

    for head in range(num_heads):
        print(f"\nHead {head + 1}:")
        print(f"         {' '.join([f'{w:>7}' for w in sentence])}")

        for i, word in enumerate(sentence):
            row = attn[head, i]
            values = ' '.join([f'{v:7.3f}' for v in row])
            print(f"{word:>7}: {values}")

        # Find pattern
        avg_self_attn = torch.diagonal(attn[head]).mean().item()
        print(f"  → Average self-attention: {avg_self_attn:.3f}")

    print("\n" + "-" * 80)
    print("INTERPRETATION:")
    print("-" * 80)
    print("""
In real transformers, different heads specialize in different patterns:
  - Head 1: Might focus on POSITION (attend to nearby words)
  - Head 2: Might focus on SYNTAX (attend to syntactic dependencies)
  - Head 3: Might focus on SEMANTICS (attend to related meanings)
  - Head 4: Might focus on ENTITIES (attend to other mentions of same entity)

This is learned automatically during training - no explicit supervision!
""")


def compare_single_vs_multi_head():
    """
    Compare single-head vs multi-head attention.
    """
    print("\n" + "=" * 80)
    print("SINGLE HEAD vs MULTI-HEAD COMPARISON")
    print("=" * 80)

    d_model = 64
    seq_len = 5
    batch_size = 1

    # Create input
    torch.manual_seed(42)
    embeddings = torch.randn(batch_size, seq_len, d_model)

    # Single-head attention (num_heads=1)
    single_head = MultiHeadAttention(d_model, num_heads=1)
    single_output, single_attn = single_head(embeddings, embeddings, embeddings)

    # Multi-head attention (num_heads=8)
    multi_head = MultiHeadAttention(d_model, num_heads=8)
    multi_output, multi_attn = multi_head(embeddings, embeddings, embeddings)

    print("\nSingle-Head Attention:")
    print(f"  - Number of heads: 1")
    print(f"  - d_k per head: {d_model}")
    print(f"  - Attention pattern shape: {single_attn.shape}")
    print(f"  - Only ONE perspective on the data")

    print("\nMulti-Head Attention:")
    print(f"  - Number of heads: 8")
    print(f"  - d_k per head: {d_model // 8}")
    print(f"  - Attention pattern shape: {multi_attn.shape}")
    print(f"  - EIGHT different perspectives on the data!")

    print("\n" + "-" * 80)
    print("WHY IS MULTI-HEAD BETTER?")
    print("-" * 80)
    print("""
1. DIVERSE PATTERNS: Each head can learn different attention patterns
   - Some heads focus on position, others on syntax, others on semantics

2. REDUNDANCY: If one head fails, others can compensate
   - More robust to different types of inputs

3. EXPRESSIVITY: Can capture multiple relationships simultaneously
   - A word can attend strongly to BOTH its subject AND its object

4. COMPUTATIONAL: Same total parameters, but more flexible
   - 1 head of 512d vs 8 heads of 64d = same parameter count

5. EMPIRICAL: Multi-head consistently outperforms single-head
   - Original Transformer paper (Vaswani et al., 2017) showed this
""")


def demonstrate_head_concatenation():
    """
    Show how heads are concatenated and projected.
    """
    print("\n" + "=" * 80)
    print("HEAD CONCATENATION AND PROJECTION")
    print("=" * 80)

    d_model = 16
    num_heads = 4
    d_k = d_model // num_heads  # 4

    seq_len = 3
    batch_size = 1

    print(f"\nSetup:")
    print(f"  d_model = {d_model}")
    print(f"  num_heads = {num_heads}")
    print(f"  d_k (per head) = {d_k}")

    # Create dummy head outputs
    torch.manual_seed(42)
    head_outputs = torch.randn(batch_size, num_heads, seq_len, d_k)

    print(f"\nHead outputs shape: {head_outputs.shape}")
    print(f"  (batch, num_heads, seq_len, d_k)")

    # Transpose and reshape to concatenate heads
    # (batch, num_heads, seq_len, d_k) -> (batch, seq_len, num_heads, d_k)
    transposed = head_outputs.transpose(1, 2)
    print(f"\nAfter transpose: {transposed.shape}")

    # Concatenate by reshaping
    concatenated = transposed.contiguous().view(batch_size, seq_len, d_model)
    print(f"After concatenation: {concatenated.shape}")
    print(f"  (batch, seq_len, d_model) - heads are concatenated!")

    # Final projection
    W_o = nn.Linear(d_model, d_model)
    output = W_o(concatenated)

    print(f"\nAfter W_o projection: {output.shape}")
    print(f"  (batch, seq_len, d_model) - ready for next layer!")

    print("\n" + "-" * 80)
    print("SUMMARY: Multi-Head Attention Pipeline")
    print("-" * 80)
    print("""
1. Input: (batch, seq_len, d_model)
2. Linear projections to Q, K, V: (batch, seq_len, d_model)
3. Split heads: (batch, num_heads, seq_len, d_k)
4. Scaled dot-product attention PER HEAD
5. Concatenate heads: (batch, seq_len, d_model)
6. Final projection W_o: (batch, seq_len, d_model)
7. Output: same shape as input!
""")


def main():
    """
    Run all demonstrations.
    """
    # Different head patterns
    demonstrate_multi_head_patterns()

    # Single vs multi-head comparison
    compare_single_vs_multi_head()

    # Head concatenation
    demonstrate_head_concatenation()

    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Multi-head attention = Multiple attention mechanisms in parallel
2. Each head has dimension d_k = d_model / num_heads
3. Different heads learn different attention patterns (position, syntax, semantics)
4. Heads are concatenated and projected to get final output
5. Same parameter count as single-head, but much more expressive!

Typical configurations:
  - BERT-base: 12 heads, d_model=768, d_k=64
  - GPT-2: 12 heads, d_model=768, d_k=64
  - GPT-3: 96 heads, d_model=12288, d_k=128

Next: Day 4 - Complete Transformer Block (attention + feed-forward + residuals)
""")


if __name__ == "__main__":
    main()
