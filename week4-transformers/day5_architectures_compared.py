"""
Day 5: Comparing Transformer Architectures
===========================================
Understanding BERT, GPT, and T5 - when to use which?

Learning Goals:
--------------
1. Understand encoder-only (BERT), decoder-only (GPT), encoder-decoder (T5)
2. See the differences in attention masks
3. Understand pre-training objectives
4. Know which architecture to use for different tasks

Run: python day5_architectures_compared.py
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class BERTStyle(nn.Module):
    """
    Encoder-only architecture (BERT-style).
    - Bidirectional attention
    - Good for understanding tasks
    """
    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.encoder_layers = nn.ModuleList([
            nn.TransformerEncoderLayer(d_model, num_heads, d_ff, batch_first=True)
            for _ in range(num_layers)
        ])
        self.classifier = nn.Linear(d_model, 2)  # Binary classification example

    def forward(self, input_ids):
        """
        Args:
            input_ids: (batch, seq_len)

        Returns:
            logits: (batch, 2) - classification logits
        """
        # Embed
        x = self.embedding(input_ids)  # (batch, seq_len, d_model)

        # Pass through encoder layers (bidirectional attention)
        for layer in self.encoder_layers:
            x = layer(x)  # No mask = bidirectional

        # Use [CLS] token (first position) for classification
        cls_output = x[:, 0, :]  # (batch, d_model)

        # Classification head
        logits = self.classifier(cls_output)  # (batch, 2)

        return logits


class GPTStyle(nn.Module):
    """
    Decoder-only architecture (GPT-style).
    - Causal (autoregressive) attention
    - Good for generation tasks
    """
    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model)
        self.decoder_layers = nn.ModuleList([
            nn.TransformerDecoderLayer(d_model, num_heads, d_ff, batch_first=True)
            for _ in range(num_layers)
        ])
        self.lm_head = nn.Linear(d_model, vocab_size)  # Language modeling head

    def forward(self, input_ids):
        """
        Args:
            input_ids: (batch, seq_len)

        Returns:
            logits: (batch, seq_len, vocab_size) - next token predictions
        """
        seq_len = input_ids.size(1)

        # Create causal mask (prevent looking at future)
        causal_mask = nn.Transformer.generate_square_subsequent_mask(seq_len)

        # Embed
        x = self.embedding(input_ids)  # (batch, seq_len, d_model)

        # Pass through decoder layers (causal attention)
        # Note: In decoder-only, we use decoder layers with self-attention only
        for layer in self.decoder_layers:
            # For decoder-only, we pass x as both tgt and memory (self-attention)
            x = layer(x, x, tgt_mask=causal_mask)

        # Language modeling head
        logits = self.lm_head(x)  # (batch, seq_len, vocab_size)

        return logits


class T5Style(nn.Module):
    """
    Encoder-Decoder architecture (T5-style).
    - Encoder: Bidirectional attention on source
    - Decoder: Causal attention on target + cross-attention to source
    - Good for sequence-to-sequence tasks
    """
    def __init__(self, vocab_size, d_model, num_heads, num_layers, d_ff):
        super().__init__()
        self.src_embedding = nn.Embedding(vocab_size, d_model)
        self.tgt_embedding = nn.Embedding(vocab_size, d_model)

        self.transformer = nn.Transformer(
            d_model=d_model,
            nhead=num_heads,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers,
            dim_feedforward=d_ff,
            batch_first=True
        )

        self.lm_head = nn.Linear(d_model, vocab_size)

    def forward(self, src_ids, tgt_ids):
        """
        Args:
            src_ids: Source tokens (batch, src_len)
            tgt_ids: Target tokens (batch, tgt_len)

        Returns:
            logits: (batch, tgt_len, vocab_size)
        """
        tgt_len = tgt_ids.size(1)

        # Create causal mask for target
        tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt_len)

        # Embed
        src = self.src_embedding(src_ids)  # (batch, src_len, d_model)
        tgt = self.tgt_embedding(tgt_ids)  # (batch, tgt_len, d_model)

        # Pass through transformer
        output = self.transformer(src, tgt, tgt_mask=tgt_mask)

        # Language modeling head
        logits = self.lm_head(output)  # (batch, tgt_len, vocab_size)

        return logits


def compare_attention_patterns():
    """
    Compare attention patterns for BERT, GPT, and T5.
    """
    print("=" * 80)
    print("ATTENTION PATTERNS COMPARISON")
    print("=" * 80)

    seq_len = 5

    # BERT: Full attention (bidirectional)
    bert_mask = torch.ones(seq_len, seq_len)

    # GPT: Causal attention (autoregressive)
    gpt_mask = torch.tril(torch.ones(seq_len, seq_len))

    # T5 Encoder: Full attention (like BERT)
    t5_encoder_mask = torch.ones(seq_len, seq_len)

    # T5 Decoder: Causal attention (like GPT)
    t5_decoder_mask = torch.tril(torch.ones(seq_len, seq_len))

    print("\nBERT (Encoder-only) - Bidirectional Attention:")
    print("  Each token can see ALL other tokens (past and future)")
    print(bert_mask.int())

    print("\nGPT (Decoder-only) - Causal Attention:")
    print("  Each token can only see PREVIOUS tokens (no future)")
    print(gpt_mask.int())

    print("\nT5 (Encoder-Decoder):")
    print("  Encoder attention (on source):")
    print(t5_encoder_mask.int())
    print("\n  Decoder attention (on target):")
    print(t5_decoder_mask.int())
    print("  + Cross-attention: Decoder attends to encoder output")


def compare_use_cases():
    """
    Compare typical use cases for each architecture.
    """
    print("\n\n" + "=" * 80)
    print("USE CASES FOR EACH ARCHITECTURE")
    print("=" * 80)

    architectures = {
        "BERT (Encoder-only)": {
            "Attention": "Bidirectional (sees entire input)",
            "Pre-training": "Masked Language Model (MLM) + Next Sentence Prediction",
            "Best for": [
                "Text classification (sentiment, spam)",
                "Named Entity Recognition (NER)",
                "Question Answering (extractive)",
                "Sentence embeddings",
                "Token classification"
            ],
            "Examples": "BERT, RoBERTa, ALBERT, DistilBERT",
            "Limitation": "Cannot generate text autoregressively"
        },
        "GPT (Decoder-only)": {
            "Attention": "Causal (only sees previous tokens)",
            "Pre-training": "Next Token Prediction (language modeling)",
            "Best for": [
                "Text generation (stories, articles)",
                "Code generation (GitHub Copilot)",
                "Chatbots (ChatGPT, Claude)",
                "Text completion",
                "Few-shot learning"
            ],
            "Examples": "GPT-2, GPT-3, GPT-4, LLaMA, Mistral",
            "Limitation": "Unidirectional context (no future)"
        },
        "T5 (Encoder-Decoder)": {
            "Attention": "Bidirectional encoder + Causal decoder",
            "Pre-training": "Text-to-Text (all tasks as seq2seq)",
            "Best for": [
                "Machine Translation",
                "Text Summarization",
                "Question Answering (generative)",
                "Data-to-text generation",
                "Any input→output transformation"
            ],
            "Examples": "T5, BART, mBART, mT5",
            "Limitation": "More parameters than encoder/decoder-only"
        }
    }

    for arch_name, details in architectures.items():
        print("\n" + "-" * 80)
        print(f"{arch_name}")
        print("-" * 80)
        print(f"Attention:    {details['Attention']}")
        print(f"Pre-training: {details['Pre-training']}")
        print(f"\nBest for:")
        for use_case in details['Best for']:
            print(f"  • {use_case}")
        print(f"\nExamples: {details['Examples']}")
        print(f"⚠ Limitation: {details['Limitation']}")


def compare_pretraining_objectives():
    """
    Compare how each architecture is pre-trained.
    """
    print("\n\n" + "=" * 80)
    print("PRE-TRAINING OBJECTIVES")
    print("=" * 80)

    print("\n1. BERT: Masked Language Modeling (MLM)")
    print("-" * 80)
    print("Input:  'The [MASK] sat on the [MASK]'")
    print("Target: 'The cat sat on the mat'")
    print("\nProcess:")
    print("  1. Randomly mask 15% of tokens")
    print("  2. Predict masked tokens using bidirectional context")
    print("  3. Loss: Cross-entropy on masked positions only")
    print("\n✓ Learns bidirectional representations")
    print("✓ Good for understanding tasks")

    print("\n\n2. GPT: Next Token Prediction")
    print("-" * 80)
    print("Input:  'The cat sat'")
    print("Target: 'cat sat on'  (shifted by 1)")
    print("\nProcess:")
    print("  1. Predict next token given all previous tokens")
    print("  2. Use causal mask (can't see future)")
    print("  3. Loss: Cross-entropy on all positions")
    print("\n✓ Learns to generate coherent text")
    print("✓ Autoregressive by nature")

    print("\n\n3. T5: Text-to-Text")
    print("-" * 80)
    print("Task 1 - Translation:")
    print("  Input:  'translate English to French: Hello'")
    print("  Target: 'Bonjour'")
    print("\nTask 2 - Summarization:")
    print("  Input:  'summarize: [long article]'")
    print("  Target: '[summary]'")
    print("\nProcess:")
    print("  1. Frame ALL tasks as text-to-text")
    print("  2. Encoder processes input (bidirectional)")
    print("  3. Decoder generates output (causal)")
    print("  4. Loss: Cross-entropy on target tokens")
    print("\n✓ Unified framework for all NLP tasks")
    print("✓ Transfer learning across tasks")


def decision_tree():
    """
    Help user decide which architecture to use.
    """
    print("\n\n" + "=" * 80)
    print("DECISION TREE: Which Architecture Should I Use?")
    print("=" * 80)
    print("""
