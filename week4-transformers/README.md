# Week 4: Transformers & Attention Mechanisms

> **Understanding Modern AI: How GPT, BERT, and Claude Actually Work**

## 🎯 Mission Statement

This week, you'll understand the **revolutionary architecture** that powers every modern AI system you use:
- ChatGPT, GPT-4, Claude → Transformer-based
- BERT, sentence embeddings → Transformer-based
- GitHub Copilot → Transformer-based
- DALL-E, Stable Diffusion → Transformer-based
- Translation systems → Transformer-based

**You won't just use these tools - you'll understand them deeply and build them from scratch.**

## 📚 Why Transformers Changed Everything

### Before Transformers (Pre-2017)
- **RNNs/LSTMs**: Processed text word-by-word sequentially
- **Problem**: Slow, couldn't parallelize, forgot long-range context
- **Example**: Understanding "The cat, which was sitting on the mat that was near the fireplace in the old house, was happy" - struggled with long dependencies

### After Transformers (2017+)
- **Attention Mechanism**: Look at ALL words simultaneously
- **Parallelization**: Process entire sequences at once (100x faster)
- **Long-range dependencies**: "Attention" to any word regardless of distance
- **Result**: ChatGPT can write essays, code, have conversations

**The "Attention Is All You Need" paper (2017) changed AI forever.**

## 🗺️ Week 4 Roadmap

### Day 1-2: Attention Fundamentals
**Files**: `day1_attention_basics.py`, `day2_self_attention.py`

**What You'll Learn**:
- The Query, Key, Value (Q, K, V) mechanism
- Scaled dot-product attention
- Why attention works mathematically
- Build attention from scratch in NumPy/PyTorch

**Visual Aids**:
- `SVG1-Attention-Fundamentals.svg` - Q, K, V explanation
- `SVG2-Attention-Mechanism-Step-by-Step.svg` - Complete calculation walkthrough
- `SVG3-Attention-Example-Sentence.svg` - Real example with actual numbers

### Day 3: Multi-Head Attention & Transformer Block
**Files**: `day3_multi_head_attention.py`, `day4_transformer_block.py`

**What You'll Learn**:
- Why multiple attention heads
- Parallel attention mechanisms
- Feed-forward networks
- Layer normalization & residual connections
- Positional encoding (how transformers understand word order)

**Visual Aids**:
- `SVG4-Multi-Head-Attention.svg` - Parallel attention heads
- `SVG5-Transformer-Block-Complete.svg` - Full transformer block architecture
- `SVG6-Positional-Encoding.svg` - Position representation

### Day 4: Encoder vs Decoder vs Encoder-Decoder
**Files**: `day5_architectures_compared.py`

**What You'll Learn**:
- **Encoder-only (BERT)**: Bidirectional, understands context
- **Decoder-only (GPT)**: Autoregressive, generates text
- **Encoder-Decoder (T5, Translation)**: Both together
- Masked vs Causal attention
- When to use which architecture

**Visual Aids**:
- `SVG7-Encoder-Architecture-BERT.svg` - BERT-style encoder
- `SVG8-Decoder-Architecture-GPT.svg` - GPT-style decoder
- `SVG9-Encoder-Decoder-Translation.svg` - Full translation model
- `SVG10-Masked-vs-Causal-Attention.svg` - Attention masking comparison

### Day 5: Build Mini-GPT from Scratch
**Files**: `day6_mini_gpt.py`, `day7_text_generation.py`

**What You'll Learn**:
- Build a working GPT-style model
- Train on real text data
- Generate text character-by-character or word-by-word
- Understand how ChatGPT generates responses

**Visual Aids**:
- `SVG11-GPT-Generation-Process.svg` - How GPT generates text step-by-step

## 📊 Visual Learning Materials

### Complete SVG Diagram Collection

1. **SVG1-Attention-Fundamentals.svg**
   - What are Query, Key, Value vectors?
   - The attention formula explained visually
   - Why "attention" is the right name

2. **SVG2-Attention-Mechanism-Step-by-Step.svg**
   - Complete attention calculation walkthrough
   - Matrix operations visualized
   - Softmax and weighted sum

3. **SVG3-Attention-Example-Sentence.svg**
   - Real example: "The cat sat on the mat"
   - Actual attention scores between words
   - How context is captured

4. **SVG4-Multi-Head-Attention.svg**
   - Why 8-12 parallel attention heads
   - Each head learns different patterns
   - Concatenation and projection

5. **SVG5-Transformer-Block-Complete.svg**
   - Complete transformer encoder/decoder block
   - Multi-head attention
   - Feed-forward network
   - Layer norm & residuals
   - All connections labeled

