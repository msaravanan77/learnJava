# Week 4a: Mini Project - Question Answering System

## 🎯 Project Overview

Build a complete end-to-end **Question Answering (QA) system** that reads documents and answers questions using transformer-based encoders.

This project consolidates everything you learned in Week 4:
- ✅ BERT-style transformer encoder
- ✅ Attention mechanisms for understanding
- ✅ Token, position, and segment embeddings
- ✅ Real-world application with measurable results

## 🏗️ Architecture

The system consists of 5 main components:

```
1. INPUT LAYER
   ├── Documents (Knowledge Base)
   └── User Question

2. PROCESSING LAYER
   ├── Document Processor (chunking, tokenization)
   ├── Question Processor (normalization)
   ├── Context Matcher (relevance scoring)
   └── Pair Formation ([CLS] Q [SEP] Doc [SEP])

3. TRANSFORMER ENCODER (BERT-style)
   ├── Embedding Layer (Token + Position + Segment)
   └── 12 Encoder Blocks (Multi-head Attention + Feed-Forward)

4. ANSWER EXTRACTION
   ├── Start Position Classifier
   ├── End Position Classifier
   └── Span Extractor

5. OUTPUT
   └── Answer with confidence score
```

See `Project-Architecture-Overview.svg` for detailed architecture diagram.

## 📁 Project Structure

```
week4a-mini-project/
├── Project-Architecture-Overview.svg    # System architecture
├── QA-Pipeline-Flow.svg                 # Data flow diagram
├── Model-Architecture-Detail.svg        # Neural network detail
│
├── step1_document_processor.py          # Load and chunk documents
├── step2_build_encoder.py               # Build BERT encoder
├── step3_answer_extractor.py            # Extract answer spans
├── step4_qa_engine.py                   # Complete QA engine
├── step5_evaluation.py                  # Evaluate performance
├── step6_web_interface.py               # Web UI (FastAPI)
│
├── sample_documents/                    # Knowledge base
│   ├── transformers.txt
│   ├── attention.txt
│   └── bert.txt
│
├── test_questions.json                  # Test Q&A pairs
├── requirements.txt                     # Dependencies
├── REVIEW_CHECKLIST.md                  # Self-review checklist
└── README.md                            # This file
```

## 🚀 Getting Started

### Step 1: Install Dependencies

```bash
cd week4a-mini-project
pip install -r requirements.txt
```

### Step 2: Run Each Step Sequentially

```bash
# Step 1: Document Processing
python step1_document_processor.py

# Step 2: Build Encoder
python step2_build_encoder.py

# Step 3: Answer Extraction
python step3_answer_extractor.py

# Step 4: Complete QA Engine
python step4_qa_engine.py

# Step 5: Evaluation
python step5_evaluation.py

# Step 6: Web Interface
python step6_web_interface.py
# Then visit: http://localhost:8000
```

### Step 3: Add Your Own Documents

```bash
# Add .txt files to sample_documents/ directory
echo "Your content here" > sample_documents/my_document.txt

# Re-run step 4 to reload documents
python step4_qa_engine.py
```

## 📊 How It Works

### 1. Document Processing (Step 1)

- Loads documents from `sample_documents/` directory
- Cleans and normalizes text
- Splits into overlapping chunks (512 tokens, 50 overlap)
- Creates searchable document database

**Example:**
```python
processor = DocumentProcessor(max_chunk_length=512, chunk_overlap=50)
processor.add_documents_from_directory("sample_documents")
```

### 2. BERT Encoder (Step 2)

- Token embeddings: Maps words to vectors
- Position embeddings: Encodes word positions
- Segment embeddings: Distinguishes question vs document
- 12 transformer encoder blocks with multi-head attention

**Configuration:**
- d_model: 768 (or 128 for demo)
- num_heads: 12 (or 4 for demo)
- num_layers: 12 (or 2-4 for demo)
- Parameters: ~110M (BERT-base) or ~1M (demo)

### 3. Answer Extraction (Step 3)

- Encodes question-document pairs
- Predicts start position of answer
- Predicts end position of answer
- Extracts span: `text[start:end]`

**Example:**
```python
answer, start, end, confidence = qa_model.extract_answer(
    input_ids, segment_ids, attention_mask, tokenizer
)
```

