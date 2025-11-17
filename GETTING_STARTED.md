# Getting Started - Your First 30 Minutes

Welcome! You're about to take your first steps into AI/ML. This guide will get you from zero to running code in 30 minutes.

## What You'll Do

1. **5 min**: Set up your environment
2. **10 min**: Run your first tensor program
3. **15 min**: Understand what just happened

## Step-by-Step Guide

### Step 1: Setup (5 minutes)

```bash
# Option A: Automatic setup (recommended)
bash setup.sh

# Option B: Manual setup
pip3 install torch torchvision numpy
```

**Verify installation:**
```bash
python3 -c "import torch; print(f'PyTorch {torch.__version__} installed successfully!')"
```

You should see: `PyTorch X.X.X installed successfully!`

---

### Step 2: Run Your First Program (10 minutes)

```bash
cd week1-tensors
python3 day1_tensor_basics.py
```

**What you'll see:**
- Tensor basics (arrays on steroids!)
- Security log analysis
- Real-time anomaly detection
- Performance comparisons

**Expected output:**
```
🚀 ======================================================== 🚀
   Welcome to PyTorch Tensors for C Programmers!
🚀 ======================================================== 🚀

============================================================
PART 1: C Arrays vs PyTorch Tensors
============================================================
Temperatures tensor: tensor([72, 75, 68, 70, 73, 71, 69])
Type: torch.int64
Shape: torch.Size([7])
Device: cpu

Average temperature: 71.14°F
Days above average: tensor([72, 75, 73])

[... more output ...]
```

---

### Step 3: Understand What Happened (15 minutes)

Open `day1_tensor_basics.py` in your favorite editor.

**Key concepts to notice:**

#### 1. Creating Tensors (Like C Arrays)
```python
# In C: int temps[7] = {72, 75, 68, 70, 73, 71, 69};
# In PyTorch:
temperatures = torch.tensor([72, 75, 68, 70, 73, 71, 69])
```

#### 2. No Loops Needed!
```python
# In C: Loop through array to sum
# for(int i=0; i<7; i++) sum += temps[i];

# In PyTorch: One operation
avg = temperatures.float().mean()
```

#### 3. Boolean Indexing (Super Powerful)
```python
# Get all values above average - no loop!
above_avg = temperatures[temperatures > avg]
```

#### 4. Multi-dimensional Operations
```python
# 2D array: 24 hours x 7 days
login_attempts = torch.randint(0, 20, (24, 7))

# Sum by hour (across all days) - no nested loops!
total_by_hour = login_attempts.sum(dim=1)
```

---

### Step 4: Experiment! (Next 30+ minutes)

Now that it's working, try modifying the code:

**Easy modifications:**
1. Change the failed login data in `real_world_security_analysis()`
2. Adjust the threshold for "suspicious hours"
3. Add a new day to the week

**Medium modifications:**
1. Add a new analysis: Find the most dangerous hour of the week
2. Create alerts for specific patterns
3. Calculate moving averages

**Challenge modifications:**
1. Load real log data from a CSV file
2. Add visualization (you'll need matplotlib)
3. Create a function to predict next week's pattern

---

### Next Steps

After you're comfortable with Day 1:

```bash
# Run Day 2: Password Analysis
python3 day2_password_analysis.py
```

This will show you:
- How to work with structured data
- Batch processing (analyze 1000s of passwords at once)
- Building a real security tool

---

## Common Issues & Solutions

### "ImportError: No module named 'torch'"
**Solution:**
```bash
pip3 install torch
# or
python3 -m pip install torch
```

### "Command 'python3' not found"
**Solution:** You might need to use `python` instead:
```bash
python day1_tensor_basics.py
```

### Setup script fails
**Solution:** Manual installation:
```bash
pip3 install torch>=2.0.0 torchvision>=0.15.0 numpy>=1.24.0
```

### Want to use GPU?
PyTorch CPU version is fine for learning. When you want GPU:
```bash
# Check if CUDA is available
python3 -c "import torch; print(torch.cuda.is_available())"
```

---

## Quick Reference

### Running Programs
```bash
# Week 1
cd week1-tensors
python3 day1_tensor_basics.py
python3 day2_password_analysis.py

# Later weeks (as you progress)
cd week2-pytorch
python3 day5_neural_network_intro.py
```

### File Structure
```
learnJava/
├── README.md                          ← Overview
├── GETTING_STARTED.md                 ← This file
├── HANDSON_ROADMAP.md                 ← Detailed curriculum
├── AI-Fundamentals-Architecture.svg   ← Visual guide
├── setup.sh                           ← Quick setup
├── requirements.txt                   ← Dependencies
└── week1-tensors/                     ← Start here!
    ├── day1_tensor_basics.py          ← Your first program
    └── day2_password_analysis.py      ← Real-world tool
```

---

## Learning Resources

### Inside This Repository
1. **README.md** - Big picture overview
2. **HANDSON_ROADMAP.md** - Complete 4-week curriculum with code
3. **AI-Fundamentals-Architecture.svg** - Visual architecture diagram
4. **week1-tensors/** - Runnable code with extensive comments

### When You're Ready for More
- **PyTorch Tutorials**: https://pytorch.org/tutorials/
- **Fast.ai**: https://www.fast.ai/ (practical approach)
- **3Blue1Brown Neural Networks**: YouTube series (visual explanations)

---

## Your First 30 Minutes: Checklist

- [ ] Run `setup.sh` or install dependencies
- [ ] Verify PyTorch is installed
- [ ] Run `day1_tensor_basics.py` successfully
- [ ] Read through the code with comments
- [ ] Modify at least one value and re-run
- [ ] Run `day2_password_analysis.py`
- [ ] Open `HANDSON_ROADMAP.md` to see what's next

---

## What's Next?

After completing your first 30 minutes:

**Short term (This week)**:
- Complete Week 1 (Tensors)
- Experiment with the code
- Try loading your own data

**Medium term (This month)**:
- Complete all 4 weeks
- Build a custom project for your domain
- Share your knowledge with colleagues

**Long term**:
- Apply ML to real problems at work
- Deepen knowledge in areas you find interesting
- Stay current with ML developments

---

## Questions?

As you go through this:
1. Read the code comments - they explain everything
2. Check `HANDSON_ROADMAP.md` for detailed explanations
3. Google is your friend - PyTorch has great documentation
4. Experiment! You can't break anything.

---

## Remember

> "The best way to learn is to build. Start small, see results, understand deeply, then scale up."

You don't need to understand everything perfectly before moving on. Understanding comes from **doing**, not just reading.

**Now go run that first program!**

```bash
cd week1-tensors && python3 day1_tensor_basics.py
```

See you on the other side! 🚀
