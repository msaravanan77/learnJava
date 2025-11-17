"""
Helper Utilities for Week 4: Transformers & Attention
======================================================
Common utility functions used across the week.
"""

import torch
import torch.nn as nn
import math


def create_causal_mask(seq_len, device='cpu'):
    """
    Create causal (lower triangular) mask for autoregressive attention.

    Args:
        seq_len: Sequence length
        device: Device to create mask on

    Returns:
        Causal mask of shape (seq_len, seq_len)
        1 where tokens can attend, 0 where they cannot
    """
    mask = torch.tril(torch.ones(seq_len, seq_len, device=device))
    return mask


def create_padding_mask(seq, pad_token=0):
    """
    Create padding mask from a sequence.

    Args:
        seq: Token sequence (batch, seq_len)
        pad_token: Padding token ID

    Returns:
        Padding mask (batch, seq_len) - 1 for real tokens, 0 for padding
    """
    return (seq != pad_token).long()


def count_parameters(model):
    """
    Count trainable parameters in a model.

    Args:
        model: PyTorch model

    Returns:
        Number of trainable parameters
    """
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


def get_parameter_breakdown(model):
    """
    Get detailed parameter breakdown for a model.

    Args:
        model: PyTorch model

    Returns:
        Dictionary mapping module names to parameter counts
    """
    breakdown = {}
    for name, param in model.named_parameters():
        if param.requires_grad:
            breakdown[name] = param.numel()
    return breakdown


def visualize_attention(attention_weights, tokens, head_idx=0):
    """
    Print attention weights in a readable format.

    Args:
        attention_weights: (batch, num_heads, seq_len, seq_len)
        tokens: List of token strings
        head_idx: Which attention head to visualize
    """
    attn = attention_weights[0, head_idx].detach()  # (seq_len, seq_len)

    print(f"\nAttention Head {head_idx}:")
    print(f"         {' '.join([f'{t:>7}' for t in tokens])}")

    for i, token in enumerate(tokens):
        row = attn[i]
        values = ' '.join([f'{v:7.3f}' for v in row])
        print(f"{token:>7}: {values}")


def scaled_dot_product_attention(Q, K, V, mask=None):
    """
    Compute scaled dot-product attention.

    Args:
        Q: Query (batch, ..., seq_len, d_k)
        K: Key (batch, ..., seq_len, d_k)
        V: Value (batch, ..., seq_len, d_v)
        mask: Optional mask (batch, ..., seq_len, seq_len)

    Returns:
        output: (batch, ..., seq_len, d_v)
        attention_weights: (batch, ..., seq_len, seq_len)
    """
    d_k = Q.size(-1)

    # Compute attention scores
    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(d_k)

    # Apply mask if provided
    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    # Softmax to get probabilities
    attention_weights = torch.softmax(scores, dim=-1)

    # Apply attention to values
    output = torch.matmul(attention_weights, V)

    return output, attention_weights


def positional_encoding(seq_len, d_model, device='cpu'):
    """
    Generate sinusoidal positional encoding.

    Args:
        seq_len: Sequence length
        d_model: Model dimension
        device: Device to create encoding on

    Returns:
        Positional encoding (seq_len, d_model)
    """
    pe = torch.zeros(seq_len, d_model, device=device)

    position = torch.arange(0, seq_len, dtype=torch.float, device=device).unsqueeze(1)
    div_term = torch.exp(
        torch.arange(0, d_model, 2, dtype=torch.float, device=device) *
        (-math.log(10000.0) / d_model)
    )

    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)

    return pe


def compute_perplexity(loss):
    """
    Compute perplexity from cross-entropy loss.

    Args:
        loss: Cross-entropy loss

    Returns:
        Perplexity score
    """
    return math.exp(loss)


def get_device():
    """
    Get the best available device (CUDA > MPS > CPU).

    Returns:
        torch.device
    """
    if torch.cuda.is_available():
        return torch.device('cuda')
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return torch.device('mps')
    else:
        return torch.device('cpu')


def set_seed(seed=42):
    """
    Set random seed for reproducibility.

    Args:
        seed: Random seed
    """
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)


def lr_schedule_warmup(step, d_model, warmup_steps=4000):
    """
    Learning rate schedule with warmup as in original Transformer paper.

    Args:
        step: Current training step
        d_model: Model dimension
        warmup_steps: Number of warmup steps

    Returns:
        Learning rate multiplier
    """
    step = max(step, 1)  # Avoid division by zero
    return d_model ** (-0.5) * min(step ** (-0.5), step * warmup_steps ** (-1.5))


def generate_text_greedy(model, prompt_tokens, max_new_tokens, vocab_size):
    """
    Generate text using greedy decoding.

    Args:
        model: Language model
        prompt_tokens: Starting tokens (1, seq_len)
        max_new_tokens: Number of tokens to generate
        vocab_size: Vocabulary size

    Returns:
        Generated tokens (1, seq_len + max_new_tokens)
    """
    model.eval()

    with torch.no_grad():
        for _ in range(max_new_tokens):
            # Get predictions
            logits = model(prompt_tokens)  # (1, seq_len, vocab_size)

            # Get next token (greedy)
            next_token = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)  # (1, 1)

            # Append to sequence
            prompt_tokens = torch.cat([prompt_tokens, next_token], dim=1)

    return prompt_tokens


def plot_attention_heatmap(attention_weights, tokens, head_idx=0):
    """
    Create a simple text-based heatmap of attention weights.

    Args:
        attention_weights: (batch, num_heads, seq_len, seq_len)
        tokens: List of token strings
        head_idx: Which head to visualize
    """
    attn = attention_weights[0, head_idx].detach()

    print(f"\nAttention Heatmap (Head {head_idx}):")
    print("Intensity: █ = high, ░ = low")
    print()

    # Column headers
    print("       " + "".join([f"{t:>8}" for t in tokens]))

    for i, token in enumerate(tokens):
        row_str = f"{token:>6} "
        for j in range(len(tokens)):
            val = attn[i, j].item()
            if val > 0.5:
                char = "█"
            elif val > 0.3:
                char = "▓"
            elif val > 0.1:
                char = "▒"
            else:
                char = "░"
            row_str += f"{char:>8}"
        print(row_str)


def demonstrate_helpers():
    """
    Demonstrate helper functions.
    """
    print("=" * 80)
    print("HELPER FUNCTIONS DEMONSTRATION")
    print("=" * 80)

    # Causal mask
    print("\n1. Causal Mask:")
    mask = create_causal_mask(5)
    print(mask)

    # Positional encoding
    print("\n2. Positional Encoding:")
    pe = positional_encoding(4, 8)
    print(f"Shape: {pe.shape}")
    print(pe)

    # Device detection
    print("\n3. Best Device:")
    device = get_device()
    print(f"Using device: {device}")

    # Perplexity
    print("\n4. Perplexity:")
    loss = 2.5
    perplexity = compute_perplexity(loss)
    print(f"Loss: {loss:.2f} → Perplexity: {perplexity:.2f}")

    print("\n✓ All helper functions ready to use!")


if __name__ == "__main__":
    demonstrate_helpers()