### 4. QA Engine (Step 4)

- Searches for relevant document chunks
- Scores each chunk for relevance
- Extracts answers from top-k chunks
- Ranks answers by combined confidence

### 5. Evaluation (Step 5)

Metrics:
- **Exact Match (EM)**: % of exact correct answers
- **F1 Score**: Token-level overlap with ground truth

Expected scores (with proper training):
- EM: 80-85%
- F1: 88-92%

### 6. Web Interface (Step 6)

- FastAPI web server
- Interactive UI for asking questions
- REST API endpoints
- Document upload functionality

## 🎓 Learning Objectives

After completing this project, you will be able to:

✅ Build a complete QA system from scratch
✅ Use transformer encoders for text understanding
✅ Implement attention-based answer extraction
✅ Evaluate NLP models with standard metrics
✅ Deploy ML models as web services

## 📝 Important Notes

### Current Implementation

This is a **demonstration** version with:
- Randomly initialized weights (no pre-training)
- Simple word tokenizer (not WordPiece/BPE)
- Small model size (for fast experimentation)
- Basic retrieval (keyword matching)

### For Production Use

To achieve state-of-the-art results:

1. **Use Pre-trained Weights**
   ```python
   from transformers import BertForQuestionAnswering
   model = BertForQuestionAnswering.from_pretrained('bert-base-uncased')
   ```

2. **Fine-tune on SQuAD Dataset**
   - 100k+ question-answer pairs
   - Train for 2-3 epochs
   - Use proper tokenizer

3. **Advanced Retrieval**
   - Dense embeddings (BERT, Sentence-BERT)
   - Vector databases (FAISS, Pinecone)
   - Re-ranking models

4. **Production Optimizations**
   - Model quantization (INT8)
   - ONNX runtime
   - Batch processing
   - Caching

## 🔧 Customization

### Change Model Size

Edit model parameters in each step:

```python
encoder = BERTEncoder(
    vocab_size=vocab_size,
    d_model=768,      # Increase for more capacity
    num_heads=12,     # More heads = more patterns
    num_layers=12,    # Deeper = more understanding
    d_ff=3072         # Feed-forward size
)
```

### Add More Documents

Simply add `.txt` files to `sample_documents/`:

```bash
cp ~/my_docs/*.txt sample_documents/
```

### Change Chunk Size

```python
processor = DocumentProcessor(
    max_chunk_length=1024,  # Longer chunks
    chunk_overlap=100       # More overlap for continuity
)
```

## 🧪 Testing

Run all tests:

```bash
# Test each component
python step1_document_processor.py
python step2_build_encoder.py
python step3_answer_extractor.py

# Run evaluation
python step5_evaluation.py
```

Expected output:
- Document processing: ✓ Documents loaded
- Encoder: ✓ Embeddings generated
- Answer extraction: ✓ Spans predicted
- Evaluation: Metrics calculated (EM, F1)

## 📚 Resources

- [BERT Paper](https://arxiv.org/abs/1810.04805)
- [SQuAD Dataset](https://rajpurkar.github.io/SQuAD-explorer/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## 🎯 Review Checklist

See `REVIEW_CHECKLIST.md` for detailed review criteria.

Quick check:
- [ ] All 6 steps run without errors
- [ ] Can answer questions from documents
- [ ] Web interface works
- [ ] Evaluation produces metrics
- [ ] Code is well-documented

## 💡 Next Steps

After completing this project:

1. **Week 5**: Advanced Transformers (Fine-tuning, RAG, LoRA)
2. **Improvements**:
   - Load pre-trained BERT weights
   - Fine-tune on SQuAD
   - Add dense retrieval
   - Implement re-ranking
3. **Extensions**:
   - Multi-hop QA
   - Conversational QA
   - Visual QA (images + text)

## 🤝 Getting Help

If you encounter issues:

1. Check error messages carefully
2. Ensure all dependencies are installed
3. Verify `sample_documents/` exists with .txt files
4. Check Python version (3.8+)

## 📄 License

This is educational material for learning purposes.

---

**Congratulations on completing Week 4a Mini Project!** 🎉

You've built a real Question Answering system using transformers!
