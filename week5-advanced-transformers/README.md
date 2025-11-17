# Week 5: Advanced Transformers & Modern AI Applications

## 🎯 Overview

Build on Week 4 fundamentals to master **production-ready** modern AI applications.

This week covers what AI companies actually use in production:
- ✅ Fine-tuning pre-trained models (Hugging Face)
- ✅ Prompt engineering & in-context learning
- ✅ RAG (Retrieval Augmented Generation)
- ✅ Efficient fine-tuning (LoRA/QLoRA)
- ✅ AI agents with tools and memory

## 📅 5-Day Roadmap

### Day 1: Fine-Tuning Pre-trained Models
**Learn:** Use Hugging Face Transformers, fine-tune BERT for classification

**Files:**
- `day1_huggingface_intro.py` - Load and use pre-trained models
- `day1_fine_tuning.py` - Fine-tune BERT for sentiment analysis
- `day1_comparison.py` - Scratch vs pre-trained comparison
- `sample_movie_reviews.csv` - Training data

**SVG:** `SVG1-Transfer-Learning-Pipeline.svg`

**Key Concepts:**
- Transfer learning: Pre-training → Fine-tuning
- Hugging Face model hub
- Trainer API for easy training
- Evaluation metrics (accuracy, F1)

---

### Day 2: Prompt Engineering & In-Context Learning
**Learn:** Craft effective prompts, few-shot learning, chain-of-thought

**Files:**
- `day2_prompt_basics.py` - Prompt templates and examples
- `day2_few_shot_learning.py` - In-context learning demonstrations
- `day2_chain_of_thought.py` - CoT reasoning
- `day2_prompt_optimization.py` - A/B testing prompts

**SVGs:**
- `SVG2-Prompt-Engineering-Strategies.svg`
- `SVG3-In-Context-Learning.svg`

**Key Concepts:**
- Zero-shot, one-shot, few-shot learning
- Chain-of-thought prompting
- Prompt templates and best practices
- How ChatGPT/Claude use prompts

---

### Day 3: RAG (Retrieval Augmented Generation)
**Learn:** Build RAG system, vector databases, semantic search

**Files:**
- `day3_embeddings.py` - Create and search embeddings
- `day3_vector_db.py` - Build vector database with FAISS
- `day3_retrieval.py` - Semantic search implementation
- `day3_rag_system.py` - Complete RAG pipeline
- `knowledge_base/` - Sample documents

**SVGs:**
- `SVG4-RAG-Architecture.svg`
- `SVG5-Vector-Search-Process.svg`

**Key Concepts:**
- Dense embeddings vs keyword search
- Vector databases (FAISS, ChromaDB)
- Semantic similarity search
- RAG: Retrieve → Augment → Generate

---

### Day 4: Efficient Fine-Tuning (LoRA/QLoRA)
**Learn:** Parameter-efficient fine-tuning, quantization

**Files:**
- `day4_lora_explained.py` - LoRA theory and implementation
- `day4_quantization.py` - Model quantization (4-bit, 8-bit)
- `day4_fine_tune_7b.py` - Fine-tune 7B model on consumer GPU
- `day4_comparison.py` - Full vs LoRA fine-tuning

**SVGs:**
- `SVG6-LoRA-Architecture.svg`
- `SVG7-Full-vs-LoRA-Comparison.svg`

**Key Concepts:**
- LoRA: Low-Rank Adaptation
- Quantization (QLoRA, 4-bit, 8-bit)
- PEFT (Parameter-Efficient Fine-Tuning)
- Fine-tune 7B-70B models on single GPU

---

### Day 5: Building an AI Agent/Chatbot
**Learn:** Conversational AI, memory, tool use

**Files:**
- `day5_conversation_manager.py` - Handle chat history
- `day5_tool_calling.py` - Function calling
- `day5_agent.py` - Complete AI agent
- `day5_api_server.py` - FastAPI deployment
- `day5_web_ui.py` - Chat interface

**SVGs:**
- `SVG8-Agent-Architecture.svg`
- `SVG9-Conversation-Flow.svg`

**Key Concepts:**
- Conversation memory and context
- Tool use and function calling
- Multi-turn dialogue management
- Production deployment

---

## 🏗️ Project Structure

```
week5-advanced-transformers/
├── README.md
│
├── SVG1-Transfer-Learning-Pipeline.svg
├── SVG2-Prompt-Engineering-Strategies.svg
├── SVG3-In-Context-Learning.svg
├── SVG4-RAG-Architecture.svg
├── SVG5-Vector-Search-Process.svg
├── SVG6-LoRA-Architecture.svg
├── SVG7-Full-vs-LoRA-Comparison.svg
├── SVG8-Agent-Architecture.svg
├── SVG9-Conversation-Flow.svg
│
├── day1_huggingface_intro.py
├── day1_fine_tuning.py
├── day1_comparison.py
├── sample_movie_reviews.csv
│
├── day2_prompt_basics.py
├── day2_few_shot_learning.py
├── day2_chain_of_thought.py
├── day2_prompt_optimization.py
│
├── day3_embeddings.py
├── day3_vector_db.py
├── day3_retrieval.py
├── day3_rag_system.py
├── knowledge_base/
│
├── day4_lora_explained.py
├── day4_quantization.py
├── day4_fine_tune_7b.py
├── day4_comparison.py
│
├── day5_conversation_manager.py
├── day5_tool_calling.py
├── day5_agent.py
├── day5_api_server.py
├── day5_web_ui.py
│
├── helpers.py
├── requirements.txt
└── deployment_guide.md
```

## 🚀 Getting Started

