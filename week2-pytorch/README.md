# Week 2: Neural Networks & Training

> **Building and Training Your First Neural Network**

## 🎯 Learning Objectives

By the end of Week 2, you will:
- Understand what neural networks are and how they work
- Build neural networks using PyTorch
- Implement the complete training loop (forward → loss → backward → update)
- Evaluate model performance using real metrics
- Train a model to solve a real business problem

## 📚 Content Overview

### Day 5-7: Introduction to Neural Networks (3 hours)
**File**: `day5_neural_network_intro.py`

**What You'll Learn**:
- Neural network architecture (layers, neurons, activations)
- Forward pass: Making predictions
- Loss functions: Measuring errors
- Building your first network in PyTorch

**Project**: Customer Churn Predictor
- Predict which customers will cancel their subscription
- Binary classification problem (churn: yes/no)
- Small dataset included for immediate hands-on practice

### Day 8-10: Training Neural Networks (3 hours)
**File**: `day8_training_loop.py`

**What You'll Learn**:
- The complete training loop
- Backward pass: Computing gradients automatically
- Optimizers: Updating weights intelligently
- Train/validation/test splits
- Evaluation metrics: Accuracy, precision, recall, F1-score

**Project**: Train and Evaluate the Churn Predictor
- Train model on customer data
- Monitor training progress
- Evaluate final performance
- Save and load trained models

## 📊 Sample Data Included

### `sample_customer_data.csv`
Customer subscription data with features:
- Demographics (age, gender, location)
- Usage metrics (login_frequency, session_duration, features_used)
- Support interactions (support_tickets, satisfaction_score)
- Label: churned (0=stayed, 1=left)

**500 rows** of realistic data ready to use!

## 🚀 Quick Start

```bash
cd week2-pytorch

# Day 5-7: Build your first neural network
python3 day5_neural_network_intro.py

# Day 8-10: Train the complete model
python3 day8_training_loop.py
```

## 📖 Visual Learning Aid

**`Week2-Neural-Network-Training.svg`**
- Visual representation of the training process
- Shows forward pass, loss calculation, backward pass, weight updates
- Great reference while coding!

## 🔑 Key Concepts

### Neural Network Layers
```python
# A simple 3-layer network
model = nn.Sequential(
    nn.Linear(10, 20),   # Input layer: 10 features → 20 neurons
    nn.ReLU(),           # Activation function
    nn.Linear(20, 10),   # Hidden layer: 20 → 10
    nn.ReLU(),           # Activation function
    nn.Linear(10, 1),    # Output layer: 10 → 1 (prediction)
    nn.Sigmoid()         # Output activation (0-1 for probability)
)
```

### Training Loop
```python
for epoch in range(100):
    # Forward pass
    predictions = model(inputs)

    # Calculate loss
    loss = criterion(predictions, labels)

    # Backward pass (PyTorch does this automatically!)
    optimizer.zero_grad()
    loss.backward()

    # Update weights
    optimizer.step()
```

### Evaluation
```python
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Make predictions
with torch.no_grad():
    predictions = model(test_data)

# Calculate metrics
accuracy = accuracy_score(true_labels, predicted_labels)
precision = precision_score(true_labels, predicted_labels)
recall = recall_score(true_labels, predicted_labels)
```

## 💡 What Makes This Week Different from Week 1

| Week 1: Tensors | Week 2: Neural Networks |
|----------------|------------------------|
| Data manipulation | Pattern learning |
| Manual calculations | Automatic learning |
| Static analysis | Adaptive models |
| Immediate results | Training required |
| Direct operations | Gradient descent |

## 🎓 Prerequisites

Before starting Week 2:
- ✅ Complete Week 1 (understand tensors)
- ✅ Comfortable with tensor operations
- ✅ Understand vectorization concepts

If you haven't done Week 1, start there first!

## 📈 Progress Tracking

- [ ] Understand neural network architecture
- [ ] Build a simple 3-layer network
- [ ] Implement forward pass manually
- [ ] Calculate loss with different loss functions
- [ ] Run the complete training loop
- [ ] Evaluate model with proper metrics
- [ ] Achieve >80% accuracy on test set
- [ ] Save and load trained models

## 🔥 Common Questions

**Q: Do I need to understand the math behind backpropagation?**
A: Not initially! PyTorch handles it automatically with `.backward()`. Understanding helps later, but you can build working models without deep math knowledge.

**Q: How much data do I need?**
A: For learning: our 500-row sample is perfect. For production: typically 1000s-millions depending on complexity.

**Q: What if my model doesn't learn (loss doesn't decrease)?**
A: Common issues:
- Learning rate too high or too low
- Wrong loss function
- Data not normalized
- Model too simple or too complex

We cover debugging in the exercises!

**Q: GPU required?**
A: No! The sample dataset trains in seconds on CPU. GPU becomes important for large datasets/models.

## 🎯 Success Criteria

By the end of Week 2, you should be able to:
1. ✅ Explain how neural networks learn (in plain English)
2. ✅ Build a neural network for binary classification
3. ✅ Train a model and monitor its progress
4. ✅ Evaluate performance using multiple metrics
5. ✅ Identify common training problems and fix them

## 🚀 Next Steps After Week 2

Once comfortable with Week 2:
- **Week 3**: Build a complete production ML system
- **Week 4**: Advanced topics (embeddings, RAG, transformers)
- **Projects**: Apply to your own datasets and problems

## 📚 Additional Resources

### Included in This Week
- ✅ 2 complete Python programs with extensive comments
- ✅ 500 rows of sample data (CSV)
- ✅ Data loading helper script
- ✅ Visual training diagram (SVG)
- ✅ This README with all concepts explained

### External (Optional)
- PyTorch official tutorial on neural networks
- 3Blue1Brown: Neural Networks series (YouTube)
- Fast.ai: Practical Deep Learning for Coders

## 🤝 Getting Help

If you get stuck:
1. Read the code comments carefully
2. Check the error message
3. Try the debugging tips in the code
4. Experiment with hyperparameters
5. Compare with Week 1 tensor operations

Remember: **Everyone struggles initially. Keep experimenting!**

---

**Ready to build your first neural network? Start with `day5_neural_network_intro.py`!** 🚀
