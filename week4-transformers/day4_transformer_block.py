"""
Day 4: Complete Transformer Block
==================================
Building a full transformer block with all components.

Learning Goals:
--------------
1. Combine multi-head attention with feed-forward network
2. Understand residual connections and layer normalization
3. Build encoder and decoder blocks
4. See how blocks stack

Run: python day4_transformer_block.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class MultiHeadAttention(nn.Module):
    """Multi-head attention (from Day 3)."""
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

    def split_heads(self, x):
        batch_size, seq_len, d_model = x.shape
        x = x.view(batch_size, seq_len, self.num_heads, self.d_k)
        return x.transpose(1, 2)

    def combine_heads(self, x):
        batch_size, num_heads, seq_len, d_k = x.shape
        x = x.transpose(1, 2)
        return x.contiguous().view(batch_size, seq_len, self.d_model)

    def forward(self, query, key, value, mask=None):
        Q = self.split_heads(self.W_q(query))
        K = self.split_heads(self.W_k(key))
        V = self.split_heads(self.W_v(value))

        scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(self.d_k)

        if mask is not None:
            scores = scores.masked_fill(mask == 0, float('-inf'))

        attention_weights = F.softmax(scores, dim=-1)
        attention_weights = self.dropout(attention_weights)

        attended = torch.matmul(attention_weights, V)
        attended = self.combine_heads(attended)

        return self.W_o(attended), attention_weights


class FeedForward(nn.Module):
    """
    Position-wise feed-forward network.
    FFN(x) = max(0, xW1 + b1)W2 + b2
    """
    def __init__(self, d_model, d_ff, dropout=0.1):
        """
        Args:
            d_model: Model dimension (e.g., 512)
            d_ff: Hidden dimension (typically 4 * d_model = 2048)
            dropout: Dropout probability
        """
        super().__init__()
        self.linear1 = nn.Linear(d_model, d_ff)
        self.linear2 = nn.Linear(d_ff, d_model)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        Returns:
            (batch, seq_len, d_model)
        """
        # First linear + ReLU
        x = F.relu(self.linear1(x))
        x = self.dropout(x)

        # Second linear
        x = self.linear2(x)
        return x


class TransformerEncoderBlock(nn.Module):
    """
    A single transformer encoder block.
    Components: Multi-head attention + Feed-forward + Residuals + Layer norms
    """
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        """
        Args:
            d_model: Model dimension
            num_heads: Number of attention heads
            d_ff: Feed-forward hidden dimension
            dropout: Dropout probability
        """
        super().__init__()

        # Multi-head self-attention
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)

        # Feed-forward network
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        # Dropout
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        """
        Args:
            x: Input (batch, seq_len, d_model)
            mask: Optional attention mask

        Returns:
            Output (batch, seq_len, d_model)
        """
        # 1. Multi-head self-attention with residual and layer norm
        attn_output, _ = self.self_attn(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))  # Residual + LayerNorm

        # 2. Feed-forward with residual and layer norm
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))  # Residual + LayerNorm

        return x


class TransformerDecoderBlock(nn.Module):
    """
    A single transformer decoder block.
    Components: Masked self-attention + Cross-attention + Feed-forward + Residuals + Layer norms
    """
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        # Masked self-attention
        self.self_attn = MultiHeadAttention(d_model, num_heads, dropout)

        # Cross-attention (encoder-decoder attention)
        self.cross_attn = MultiHeadAttention(d_model, num_heads, dropout)

        # Feed-forward network
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

        # Layer normalizations
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.norm3 = nn.LayerNorm(d_model)

        # Dropout
        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)
        self.dropout3 = nn.Dropout(dropout)

    def forward(self, x, encoder_output, src_mask=None, tgt_mask=None):
        """
        Args:
            x: Target input (batch, tgt_len, d_model)
            encoder_output: Encoder output (batch, src_len, d_model)
            src_mask: Source attention mask
            tgt_mask: Target attention mask (causal)

        Returns:
            Output (batch, tgt_len, d_model)
        """
        # 1. Masked self-attention
        self_attn_output, _ = self.self_attn(x, x, x, tgt_mask)
        x = self.norm1(x + self.dropout1(self_attn_output))

        # 2. Cross-attention (Q from decoder, K,V from encoder)
        cross_attn_output, _ = self.cross_attn(x, encoder_output, encoder_output, src_mask)
        x = self.norm2(x + self.dropout2(cross_attn_output))

        # 3. Feed-forward
        ff_output = self.feed_forward(x)
        x = self.norm3(x + self.dropout3(ff_output))

        return x


