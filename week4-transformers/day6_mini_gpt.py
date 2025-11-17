"""
Day 6: Building a Mini-GPT
===========================
Implementing a small GPT model from scratch.

Learning Goals:
--------------
1. Combine all components into a complete GPT model
2. Add positional encoding
3. Implement token embedding and output head
4. Understand the full forward pass

Run: python day6_mini_gpt.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import math


class PositionalEncoding(nn.Module):
    """
    Sinusoidal positional encoding as in original Transformer paper.
    """
    def __init__(self, d_model, max_len=5000):
        super().__init__()

        # Create positional encoding matrix
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))

        pe[:, 0::2] = torch.sin(position * div_term)  # Even indices
        pe[:, 1::2] = torch.cos(position * div_term)  # Odd indices

        pe = pe.unsqueeze(0)  # (1, max_len, d_model)
        self.register_buffer('pe', pe)

    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, d_model)
        Returns:
            x with positional encoding added
        """
        seq_len = x.size(1)
        x = x + self.pe[:, :seq_len, :]
        return x


class MultiHeadAttention(nn.Module):
    """Multi-head attention mechanism."""
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

        return self.W_o(attended)


class FeedForward(nn.Module):
    """Position-wise feed-forward network."""
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


class GPTBlock(nn.Module):
    """
    A single GPT transformer block.
    """
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        self.attention = MultiHeadAttention(d_model, num_heads, dropout)
        self.feed_forward = FeedForward(d_model, d_ff, dropout)

        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        self.dropout1 = nn.Dropout(dropout)
        self.dropout2 = nn.Dropout(dropout)

    def forward(self, x, mask):
        """
        Args:
            x: (batch, seq_len, d_model)
            mask: Causal mask (batch, 1, seq_len, seq_len)

        Returns:
            (batch, seq_len, d_model)
        """
        # Self-attention with residual and layer norm
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout1(attn_output))

        # Feed-forward with residual and layer norm
        ff_output = self.feed_forward(x)
        x = self.norm2(x + self.dropout2(ff_output))

        return x


class MiniGPT(nn.Module):
    """
    A mini-GPT language model.

    Architecture:
      1. Token embedding
      2. Positional encoding
      3. N transformer blocks
      4. Language modeling head
    """
    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff, max_len=512, dropout=0.1):
        """
        Args:
            vocab_size: Vocabulary size
            d_model: Model dimension
            num_heads: Number of attention heads
            num_layers: Number of transformer blocks
            d_ff: Feed-forward hidden dimension
            max_len: Maximum sequence length
            dropout: Dropout probability
        """
        super().__init__()

        self.d_model = d_model

        # Token embedding
        self.token_embedding = nn.Embedding(vocab_size, d_model)

        # Positional encoding
        self.pos_encoding = PositionalEncoding(d_model, max_len)

        # Transformer blocks
        self.blocks = nn.ModuleList([
            GPTBlock(d_model, num_heads, d_ff, dropout)
            for _ in range(num_layers)
        ])

        # Output layer (language modeling head)
        self.ln_f = nn.LayerNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size)

        # Dropout
        self.dropout = nn.Dropout(dropout)

        # Initialize weights
        self.apply(self._init_weights)

    def _init_weights(self, module):
        """Initialize weights."""
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, input_ids):
        """
        Args:
            input_ids: (batch, seq_len) - Token indices

        Returns:
            logits: (batch, seq_len, vocab_size) - Next token predictions
        """
        batch_size, seq_len = input_ids.shape

        # 1. Token embeddings
        x = self.token_embedding(input_ids)  # (batch, seq_len, d_model)

        # Scale embeddings (as in original paper)
        x = x * math.sqrt(self.d_model)

        # 2. Add positional encoding
        x = self.pos_encoding(x)
        x = self.dropout(x)

        # 3. Create causal mask
        causal_mask = torch.tril(torch.ones(seq_len, seq_len, device=input_ids.device))
        causal_mask = causal_mask.unsqueeze(0).unsqueeze(0)  # (1, 1, seq_len, seq_len)

        # 4. Pass through transformer blocks
        for block in self.blocks:
            x = block(x, causal_mask)

        # 5. Final layer norm
        x = self.ln_f(x)

        # 6. Language modeling head
        logits = self.lm_head(x)  # (batch, seq_len, vocab_size)

        return logits

    @torch.no_grad()
    def generate(self, input_ids, max_new_tokens, temperature=1.0, top_k=None):
        """
        Generate tokens autoregressively.

        Args:
            input_ids: (batch, seq_len) - Starting tokens
            max_new_tokens: Number of tokens to generate
            temperature: Sampling temperature (higher = more random)
            top_k: If set, only sample from top k tokens

        Returns:
            (batch, seq_len + max_new_tokens) - Generated sequence
        """
        for _ in range(max_new_tokens):
            # Get predictions for next token
            logits = self(input_ids)  # (batch, seq_len, vocab_size)
            logits = logits[:, -1, :] / temperature  # (batch, vocab_size) - last position

            # Apply top-k filtering if specified
            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float('-inf')

            # Sample from distribution
            probs = F.softmax(logits, dim=-1)
            next_token = torch.multinomial(probs, num_samples=1)  # (batch, 1)

            # Append to sequence
            input_ids = torch.cat([input_ids, next_token], dim=1)

        return input_ids