### Installation

```bash
cd week5-advanced-transformers
pip install -r requirements.txt
```

### Quick Start

Each day is self-contained:

```bash
# Day 1: Fine-tuning
python day1_huggingface_intro.py
python day1_fine_tuning.py

# Day 2: Prompt engineering
python day2_prompt_basics.py
python day2_few_shot_learning.py

# Day 3: RAG
python day3_rag_system.py

# Day 4: LoRA
python day4_lora_explained.py

# Day 5: AI Agent
python day5_agent.py
python day5_api_server.py  # Web server
```

## 🎓 Prerequisites

Before starting Week 5, you should have completed:
- ✅ Week 4: Transformers & Attention
- ✅ Week 4a: Mini Project (QA System)

You should understand:
- Transformer architecture
- Attention mechanisms
- BERT and GPT models
- Basic PyTorch

## 💡 Key Takeaways

### What You'll Learn

1. **Production ML Skills**
   - Use industry-standard tools (Hugging Face)
   - Fine-tune instead of training from scratch
   - Deploy models efficiently

2. **Modern AI Techniques**
   - Prompt engineering (used by ChatGPT)
   - RAG (used by most AI chatbots)
   - LoRA (fine-tune huge models cheaply)

3. **Real-World Applications**
   - Build chatbots with memory
   - Create document Q&A systems
   - Deploy AI agents with tools

### Why This Matters

- **Transfer Learning**: 100x faster than training from scratch
- **RAG**: Enables AI with up-to-date knowledge
- **LoRA**: Fine-tune 70B models on consumer GPUs
- **Agents**: Power modern AI assistants (ChatGPT plugins, Claude tools)

## 🔧 Technical Requirements

**Minimum:**
- Python 3.8+
- 8GB RAM
- CPU (GPU optional for Day 1-3)

**Recommended:**
- 16GB RAM
- NVIDIA GPU with 8GB VRAM (for Day 4-5)
- CUDA 11.8+

**For 7B Model Fine-tuning (Day 4):**
- 16GB+ VRAM (or use QLoRA with 8GB)
- Or use Google Colab free tier

## 📊 Performance Expectations

| Task | Training Time | Inference Time | Accuracy |
|------|---------------|----------------|----------|
| BERT Fine-tuning | 10-20 min | 10ms | 90%+ |
| RAG System | N/A (no training) | 100-200ms | High quality |
| LoRA 7B | 1-3 hours | 50-100ms | 85%+ |
| AI Agent | N/A | 200-500ms | Task-dependent |

## 🎯 Learning Path

```
Week 4: Fundamentals
  └─→ Transformers, Attention, BERT, GPT

Week 4a: Mini Project
  └─→ Build QA System from scratch

Week 5: Advanced (YOU ARE HERE)
  ├─→ Day 1: Fine-tuning (practical transfer learning)
  ├─→ Day 2: Prompting (how to use LLMs effectively)
  ├─→ Day 3: RAG (knowledge augmentation)
  ├─→ Day 4: LoRA (efficient fine-tuning)
  └─→ Day 5: Agents (put it all together)

Week 6+: Specialized Topics
  └─→ Multi-modal, RL, Production ML
```

## 📚 Resources

### Official Documentation
- [Hugging Face Transformers](https://huggingface.co/docs/transformers)
- [PEFT Library](https://huggingface.co/docs/peft)
- [LangChain](https://python.langchain.com/)
- [FastAPI](https://fastapi.tiangolo.com/)

### Papers
- [LoRA: Low-Rank Adaptation](https://arxiv.org/abs/2106.09685)
- [RAG: Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [Chain-of-Thought Prompting](https://arxiv.org/abs/2201.11903)

### Datasets
- [IMDb Reviews](https://ai.stanford.edu/~amaas/data/sentiment/) - Sentiment analysis
- [SQuAD](https://rajpurkar.github.io/SQuAD-explorer/) - Question answering
- [Alpaca](https://github.com/tatsu-lab/stanford_alpaca) - Instruction following

## 🤝 Tips for Success

1. **Run code progressively**: Don't skip days
2. **Experiment**: Change hyperparameters and observe
3. **Read the SVGs**: They explain the concepts visually
4. **Use checkpoints**: Save models after training
5. **Monitor resources**: Check GPU/RAM usage

## 🐛 Troubleshooting

### Out of Memory
```python
# Reduce batch size
batch_size = 4  # Instead of 16

# Use gradient accumulation
accumulation_steps = 4

# Enable gradient checkpointing
model.gradient_checkpointing_enable()
```

### Slow Training
```python
# Use mixed precision
from torch.cuda.amp import autocast, GradScaler

# Use DataLoader with multiple workers
DataLoader(dataset, num_workers=4)
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

## 🎁 Bonus Content

### Optional Extensions
- Deploy to Hugging Face Spaces
- Add speech input/output
- Multi-language support
- Real-time streaming responses
- Integration with external APIs

## 📝 Exercises

Each day includes:
- ✅ Hands-on coding exercises
- ✅ Concept explanation
- ✅ Working examples
- ✅ Best practices

## 🏆 Week 5 Goals

By the end of this week, you will:

✅ Fine-tune BERT for 90%+ accuracy
✅ Build a RAG system with your documents
✅ Fine-tune a 7B model with LoRA
✅ Deploy an AI agent with tools
✅ Understand production ML workflows

---

## 🚀 Let's Get Started!

Begin with Day 1:
```bash
python day1_huggingface_intro.py
```

**Next:** See individual day files for detailed implementations.

---

*This week bridges the gap between understanding transformers and using them in production!*