def demonstrate_encoder_block():
    """
    Demonstrate encoder block (BERT-style).
    """
    print("=" * 80)
    print("TRANSFORMER ENCODER BLOCK (BERT-style)")
    print("=" * 80)

    # Configuration
    batch_size = 2
    seq_len = 5
    d_model = 64
    num_heads = 8
    d_ff = 256  # 4 * d_model

    print(f"\nConfiguration:")
    print(f"  d_model = {d_model}")
    print(f"  num_heads = {num_heads}")
    print(f"  d_ff = {d_ff} (4 × d_model)")
    print(f"  seq_len = {seq_len}")
    print(f"  batch_size = {batch_size}")

    # Create encoder block
    encoder_block = TransformerEncoderBlock(d_model, num_heads, d_ff)

    # Count parameters
    total_params = sum(p.numel() for p in encoder_block.parameters())
    print(f"\nTotal parameters in one encoder block: {total_params:,}")

    # Create input
    torch.manual_seed(42)
    x = torch.randn(batch_size, seq_len, d_model)

    print(f"\nInput shape: {x.shape}")

    # Forward pass
    output = encoder_block(x)

    print(f"Output shape: {output.shape}")
    print(f"\n✓ Input and output have the same shape!")
    print("  This allows stacking multiple encoder blocks")

    # Show data flow
    print("\n" + "-" * 80)
    print("DATA FLOW THROUGH ENCODER BLOCK:")
    print("-" * 80)
    print("""
1. Input: (batch, seq_len, d_model)
   ↓
2. Multi-Head Self-Attention
   ↓
3. Add & Norm (Residual + LayerNorm)
   ↓
4. Feed-Forward Network (d_model → d_ff → d_model)
   ↓
5. Add & Norm (Residual + LayerNorm)
   ↓
6. Output: (batch, seq_len, d_model) - same shape as input!

Each encoder block refines the representations.
BERT-base: Stack 12 of these blocks
GPT-2: Stack 12-48 of these (decoder variant)
""")