6. **SVG6-Positional-Encoding.svg**
   - Sine/cosine positional encodings
   - Why transformers need position information
   - How position is added to embeddings

7. **SVG7-Encoder-Architecture-BERT.svg**
   - Full BERT-style encoder stack
   - Bidirectional attention
   - Use cases: classification, embeddings

8. **SVG8-Decoder-Architecture-GPT.svg**
   - Full GPT-style decoder stack
   - Causal (masked) attention
   - Autoregressive generation
   - How ChatGPT works

9. **SVG9-Encoder-Decoder-Translation.svg**
   - Complete translation model
   - Encoder processes source language
   - Decoder generates target language
   - Cross-attention between encoder and decoder

10. **SVG10-Masked-vs-Causal-Attention.svg**
    - Bidirectional (BERT): See all words
    - Causal (GPT): Only see previous words
    - Visual attention matrix comparison

11. **SVG11-GPT-Generation-Process.svg**
    - Step-by-step text generation
    - Sampling strategies (greedy, top-k, nucleus)
    - How ChatGPT continues conversations

## 🔬 Hands-On Implementation

### Day 1-2: Attention from Scratch

```python
# You'll implement this yourself!
def attention(query, key, value):
    """
    Scaled Dot-Product Attention

    Args:
        query: (batch, seq_len, d_k)
        key: (batch, seq_len, d_k)
        value: (batch, seq_len, d_v)

    Returns:
        output: (batch, seq_len, d_v)
        attention_weights: (batch, seq_len, seq_len)
    """
    d_k = query.size(-1)

    # 1. Compute attention scores: Q @ K^T
    scores = torch.matmul(query, key.transpose(-2, -1))

    # 2. Scale by sqrt(d_k)
    scores = scores / math.sqrt(d_k)

    # 3. Apply softmax
    attention_weights = F.softmax(scores, dim=-1)

    # 4. Weighted sum of values
    output = torch.matmul(attention_weights, value)

    return output, attention_weights
```

### Day 3: Multi-Head Attention

```python
class MultiHeadAttention(nn.Module):
    def __init__(self, d_model, num_heads):
        super().__init__()
        self.num_heads = num_heads
        self.d_model = d_model
        self.d_k = d_model // num_heads

        # Linear projections for Q, K, V
        self.W_q = nn.Linear(d_model, d_model)
        self.W_k = nn.Linear(d_model, d_model)
        self.W_v = nn.Linear(d_model, d_model)
        self.W_o = nn.Linear(d_model, d_model)

    def forward(self, query, key, value, mask=None):
        # Project and split into multiple heads
        # Apply attention
        # Concatenate heads
        # Final projection
        pass  # You'll implement this!
```

### Day 4: Complete Transformer Block

```python
class TransformerBlock(nn.Module):
    def __init__(self, d_model, num_heads, d_ff, dropout=0.1):
        super().__init__()

        # Multi-head attention
        self.attention = MultiHeadAttention(d_model, num_heads)

        # Feed-forward network
        self.ff = nn.Sequential(
            nn.Linear(d_model, d_ff),
            nn.ReLU(),
            nn.Linear(d_ff, d_model)
        )

        # Layer normalization
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)

        # Dropout
        self.dropout = nn.Dropout(dropout)

    def forward(self, x, mask=None):
        # Attention with residual connection
        attn_output = self.attention(x, x, x, mask)
        x = self.norm1(x + self.dropout(attn_output))

        # Feed-forward with residual connection
        ff_output = self.ff(x)
        x = self.norm2(x + self.dropout(ff_output))

        return x
```

### Day 5: Mini-GPT

```python
class MiniGPT(nn.Module):
    """
    A simplified GPT model for text generation
    Similar to how ChatGPT works (but much smaller)
    """
    def __init__(self, vocab_size, d_model=256, num_heads=8,
                 num_layers=6, max_seq_len=512):
        super().__init__()

        # Token embeddings
        self.token_embedding = nn.Embedding(vocab_size, d_model)

        # Positional embeddings
        self.position_embedding = nn.Embedding(max_seq_len, d_model)

        # Transformer decoder blocks
        self.blocks = nn.ModuleList([
            TransformerBlock(d_model, num_heads, d_model * 4)
            for _ in range(num_layers)
        ])

        # Output projection
        self.ln_f = nn.LayerNorm(d_model)
        self.head = nn.Linear(d_model, vocab_size)

    def forward(self, x):
        # Generate text token by token
        # This is how ChatGPT generates responses!
        pass
```

## 📖 Core Concepts Deep Dive

