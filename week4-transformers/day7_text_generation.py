"""
Day 7: Training Mini-GPT for Text Generation
=============================================
Train a mini-GPT model on real text and generate stories!

Learning Goals:
--------------
1. Prepare text data for language modeling
2. Train mini-GPT on character-level or word-level data
3. Generate coherent text
4. Understand training dynamics

Run: python day7_text_generation.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from day6_mini_gpt import MiniGPT
import math


class CharacterTokenizer:
    """
    Simple character-level tokenizer.
    """
    def __init__(self, text):
        """
        Args:
            text: Training text corpus
        """
        self.chars = sorted(list(set(text)))
        self.vocab_size = len(self.chars)
        self.char_to_idx = {ch: i for i, ch in enumerate(self.chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(self.chars)}

    def encode(self, text):
        """Convert text to token IDs."""
        return [self.char_to_idx[ch] for ch in text]

    def decode(self, tokens):
        """Convert token IDs to text."""
        return ''.join([self.idx_to_char[i] for i in tokens])


def create_training_data(text, block_size=128):
    """
    Create training examples for language modeling.

    Args:
        text: Input text
        block_size: Sequence length

    Returns:
        List of (input, target) pairs
    """
    data = []
    for i in range(0, len(text) - block_size):
        x = text[i:i + block_size]
        y = text[i + 1:i + block_size + 1]  # Shifted by 1
        data.append((x, y))
    return data


def train_mini_gpt():
    """
    Train a mini-GPT model on sample text.
    """
    print("=" * 80)
    print("TRAINING MINI-GPT ON TEXT")
    print("=" * 80)

    # Sample training text (Shakespeare-style for demonstration)
    # In practice, you'd load from sample_text.txt
    training_text = """
    To be, or not to be, that is the question:
    Whether 'tis nobler in the mind to suffer
    The slings and arrows of outrageous fortune,
    Or to take arms against a sea of troubles
    And by opposing end them. To die—to sleep,
    No more; and by a sleep to say we end
    The heart-ache and the thousand natural shocks
    That flesh is heir to: 'tis a consummation
    Devoutly to be wish'd. To die, to sleep;
    To sleep, perchance to dream—ay, there's the rub:
    For in that sleep of death what dreams may come,
    When we have shuffled off this mortal coil,
    Must give us pause—there's the respect
    That makes calamity of so long life.
    """ * 10  # Repeat to have more data

    print(f"\nTraining corpus length: {len(training_text)} characters")

    # Create tokenizer
    tokenizer = CharacterTokenizer(training_text)
    vocab_size = tokenizer.vocab_size

    print(f"Vocabulary size: {vocab_size} characters")
    print(f"Vocabulary: {''.join(tokenizer.chars)}")

    # Encode text
    encoded_text = tokenizer.encode(training_text)
    print(f"Encoded text length: {len(encoded_text)} tokens")

    # Create training data
    block_size = 64
    train_data = create_training_data(encoded_text, block_size)
    print(f"Number of training examples: {len(train_data)}")

    # Create model
    model = MiniGPT(
        vocab_size=vocab_size,
        d_model=128,
        num_heads=8,
        num_layers=4,
        d_ff=512,
        max_len=block_size,
        dropout=0.1
    )

    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nModel parameters: {total_params:,}")

    # Training setup
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)

    optimizer = torch.optim.AdamW(model.parameters(), lr=3e-4)
    criterion = nn.CrossEntropyLoss()

    # Training loop
    print("\n" + "-" * 80)
    print("TRAINING")
    print("-" * 80)

    num_epochs = 5
    batch_size = 32
    print_every = 50

    model.train()

    for epoch in range(num_epochs):
        total_loss = 0
        num_batches = 0

        # Simple batching (in practice, use DataLoader)
        for i in range(0, len(train_data) - batch_size, batch_size):
            batch = train_data[i:i + batch_size]

            # Prepare batch
            inputs = torch.tensor([x for x, y in batch], device=device)
            targets = torch.tensor([y for x, y in batch], device=device)

            # Forward pass
            logits = model(inputs)  # (batch, seq_len, vocab_size)

            # Reshape for loss computation
            logits = logits.view(-1, vocab_size)  # (batch * seq_len, vocab_size)
            targets = targets.view(-1)  # (batch * seq_len)

            # Compute loss
            loss = criterion(logits, targets)

            # Backward pass
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            num_batches += 1

            if num_batches % print_every == 0:
                avg_loss = total_loss / num_batches
                perplexity = math.exp(avg_loss)
                print(f"Epoch {epoch + 1}, Batch {num_batches}: Loss = {avg_loss:.4f}, Perplexity = {perplexity:.2f}")

        avg_loss = total_loss / num_batches
        perplexity = math.exp(avg_loss)
        print(f"\nEpoch {epoch + 1} complete: Avg Loss = {avg_loss:.4f}, Perplexity = {perplexity:.2f}")

    print("\nTraining complete!")

    # Generate text
    print("\n" + "-" * 80)
    print("TEXT GENERATION")
    print("-" * 80)

    model.eval()

    # Start with a prompt
    prompt = "To be, or not to be"
    print(f"\nPrompt: '{prompt}'")

    # Encode prompt
    prompt_tokens = tokenizer.encode(prompt)
    prompt_tensor = torch.tensor([prompt_tokens], device=device)

    # Generate
    with torch.no_grad():
        generated_tokens = model.generate(
            prompt_tensor,
            max_new_tokens=200,
            temperature=0.8,
            top_k=10
        )

    # Decode
    generated_text = tokenizer.decode(generated_tokens[0].tolist())

    print(f"\nGenerated text:\n")
    print(generated_text)

    print("\n" + "-" * 80)
    print("ANALYSIS")
    print("-" * 80)
    print("""