def demonstrate_decoder_block():
    """
    Demonstrate decoder block (used in translation).
    """
    print("\n\n" + "=" * 80)
    print("TRANSFORMER DECODER BLOCK (Translation)")
    print("=" * 80)

    # Configuration
    batch_size = 2
    src_len = 6  # Source sentence length
    tgt_len = 5  # Target sentence length
    d_model = 64
    num_heads = 8
    d_ff = 256

    print(f"\nConfiguration:")
    print(f"  Source length = {src_len} (e.g., English)")
    print(f"  Target length = {tgt_len} (e.g., French)")
    print(f"  d_model = {d_model}")

    # Create decoder block
    decoder_block = TransformerDecoderBlock(d_model, num_heads, d_ff)

    # Count parameters
    total_params = sum(p.numel() for p in decoder_block.parameters())
    print(f"\nTotal parameters in one decoder block: {total_params:,}")

    # Create inputs
    torch.manual_seed(42)
    target_input = torch.randn(batch_size, tgt_len, d_model)  # Decoder input
    encoder_output = torch.randn(batch_size, src_len, d_model)  # From encoder

    # Create causal mask for target (prevent looking at future)
    tgt_mask = torch.tril(torch.ones(tgt_len, tgt_len))
    tgt_mask = tgt_mask.unsqueeze(0).unsqueeze(0)  # (1, 1, tgt_len, tgt_len)

    print(f"\nTarget input shape: {target_input.shape}")
    print(f"Encoder output shape: {encoder_output.shape}")
    print(f"Causal mask shape: {tgt_mask.shape}")

    # Forward pass
    output = decoder_block(target_input, encoder_output, tgt_mask=tgt_mask)

    print(f"Output shape: {output.shape}")

    # Show data flow
    print("\n" + "-" * 80)
    print("DATA FLOW THROUGH DECODER BLOCK:")
    print("-" * 80)
    print("""
1. Target Input: (batch, tgt_len, d_model)
   ↓
2. Masked Self-Attention (can't see future)
   ↓
3. Add & Norm
   ↓
4. Cross-Attention (Q from decoder, K,V from encoder)
   ↓
5. Add & Norm
   ↓
6. Feed-Forward Network
   ↓
7. Add & Norm
   ↓
8. Output: (batch, tgt_len, d_model)

This allows the decoder to:
  - Attend to previously generated tokens (masked self-attention)
  - Attend to the source sentence (cross-attention)
""")


def demonstrate_residual_connections():
    """
    Show importance of residual connections.
    """
    print("\n\n" + "=" * 80)
    print("RESIDUAL CONNECTIONS: Why They Matter")
    print("=" * 80)

    d_model = 64
    batch_size = 1
    seq_len = 5

    # Create input
    torch.manual_seed(42)
    x = torch.randn(batch_size, seq_len, d_model)

    # Simple transformation (like attention or FFN)
    transform = nn.Linear(d_model, d_model)

    # Without residual
    output_no_residual = transform(x)

    # With residual
    output_with_residual = x + transform(x)

    print("\nWithout residual:")
    print(f"  Output = Transform(x)")
    print(f"  If Transform outputs zeros, we lose all information!")

    print("\nWith residual:")
    print(f"  Output = x + Transform(x)")
    print(f"  Even if Transform outputs zeros, we still have x!")

    print("\n" + "-" * 80)
    print("WHY RESIDUALS ARE CRITICAL:")
    print("-" * 80)
    print("""
1. GRADIENT FLOW: Allows gradients to flow directly through the network
   - Without residuals: Gradient must flow through many transformations
   - With residuals: Gradient has a direct path backward

2. LEARNING IDENTITY: Network can learn to "do nothing" if needed
   - If Transform(x) = 0, then output = x (identity mapping)

3. DEEP NETWORKS: Enables training of very deep networks (100+ layers)
   - ResNet paper showed this enables ImageNet training
   - Transformers use same idea

4. INITIALIZATION: Better gradient magnitudes at initialization
   - Prevents vanishing/exploding gradients

Formula: LayerNorm(x + Sublayer(x))
  - Sublayer = attention or feed-forward
  - Add before or after norm (both work, pre-norm is common)
""")


def main():
    """
    Run all demonstrations.
    """
    # Encoder block
    demonstrate_encoder_block()

    # Decoder block
    demonstrate_decoder_block()

    # Residual connections
    demonstrate_residual_connections()

    print("\n\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. Transformer block = Attention + FFN + Residuals + LayerNorm
2. Encoder block: Self-attention only (bidirectional)
3. Decoder block: Masked self-attention + Cross-attention
4. Residual connections are crucial for deep networks
5. Layer normalization stabilizes training

Parameter counts (d_model=512, d_ff=2048):
  - Multi-head attention: ~2M parameters
  - Feed-forward: ~4M parameters
  - Total per block: ~7M parameters
  - GPT-3 (96 layers): ~650M parameters just for transformer blocks!

Next: Day 5 - Compare different architectures (BERT vs GPT vs T5)
""")


if __name__ == "__main__":
    main()
