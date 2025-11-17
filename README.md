# AI/ML Fundamentals: A Hands-On Journey for Experienced Programmers

> **For C Programmers Who Want to Understand AI - Not Just Use It**

## 🎯 What This Is

This is a **practical, hands-on learning path** designed specifically for experienced programmers (like you, with 20 years of C experience) who want to:

- Understand what AI/ML really is and what problems it solves
- Learn PyTorch, tensors, and neural networks from first principles
- Build real-world projects (not toy examples)
- See the connection between traditional programming and AI/ML
- Understand tools you're already using (Claude, Copilot, etc.)

## 📋 Prerequisites

- **Programming experience**: You know how to code (any language)
- **Basic math**: High school algebra (you don't need calculus to start!)
- **Curiosity**: Willingness to experiment and break things
- **Python basics**: Variables, functions, loops (we'll teach you the rest)

## 🚀 Quick Start (5 Minutes)

```bash
# 1. Make sure Python is installed (3.8 or higher)
python3 --version

# 2. Install PyTorch
pip3 install torch torchvision numpy

# 3. Run your first tensor program
cd week1-tensors
python3 day1_tensor_basics.py
```

**That's it!** You just ran your first AI/ML code.

## 📚 Learning Path Overview

### Week 1: Tensors - The Foundation
**Goal**: Understand what tensors are and why they matter

| Day | Topic | Project | Time |
|-----|-------|---------|------|
| 1 | C Arrays → Tensors | Security log analyzer | 2 hrs |
| 2 | Tensor operations | Password strength analyzer | 2 hrs |
| 3 | Multi-dimensional tensors | Image processing basics | 2 hrs |

**What You'll Learn**:
- Tensors are just multi-dimensional arrays
- They run on GPUs for massive parallelization
- No loops needed - vectorized operations are 10-100x faster
- Real security applications using just tensors

### Week 2: PyTorch Basics
**Goal**: Build and train your first neural network

| Day | Topic | Project | Time |
|-----|-------|---------|------|
| 5-7 | Neural networks | Login anomaly detector | 3 hrs |
| 8-10 | Training models | Train the detector | 3 hrs |

**What You'll Learn**:
- Neural networks are pattern matchers
- Training = adjusting weights to fit data
- Forward pass (prediction) vs backward pass (learning)
- How to evaluate model performance

### Week 3: Real-World Project
**Goal**: Build a production-ready ML system

**Project**: PAM Privilege Escalation Detector
- Use real access logs (or synthetic data)
- Train a model to detect suspicious patterns
- Deploy it as a monitoring tool
- See actual value in your domain

### Week 4: Advanced Topics
**Goal**: Understand modern AI applications

- **Embeddings**: Convert text/data to meaningful vectors
- **RAG** (Retrieval-Augmented Generation): Make Claude/GPT understand YOUR data
- **MCP** (Model Context Protocol): Integrate AI with your systems
- Build: Custom documentation assistant for your codebase

## 🎨 The Big Picture - Visual Learning Guide

We've created **3 professional architecture diagrams** that serve as your visual roadmap. Open these SVG files in any browser:

### 1. AI-Fundamentals-Architecture.svg (Foundation)
**The 30,000-foot view** - Start here!
- Traditional programming vs AI/ML
- What tensors are and why they matter
- The complete AI/ML stack
- Real-world applications
- Your 4-week learning path

### 2. AI-Neural-Networks-Learning.svg (Deep Dive)
**How learning actually works**
- Visual neural network structure
- Forward pass (prediction)
- Backward pass (learning)
- Weight updates through gradient descent
- Why training works

### 3. AI-ML-Pipeline-Complete.svg (Production)
**From data to deployment**
- The complete 6-phase ML lifecycle
- Real-world example with actual code
- Common pitfalls and solutions
- Production deployment checklist
- Monitoring and maintenance

## 🏃 Getting Started TODAY

### Step 1: Environment Setup (5 min)
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Install PyTorch
pip3 install torch torchvision numpy
```

### Step 2: Run First Example (5 min)
```bash
cd week1-tensors
python3 day1_tensor_basics.py
```

You should see output analyzing failed login patterns. **Congratulations - you just did ML!**

### Step 3: Understand What Happened (15 min)
- Open `day1_tensor_basics.py` in your editor
- Read through the code with comments
- Try changing some values
- Run it again

### Step 4: Next Example (30 min)
```bash
python3 day2_password_analysis.py
```

## 🎓 For C Programmers: Translation Guide

| C Concept | ML/PyTorch Equivalent | Why |
|-----------|----------------------|-----|
| `int arr[100]` | `torch.tensor([...])` | Same idea, runs on GPU |
| `for` loops | Vectorized ops | 10-100x faster |
| `if/else` rules | Trained model | Learns patterns automatically |
| `malloc/free` | Automatic memory mgmt | PyTorch handles it |
| Pointers | Tensor views/slicing | No copies, efficient |
| `gdb` debugging | `model.eval()`, `print()` | Different tools, same goal |

**Key Insight**: Your C knowledge is an advantage! You understand:
- Memory layout (important for tensor shapes)
- Performance optimization (critical for ML)
- Systems thinking (essential for production ML)

## 📖 Key Resources

### Start Here
1. **AI-Fundamentals-Architecture.svg** - Visual overview (your "bible" first page)
2. **HANDSON_ROADMAP.md** - Detailed roadmap with all code examples
3. **week1-tensors/** - Working code you can run immediately

### External (After Week 1)
- **PyTorch Official Tutorial** - After you've run our examples
- **Fast.ai** - Practical deep learning (top-down approach)
- **3Blue1Brown Neural Networks** - Visual explanation (YouTube)

## 💡 Philosophy: Learning by Doing

**Traditional approach** (doesn't work):
1. Read 1000 pages → 2. Learn all math → 3. Finally code → 4. Forgot why you started

**Our approach** (actually works):
1. Run code in 5 minutes → 2. See it work → 3. Learn theory → 4. Build something real

## 🎯 Success Criteria

After 4 weeks, you should be able to:
- ✅ Explain what tensors are and why they matter
- ✅ Build and train a simple neural network
- ✅ Apply ML to a real problem in your domain
- ✅ Understand how Claude/GPT work conceptually
- ✅ Build a RAG system for your company's docs
- ✅ Confidently explore advanced topics

## 🎉 Let's Begin!

```bash
# Your first command
cd week1-tensors
python3 day1_tensor_basics.py
```

**See you on the other side - where you understand AI, not just use it!**

---

*Created for programmers who value understanding over hype, and building over theory.*