Observations:
  1. The model learned character patterns from the training text
  2. It captures some structure (words, spacing, punctuation)
  3. With more data and training, it would generate more coherent text
  4. This is exactly how ChatGPT works, just at massive scale!

Perplexity:
  - Measures how "surprised" the model is by the text
  - Lower perplexity = better predictions
  - exp(cross_entropy_loss)
  - Random guessing: perplexity = vocab_size
  - Perfect model: perplexity = 1

Temperature:
  - 0.0: Always pick most likely token (deterministic, boring)
  - 1.0: Sample according to model probabilities (balanced)
  - 2.0: More random, creative (but may be incoherent)
""")


def demonstrate_sampling_strategies():
    """
    Show different text generation strategies.
    """
    print("\n\n" + "=" * 80)
    print("SAMPLING STRATEGIES FOR TEXT GENERATION")
    print("=" * 80)

    # Create dummy logits for demonstration
    vocab_size = 10
    logits = torch.tensor([
        [2.0, 1.0, 0.5, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2, -0.5]
    ])  # (1, vocab_size)

    print("\nLogits (model outputs):")
    print(logits)

    # Convert to probabilities
    probs = F.softmax(logits, dim=-1)
    print("\nProbabilities (after softmax):")
    for i, p in enumerate(probs[0]):
        print(f"  Token {i}: {p:.4f} ({p * 100:.1f}%)")

    print("\n" + "-" * 80)
    print("1. GREEDY SAMPLING (temperature=0)")
    print("-" * 80)
    greedy_token = torch.argmax(probs, dim=-1)
    print(f"Selected token: {greedy_token.item()} (always picks highest probability)")
    print("Pros: Deterministic, coherent")
    print("Cons: Repetitive, boring")

    print("\n" + "-" * 80)
    print("2. TEMPERATURE SAMPLING")
    print("-" * 80)

    for temp in [0.5, 1.0, 2.0]:
        scaled_logits = logits / temp
        scaled_probs = F.softmax(scaled_logits, dim=-1)

        print(f"\nTemperature = {temp}:")
        print(f"  Top 3 probabilities: {scaled_probs[0][:3].tolist()}")

        if temp < 1.0:
            print(f"  → More peaked (favors high-probability tokens)")
        elif temp > 1.0:
            print(f"  → More uniform (more random)")

    print("\n" + "-" * 80)
    print("3. TOP-K SAMPLING (k=3)")
    print("-" * 80)
    k = 3
    top_k_probs, top_k_indices = torch.topk(probs, k)
    print(f"Top {k} tokens: {top_k_indices[0].tolist()}")
    print(f"Top {k} probabilities: {top_k_probs[0].tolist()}")
    print("Only sample from these top k tokens")
    print("Pros: Avoids very unlikely tokens, more diverse than greedy")

    print("\n" + "-" * 80)
    print("4. NUCLEUS (TOP-P) SAMPLING (p=0.9)")
    print("-" * 80)
    p = 0.9
    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
    cumsum = torch.cumsum(sorted_probs, dim=-1)

    # Find cutoff
    cutoff_idx = (cumsum <= p).sum().item()

    print(f"Nucleus probability: {p}")
    print(f"Number of tokens in nucleus: {cutoff_idx}")
    print(f"Selected tokens: {sorted_indices[0][:cutoff_idx].tolist()}")
    print("Pros: Adaptive (number of tokens varies), used by GPT-3")


def training_tips():
    """
    Provide practical training tips.
    """
    print("\n\n" + "=" * 80)
    print("PRACTICAL TRAINING TIPS")
    print("=" * 80)
    print("""
