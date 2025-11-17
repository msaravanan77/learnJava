"""
Day 2: Self-Attention Deep Dive
================================
Implementing and visualizing self-attention with real examples.

Learning Goals:
--------------
1. Understand self-attention (Q=K=V from same source)
2. See how context affects word representations
3. Visualize attention patterns for different sentences
4. Compare to traditional embeddings

Run: python day2_self_attention.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class SelfAttention(nn.Module):
    """
    Self-Attention layer where Q, K, V all come from the same input.
    """
    def __init__(self, d_model, d_k=None):
        """
        Args:
            d_model: Input/output dimension
            d_k: Dimension for Q and K (default: d_model)
        """
        super().__init__()
        self.d_model = d_model
        self.d_k = d_k if d_k is not None else d_model

        # Projection matrices
        self.W_q = nn.Linear(d_model, self.d_k, bias=False)
        self.W_k = nn.Linear(d_model, self.d_k, bias=False)
        self.W_v = nn.Linear(d_model, d_model, bias=False)

    def forward(self, x, mask=None):
        """
        Args:
            x: Input embeddings (batch, seq_len, d_model)
            mask: Optional attention mask (batch, seq_len, seq_len)

        Returns:
            output: Contextualized representations (batch, seq_len, d_model)
            attention_weights: Attention matrix (batch, seq_len, seq_len)
        """
        batch_size, seq_len, _ = x.shape

        # Project to Q, K, V
        Q = self.W_q(x)  # (batch, seq_len, d_k)
        K = self.W_k(x)  # (batch, seq_len, d_k)
        V = self.W_v(x)  # (batch, seq_len, d_model)

        # Compute attention scores
        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        # Apply mask if provided
        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        # Softmax to get attention probabilities
        attention_weights = F.softmax(scores, dim=-1)

        # Apply attention to values
        output = torch.matmul(attention_weights, V)

        return output, attention_weights


def demonstrate_pronoun_resolution():
    """
    Classic example: "The animal didn't cross the street because it was too tired"
    What does "it" refer to? Attention should show us!
    """
    print("=" * 80)
    print("PRONOUN RESOLUTION WITH SELF-ATTENTION")
    print("=" * 80)

    # Sentence: "The animal didn't cross the street because it was too tired"
    # Simplified to 6 words for clarity
    sentence = ["animal", "cross", "street", "because", "it", "tired"]

    print(f"\nSentence: {' '.join(sentence)}")
    print("\nQuestion: What does 'it' refer to?")
    print("Expected: 'it' should attend strongly to 'animal' (not 'street')")

    # Create simple embeddings (in real use, these would be from word2vec/BERT)
    # We'll make "it" and "animal" embeddings similar to help attention learn
    d_model = 16
    seq_len = len(sentence)

    torch.manual_seed(42)
    embeddings = torch.randn(1, seq_len, d_model)

    # Make "it" (pos 4) and "animal" (pos 0) more similar
    embeddings[0, 4] = embeddings[0, 0] * 0.7 + embeddings[0, 4] * 0.3

    # Create self-attention module
    self_attn = SelfAttention(d_model)

    # Apply self-attention
    output, attention_weights = self_attn(embeddings)

    # Extract attention for "it" (position 4)
    it_attention = attention_weights[0, 4].detach()

    print("\n" + "-" * 80)
    print("ATTENTION WEIGHTS FOR 'it' (position 4):")
    print("-" * 80)
    for i, word in enumerate(sentence):
        bar = "█" * int(it_attention[i] * 100)
        print(f"{word:>10}: {it_attention[i]:.4f} {bar}")

    print("\nInterpretation:")
    max_idx = it_attention.argmax().item()
    print(f"  'it' attends most strongly to '{sentence[max_idx]}' (position {max_idx})")
    print(f"  This helps the model understand what 'it' refers to!")


def demonstrate_syntax_patterns():
    """
    Show how attention captures syntactic relationships.
    """
    print("\n\n" + "=" * 80)
    print("SYNTACTIC PATTERNS IN ATTENTION")
    print("=" * 80)

    # Simple sentence with clear syntax: "The quick brown fox jumps"
    sentence = ["The", "quick", "brown", "fox", "jumps"]

    print(f"\nSentence: {' '.join(sentence)}")
    print("\nWe expect:")
    print("  - 'fox' should attend to adjectives 'quick' and 'brown'")
    print("  - 'jumps' should attend to subject 'fox'")

    # Create embeddings
    d_model = 16
    seq_len = len(sentence)

    torch.manual_seed(123)
    embeddings = torch.randn(1, seq_len, d_model)

    # Create self-attention
    self_attn = SelfAttention(d_model)

    # Apply
    output, attention_weights = self_attn(embeddings)

    # Visualize full attention matrix
    print("\n" + "-" * 80)
    print("FULL ATTENTION MATRIX:")
    print("-" * 80)
    print(f"         {' '.join([f'{w:>7}' for w in sentence])}")

    attn_matrix = attention_weights[0].detach()
    for i, word in enumerate(sentence):
        row = attn_matrix[i]
        values = ' '.join([f'{v:7.3f}' for v in row])
        print(f"{word:>7}: {values}")

    print("\nObservations:")
    print("  - Each row shows where that word 'looks'")
    print("  - Diagonal values show self-attention (word attending to itself)")
    print("  - Off-diagonal patterns reveal syntactic/semantic relationships")


def compare_before_after_attention():
    """
    Compare word representations before and after self-attention.
    """
    print("\n\n" + "=" * 80)
    print("CONTEXTUALIZATION: BEFORE vs AFTER SELF-ATTENTION")
    print("=" * 80)

    # Example showing how context changes meaning
    # "bank" has different meanings in these contexts
    sentence1 = ["river", "bank"]  # geographical bank
    sentence2 = ["money", "bank"]  # financial bank

    d_model = 8

    # Create initial embeddings where "bank" is identical in both sentences
    torch.manual_seed(42)
    bank_embedding = torch.randn(1, 1, d_model)

    # Sentence 1: "river bank"
    river_embedding = torch.randn(1, 1, d_model)
    sent1_embeddings = torch.cat([river_embedding, bank_embedding], dim=1)

    # Sentence 2: "money bank"
    money_embedding = torch.randn(1, 1, d_model)
    sent2_embeddings = torch.cat([money_embedding, bank_embedding], dim=1)

    print("\nBEFORE Self-Attention:")
    print("  'bank' in 'river bank' and 'money bank' have IDENTICAL embeddings")
    print(f"  Cosine similarity: {F.cosine_similarity(bank_embedding, bank_embedding, dim=-1).item():.4f}")

    # Apply self-attention to both sentences
    self_attn = SelfAttention(d_model)

    sent1_output, _ = self_attn(sent1_embeddings)
    sent2_output, _ = self_attn(sent2_embeddings)

    # Extract "bank" representations after attention (position 1)
    bank_river_context = sent1_output[0, 1]
    bank_money_context = sent2_output[0, 1]

    similarity = F.cosine_similarity(
        bank_river_context.unsqueeze(0),
        bank_money_context.unsqueeze(0),
        dim=-1
    ).item()

    print("\nAFTER Self-Attention:")
    print("  'bank' in 'river bank' and 'money bank' have DIFFERENT embeddings!")
    print(f"  Cosine similarity: {similarity:.4f}")
    print("\n  This is CONTEXTUALIZATION - the same word gets different")
    print("  representations based on its context!")


def main():
    """
    Run all demonstrations.
    """
    # Pronoun resolution
    demonstrate_pronoun_resolution()

    # Syntactic patterns
    demonstrate_syntax_patterns()

    # Contextualization
    compare_before_after_attention()

    print("\n\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Self-attention makes Q=K=V all come from the same input
2. It captures relationships between all positions in the sequence
3. Attention patterns emerge that correspond to syntax and semantics
4. The same word gets different representations based on context
5. This is why BERT embeddings are more powerful than word2vec!

Mathematical insight:
  - Output[i] = Σ(attention_weights[i,j] * V[j]) for all j
  - Each output is a weighted sum of ALL input values
  - Weights are learned based on Q-K similarity

Next: Day 3 - Multi-Head Attention (run multiple attentions in parallel)
""")


if __name__ == "__main__":
    main()