def demonstrate_mini_gpt():
    """
    Demonstrate the mini-GPT model.
    """
    print("=" * 80)
    print("MINI-GPT DEMONSTRATION")
    print("=" * 80)

    # Model configuration (similar to GPT-2 Small)
    vocab_size = 1000  # Small vocab for demo
    d_model = 128      # GPT-2 Small: 768
    num_heads = 8      # GPT-2 Small: 12
    num_layers = 4     # GPT-2 Small: 12
    d_ff = 512         # GPT-2 Small: 3072
    max_len = 256      # GPT-2: 1024

    print("\nModel Configuration:")
    print(f"  Vocabulary size: {vocab_size}")
    print(f"  d_model: {d_model}")
    print(f"  num_heads: {num_heads}")
    print(f"  num_layers: {num_layers}")
    print(f"  d_ff: {d_ff}")
    print(f"  max_len: {max_len}")

    # Create model
    model = MiniGPT(vocab_size, d_model, num_heads, num_layers, d_ff, max_len)

    # Count parameters
    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nTotal parameters: {total_params:,}")

    # Show parameter breakdown
    print("\nParameter breakdown:")
    for name, param in model.named_parameters():
        if param.requires_grad:
            print(f"  {name:40s}: {param.numel():>10,}")

    # Create dummy input
    batch_size = 2
    seq_len = 10
    input_ids = torch.randint(0, vocab_size, (batch_size, seq_len))

    print(f"\nInput shape: {input_ids.shape}")
    print(f"Input (token IDs): {input_ids[0].tolist()}")

    # Forward pass
    print("\nForward pass...")
    logits = model(input_ids)

    print(f"Output shape: {logits.shape}")
    print(f"  (batch={batch_size}, seq_len={seq_len}, vocab_size={vocab_size})")

    # Get predictions
    predicted_tokens = torch.argmax(logits, dim=-1)
    print(f"\nPredicted next tokens: {predicted_tokens[0].tolist()}")

    print("\n" + "-" * 80)
    print("Interpretation:")
    print(f"  For each position, we predict the NEXT token")
    print(f"  Position 0 input: {input_ids[0, 0].item()} → predicts: {predicted_tokens[0, 0].item()}")
    print(f"  Position 1 input: {input_ids[0, 1].item()} → predicts: {predicted_tokens[0, 1].item()}")
    print(f"  ...")