### 1. Attention Mechanism: The Core Idea

**Question**: How does a model understand "The animal didn't cross the street because **it** was too tired"?

**Answer**: Attention! The model learns that "it" refers to "animal", not "street".

**How**:
- **Query**: "What is 'it'?" (the word we're trying to understand)
- **Key**: Features of all words ("animal", "street", etc.)
- **Value**: Information content of each word
- **Attention Score**: How relevant each word is to "it"
- **Result**: Weighted combination focusing on "animal"

### 2. Self-Attention: Every Word Attends to Every Word

In "The cat sat on the mat":
- "cat" attends to: "The" (a bit), "sat" (strong), "on" (weak), "mat" (medium)
- "sat" attends to: "cat" (strong), "on" (strong), "mat" (medium)
- Each word builds understanding from ALL other words

**This is bidirectional in BERT, unidirectional in GPT.**

### 3. Multi-Head Attention: Multiple Perspectives

Why 8-12 heads?
- **Head 1**: Might focus on syntax (subject-verb agreement)
- **Head 2**: Might focus on semantic meaning
- **Head 3**: Might focus on position/distance
- **Head 4-8**: Learn other useful patterns

**Parallel attention = richer understanding**

### 4. Positional Encoding: Understanding Word Order

"Dog bites man" ≠ "Man bites dog"

Transformers process all words simultaneously, so they need to know position:
- Position 0: Dog
- Position 1: bites
- Position 2: man

**Solution**: Add sine/cosine positional encodings to embeddings

### 5. Encoder vs Decoder

**Encoder (BERT)**:
- Bidirectional: sees entire sentence
- Tasks: classification, embeddings, understanding
- Example: "Is this email spam?"

**Decoder (GPT)**:
- Unidirectional: only sees previous words
- Tasks: text generation, completion
- Example: "Complete this sentence: The weather today is..."

**Encoder-Decoder (T5, Translation)**:
- Encoder: understand source language
- Decoder: generate target language
- Cross-attention: decoder attends to encoder output

### 6. Masked Attention (BERT) vs Causal Attention (GPT)

**Masked Attention (BERT)**:
```
Sentence: "The [MASK] sat on the mat"
Can see: ALL words (bidirectional)
Task: Predict [MASK] = "cat"
```

**Causal Attention (GPT)**:
```
Input: "The cat sat"
Can see: Only "The cat sat" (not future words)
Predict: Next word = "on"
```

**GPT can't "cheat" by looking ahead - that's why it's autoregressive**

## 🎯 Learning Objectives

By end of Week 4, you will:

### Conceptual Understanding
- ✅ Explain attention mechanism to anyone
- ✅ Understand Q, K, V intuitively and mathematically
- ✅ Know why transformers replaced RNNs/LSTMs
- ✅ Explain how ChatGPT generates text
- ✅ Understand BERT vs GPT architectures
- ✅ Know when to use encoder vs decoder

### Technical Skills
- ✅ Implement attention from scratch (NumPy)
- ✅ Build multi-head attention (PyTorch)
- ✅ Create complete transformer block
- ✅ Build mini-GPT for text generation
- ✅ Train transformer on real text
- ✅ Generate coherent text

### Practical Knowledge
- ✅ Understand modern AI architectures
- ✅ Know how to fine-tune transformers
- ✅ Recognize different attention patterns
- ✅ Debug transformer training issues
- ✅ Choose right architecture for task

## 📁 Week 4 Structure

```
week4-transformers/
├── README.md (this file)
│
├── Visual Diagrams (11 SVGs)
│   ├── SVG1-Attention-Fundamentals.svg
│   ├── SVG2-Attention-Mechanism-Step-by-Step.svg
│   ├── SVG3-Attention-Example-Sentence.svg
│   ├── SVG4-Multi-Head-Attention.svg
│   ├── SVG5-Transformer-Block-Complete.svg
│   ├── SVG6-Positional-Encoding.svg
│   ├── SVG7-Encoder-Architecture-BERT.svg
│   ├── SVG8-Decoder-Architecture-GPT.svg
│   ├── SVG9-Encoder-Decoder-Translation.svg
│   ├── SVG10-Masked-vs-Causal-Attention.svg
│   └── SVG11-GPT-Generation-Process.svg
│
├── Implementation Files
│   ├── day1_attention_basics.py           # Attention from scratch
│   ├── day2_self_attention.py             # Self-attention implementation
│   ├── day3_multi_head_attention.py       # Multi-head attention
│   ├── day4_transformer_block.py          # Complete transformer block
│   ├── day5_architectures_compared.py     # BERT vs GPT vs T5
│   ├── day6_mini_gpt.py                   # Build GPT from scratch
│   ├── day7_text_generation.py            # Train and generate text
│   └── helpers.py                         # Utility functions
│
├── Sample Data
│   ├── sample_text.txt                    # Training text corpus
│   ├── tokenizer.py                       # Simple tokenizer
│   └── vocab.json                         # Vocabulary
│
├── Models (saved checkpoints)
│   └── mini_gpt.pth
│
└── requirements.txt
```

## 🚀 Getting Started

### Setup (5 minutes)
```bash
cd week4-transformers

# Install dependencies
pip install -r requirements.txt

# Verify setup
python day1_attention_basics.py
```

### Learning Path

**Day 1**: Attention Fundamentals
```bash
python day1_attention_basics.py
# Study: SVG1, SVG2, SVG3
# Understand: Q, K, V and attention formula
```

**Day 2**: Self-Attention
```bash
python day2_self_attention.py
# Build self-attention from scratch
# Visualize attention weights
```

**Day 3**: Multi-Head Attention
```bash
python day3_multi_head_attention.py
# Implement parallel attention heads
# Study: SVG4, SVG5, SVG6
```

**Day 4**: Transformer Architectures
```bash
python day5_architectures_compared.py
# Study: SVG7, SVG8, SVG9, SVG10
# Compare BERT, GPT, T5
```

**Day 5**: Build & Train Mini-GPT
```bash
python day6_mini_gpt.py
python day7_text_generation.py
# Study: SVG11
# Generate your own text!
```

## 💡 Key Insights

### Why Attention Works
**Traditional approach**: Process word by word sequentially
**Attention approach**: Look at entire sentence simultaneously

**Benefit**:
- Parallelization (100x faster)
- Long-range dependencies (remember context)
- Better understanding (see all relationships)

### The Transformer Revolution
```
2017: "Attention Is All You Need" paper
2018: BERT revolutionizes NLP
2020: GPT-3 shows emergence
2022: ChatGPT changes everything
2023: GPT-4, Claude - transformers everywhere
```

**All built on the same foundation you're learning this week!**

### What Makes ChatGPT "Smart"?
1. **Transformer architecture**: Attention to understand context
2. **Massive scale**: 175B parameters (GPT-3)
3. **Training data**: Huge text corpus
4. **Fine-tuning**: RLHF (Reinforcement Learning from Human Feedback)

**The architecture? It's what you're building this week!**

## 🎓 Advanced Topics (Optional)

After Week 4, you can explore:
- **Flash Attention**: Optimized attention for efficiency
- **Sparse Attention**: Reduce computation for long sequences
- **Vision Transformers**: Apply transformers to images
- **Fine-tuning**: Adapt pre-trained models to your task
- **Quantization**: Run large models efficiently

## 📚 Sample Projects

After Week 4, you can build:
1. **Sentiment Analyzer**: BERT-based sentiment classification
2. **Text Generator**: GPT-style creative writing
3. **Translation System**: Encoder-decoder for languages
4. **Code Completion**: Like GitHub Copilot (simplified)
5. **Chatbot**: Question-answering system

## 🔥 Real-World Applications

**What you can do with transformers:**

**Text**:
- Translation (Google Translate)
- Summarization (news summaries)
- Question answering (chatbots)
- Code generation (Copilot)
- Text completion (Gmail Smart Compose)

**Beyond Text**:
- Image generation (DALL-E, Stable Diffusion)
- Protein folding (AlphaFold)
- Music generation
- Video understanding

**All use transformer architecture!**

## ✅ Success Criteria

You've mastered Week 4 when you can:

1. **Explain** how attention works to a friend
2. **Draw** the attention mechanism on paper
3. **Implement** self-attention in PyTorch from memory
4. **Differentiate** between BERT and GPT architectures
5. **Build** a working text generator
6. **Understand** how ChatGPT generates responses
7. **Debug** transformer training issues
8. **Choose** right architecture for different tasks

## 🌟 Why This Week Matters Most

**Week 1**: Tensors - learned the basics
**Week 2**: Neural networks - understood training
**Week 3**: Production systems - built real applications
**Week 4**: **Transformers - understand modern AI**

**This is the architecture behind:**
- Every AI tool you use
- The future of AI development
- What companies are hiring for
- Research breakthroughs

**Master this, and you understand the foundation of modern AI.**

---

**Ready to understand how ChatGPT really works?**

**Start with:** `python day1_attention_basics.py`

Then study `SVG1-Attention-Fundamentals.svg`

Let's decode the magic of transformers! 🚀