┌─────────────────────────────────────────────┐
│ What is your task?                          │
└─────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
  Understanding  Generation  Transformation
   (classify,    (write,     (translate,
    extract)     complete)   summarize)
        │           │           │
        │           │           │
        ▼           ▼           ▼
    ┌────────┐  ┌────────┐  ┌────────────┐
    │  BERT  │  │  GPT   │  │  T5/BART   │
    └────────┘  └────────┘  └────────────┘
    Encoder     Decoder      Encoder-
     only        only        Decoder

Examples by Category:
─────────────────────

UNDERSTANDING (Use BERT):
  • Is this review positive or negative?
  • Extract person names from this text
  • Find the answer to this question in the passage
  • Are these two sentences similar?

GENERATION (Use GPT):
  • Write a story about...
  • Complete this code function...
  • Continue this conversation...
  • Generate product descriptions...

TRANSFORMATION (Use T5):
  • Translate English to French
  • Summarize this article
  • Convert this question to SQL
  • Paraphrase this sentence
""")


def main():
    """
    Run all demonstrations.
    """
    # Compare attention patterns
    compare_attention_patterns()

    # Compare use cases
    compare_use_cases()

    # Compare pre-training objectives
    compare_pretraining_objectives()

    # Decision tree
    decision_tree()

    print("\n\n" + "=" * 80)
    print("KEY TAKEAWAYS")
    print("=" * 80)
    print("""
1. BERT (Encoder): Bidirectional → Understanding
   - Pre-training: Mask words, predict from context
   - Use: Classification, NER, Q&A

2. GPT (Decoder): Causal → Generation
   - Pre-training: Predict next word
   - Use: Text generation, completion, chatbots

3. T5 (Encoder-Decoder): Both → Transformation
   - Pre-training: Text-to-text for all tasks
   - Use: Translation, summarization, seq2seq

Modern Trend:
  • Decoder-only (GPT-style) is becoming dominant
  • GPT-3/4, LLaMA, Mistral, Claude - all decoder-only!
  • Can do BOTH understanding AND generation
  • Simpler architecture, easier to scale

Next: Day 6 - Build a mini-GPT from scratch
""")


if __name__ == "__main__":
    main()