1. DATA PREPARATION
   ✓ Character-level: Small vocab (50-200), learns spelling
   ✓ Word-level: Medium vocab (10k-50k), more coherent
   ✓ BPE/WordPiece: Large vocab (32k-50k), balance both
   ✓ More data = better results (GPT-3: 300B tokens!)

2. MODEL SIZING
   ✓ Start small (d_model=128, 2-4 layers) for prototyping
   ✓ Scale up gradually based on dataset size
   ✓ Rule of thumb: 1M parameters per 1M tokens of data
   ✓ Watch for overfitting (train loss << val loss)

3. HYPERPARAMETERS
   ✓ Learning rate: 3e-4 to 1e-3 (with warmup)
   ✓ Batch size: As large as GPU memory allows
   ✓ Dropout: 0.1 for small models, 0.0 for large models
   ✓ Weight decay: 0.01 to 0.1

4. TRAINING DYNAMICS
   ✓ Loss should decrease smoothly
   ✓ Monitor perplexity (should decrease)
   ✓ Generate samples during training to check quality
   ✓ Use gradient clipping (max_norm=1.0)

5. GENERATION
   ✓ Temperature: 0.7-0.9 for most tasks
   ✓ Top-k: 40-50 for balanced diversity
   ✓ Top-p: 0.9-0.95 (nucleus sampling)
   ✓ Use repetition penalty if text repeats

6. DEBUGGING
   ✓ Overfit to single batch first (sanity check)
   ✓ Check attention patterns (should be meaningful)
   ✓ Verify positional encoding is added
   ✓ Ensure causal mask is correct (no future peeking!)

7. SCALING UP
   ✓ Use mixed precision training (torch.cuda.amp)
   ✓ Gradient accumulation for large batch sizes
   ✓ Multi-GPU with DistributedDataParallel
   ✓ Consider model parallelism for huge models
""")


def main():
    """
    Run all demonstrations.
    """
    # Train mini-GPT
    print("Starting training demonstration...")
    print("(This will take a few minutes)")
    train_mini_gpt()

    # Sampling strategies
    demonstrate_sampling_strategies()

    # Training tips
    training_tips()

    print("\n\n" + "=" * 80)
    print("CONGRATULATIONS!")
    print("=" * 80)
    print("""
You've completed the Transformers & Attention module!

What you've learned:
  ✓ Attention mechanism (Q, K, V)
  ✓ Self-attention and multi-head attention
  ✓ Transformer blocks (encoder and decoder)
  ✓ Positional encoding
  ✓ Different architectures (BERT, GPT, T5)
  ✓ Building mini-GPT from scratch
  ✓ Training and text generation

You now understand:
  • How ChatGPT generates text
  • How BERT understands language
  • How Google Translate works (encoder-decoder)
  • The fundamental architecture behind all modern AI

Next steps:
  1. Train on larger datasets (books, Wikipedia)
  2. Implement BPE tokenization
  3. Add beam search for better generation
  4. Fine-tune pre-trained models (Hugging Face)
  5. Explore advanced topics (LoRA, RLHF, RAG)

Resources:
  • Attention Is All You Need (original paper)
  • The Illustrated Transformer (Jay Alammar)
  • Hugging Face Transformers library
  • nanoGPT by Andrej Karpathy

Keep learning and building! 🚀
""")


if __name__ == "__main__":
    main()