def demonstrate_generation():
    """
    Demonstrate text generation.
    """
    print("\n\n" + "=" * 80)
    print("TEXT GENERATION DEMONSTRATION")
    print("=" * 80)

    # Create small model
    vocab_size = 100
    model = MiniGPT(
        vocab_size=vocab_size,
        d_model=64,
        num_heads=4,
        num_layers=2,
        d_ff=256,
        max_len=128
    )

    model.eval()  # Set to evaluation mode

    # Start with a prompt (random tokens for demo)
    prompt = torch.tensor([[1, 2, 3]])  # Imagine: "Once upon a"

    print(f"\nPrompt (token IDs): {prompt[0].tolist()}")

    # Generate tokens
    print("\nGenerating 10 tokens...")
    print("  Using temperature=1.0, top_k=10")

    generated = model.generate(
        prompt,
        max_new_tokens=10,
        temperature=1.0,
        top_k=10
    )

    print(f"\nGenerated sequence: {generated[0].tolist()}")
    print(f"  First 3 tokens: prompt")
    print(f"  Next 10 tokens: generated")

    print("\n" + "-" * 80)
    print("Generation Process:")
    print("-" * 80)
    print("""
1. Start with prompt tokens
2. For each new token:
   a. Run forward pass on current sequence
   b. Get logits for next token (last position)
   c. Apply temperature scaling
   d. Apply top-k filtering (keep only top k tokens)
   e. Sample from probability distribution
   f. Append to sequence
3. Repeat until max_new_tokens reached or <END> token

This is AUTOREGRESSIVE generation - each token depends on all previous tokens!
""")


def compare_to_real_gpt():
    """
    Compare mini-GPT to real GPT models.
    """
    print("\n\n" + "=" * 80)
    print("COMPARISON: Mini-GPT vs Real GPT Models")
    print("=" * 80)

    models = {
        "Mini-GPT (our demo)": {
            "d_model": 128,
            "num_layers": 4,
            "num_heads": 8,
            "params": "~1M"
        },
        "GPT-2 Small": {
            "d_model": 768,
            "num_layers": 12,
            "num_heads": 12,
            "params": "117M"
        },
        "GPT-2 Medium": {
            "d_model": 1024,
            "num_layers": 24,
            "num_heads": 16,
            "params": "345M"
        },
        "GPT-2 Large": {
            "d_model": 1280,
            "num_layers": 36,
            "num_heads": 20,
            "params": "762M"
        },
        "GPT-2 XL": {
            "d_model": 1600,
            "num_layers": 48,
            "num_heads": 25,
            "params": "1.5B"
        },
        "GPT-3": {
            "d_model": 12288,
            "num_layers": 96,
            "num_heads": 96,
            "params": "175B"
        }
    }

    print()
    print(f"{'Model':<25} {'d_model':<10} {'Layers':<10} {'Heads':<10} {'Parameters':<15}")
    print("-" * 80)
    for name, config in models.items():
        print(f"{name:<25} {config['d_model']:<10} {config['num_layers']:<10} "
              f"{config['num_heads']:<10} {config['params']:<15}")

    print("\n" + "-" * 80)
    print("Key Insights:")
    print("-" * 80)
    print("""
1. Architecture is IDENTICAL - only scale differs!
2. Our mini-GPT uses the same components as GPT-3
3. More parameters = better performance (with enough data)
4. GPT-3 is 175,000× larger than our mini-GPT
5. But fundamentally, they work the same way!

The components we implemented:
  ✓ Token embeddings
  ✓ Positional encoding
  ✓ Multi-head attention
  ✓ Feed-forward networks
  ✓ Residual connections
  ✓ Layer normalization
  ✓ Language modeling head
  ✓ Autoregressive generation

You now understand how ChatGPT works!
""")


def main():
    """
    Run all demonstrations.
    """
    # Demonstrate model
    demonstrate_mini_gpt()

    # Demonstrate generation
    demonstrate_generation()

    # Compare to real GPT
    compare_to_real_gpt()

    print("\n\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. GPT = Token Embedding + Positional Encoding + Transformer Blocks + LM Head
2. Causal attention mask prevents looking at future tokens
3. Generation is autoregressive (one token at a time)
4. Temperature controls randomness, top-k controls diversity
5. Our mini-GPT uses the SAME architecture as GPT-3!

The magic of scaling:
  - Same architecture works from 1M to 175B parameters
  - More parameters → more knowledge, better reasoning
  - But training cost scales too: GPT-3 cost ~$5M to train!

Next: Day 7 - Train mini-GPT on real text and generate!
""")


if __name__ == "__main__":
    main()
