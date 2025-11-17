"""
Day 5-7: Introduction to Neural Networks
Building your first neural network with PyTorch

Learn: Architecture, layers, forward pass, loss functions
Project: Customer Churn Predictor
"""

import torch
import torch.nn as nn
import pandas as pd
import numpy as np

print("="*60)
print("WEEK 2 - DAY 5-7: NEURAL NETWORKS")
print("="*60)
print()

# Part 1: What is a Neural Network?
print("PART 1: Understanding Neural Networks")
print("-"*60)
print("""
A neural network is like a series of filters that transform data:
  
  Input → Layer 1 → Layer 2 → ... → Output
  
Each layer learns to detect patterns in the data.
For customer churn: it learns which behaviors indicate leaving.
""")

# Part 2: Building a Simple Network
print("\nPART 2: Build Your First Neural Network")
print("-"*60)

class SimpleChurnPredictor(nn.Module):
    """
    A 3-layer neural network to predict customer churn
    
    Architecture:
      Input (9 features) → Hidden (16) → Hidden (8) → Output (1)
    """
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(9, 16),    # Layer 1: 9 inputs → 16 neurons
            nn.ReLU(),           # Activation: Keep positive values
            nn.Linear(16, 8),    # Layer 2: 16 → 8
            nn.ReLU(),           
            nn.Linear(8, 1),     # Layer 3: 8 → 1 (probability)
            nn.Sigmoid()         # Output: 0 to 1 (probability of churn)
        )
    
    def forward(self, x):
        """Forward pass: Make a prediction"""
        return self.network(x)

# Create model
model = SimpleChurnPredictor()
print("Model created!")
print(model)
print()

# Part 3: Load Sample Data
print("PART 3: Load Customer Data")
print("-"*60)

try:
    df = pd.read_csv('sample_customer_data.csv')
    print(f"✓ Loaded {len(df)} customer records")
    print(f"\nSample data:")
    print(df.head())
    print(f"\nChurn distribution:")
    print(df['churned'].value_counts())
    
    # Prepare features
    feature_cols = ['age', 'months_subscribed', 'login_frequency', 
                   'session_duration_mins', 'features_used', 
                   'support_tickets', 'satisfaction_score']
    
    # Encode gender and location
    df['gender_M'] = (df['gender'] == 'M').astype(int)
    df['location_Urban'] = (df['location'] == 'Urban').astype(int)
    
    feature_cols.extend(['gender_M', 'location_Urban'])
    
    # Create tensors
    X = torch.tensor(df[feature_cols].values, dtype=torch.float32)
    y = torch.tensor(df['churned'].values, dtype=torch.float32).unsqueeze(1)
    
    print(f"\n✓ Features shape: {X.shape}")
    print(f"✓ Labels shape: {y.shape}")
    
except FileNotFoundError:
    print("⚠ Data file not found. Using synthetic data for demo.")
    X = torch.randn(100, 9)
    y = torch.randint(0, 2, (100, 1)).float()

print()

# Part 4: Forward Pass
print("PART 4: Making Predictions (Forward Pass)")
print("-"*60)

# Make predictions on first 5 customers
sample_input = X[:5]
sample_labels = y[:5]

with torch.no_grad():  # Don't track gradients for inference
    predictions = model(sample_input)

print("First 5 customers:")
for i in range(5):
    actual = "Churned" if sample_labels[i].item() == 1 else "Stayed"
    pred_prob = predictions[i].item()
    pred_label = "Churned" if pred_prob > 0.5 else "Stayed"
    
    print(f"  Customer {i+1}: Actual={actual}, "
          f"Predicted={pred_label} ({pred_prob:.3f})")

print()

# Part 5: Loss Functions
print("PART 5: Measuring Errors (Loss Functions)")
print("-"*60)

# Binary Cross Entropy Loss (for yes/no predictions)
criterion = nn.BCELoss()

loss = criterion(predictions, sample_labels)
print(f"Loss (error): {loss.item():.4f}")
print("""
Lower loss = better predictions
Initially (untrained): loss is around 0.69 (random guessing)
After training: loss should decrease significantly
""")

# Part 6: Understanding the Architecture
print("PART 6: What Each Layer Does")
print("-"*60)

# Manually demonstrate one forward pass
sample = X[0:1]  # Just one customer

print("Input features (9 values):")
print(sample)
print()

# Layer 1
layer1 = nn.Linear(9, 16)
hidden1 = torch.relu(layer1(sample))
print(f"After Layer 1: {hidden1.shape[1]} neurons activated")
print(f"Sample values: {hidden1[0,:5]}")
print()

# Layer 2  
layer2 = nn.Linear(16, 8)
hidden2 = torch.relu(layer2(hidden1))
print(f"After Layer 2: {hidden2.shape[1]} neurons activated")
print(f"Sample values: {hidden2[0,:5]}")
print()

# Output layer
layer3 = nn.Linear(8, 1)
output = torch.sigmoid(layer3(hidden2))
print(f"Final output: {output.item():.4f}")
print(f"Prediction: {'Churn' if output.item() > 0.5 else 'Stay'}")
print()

# Summary
print("="*60)
print("✅ DAY 5-7 COMPLETE!")
print("="*60)
print("""
Key Takeaways:
  1. Neural networks are layers of transformations
  2. Forward pass: Input → Layers → Prediction
  3. Loss function measures how wrong we are
  4. Model starts random - needs training!

Next Steps:
  • Run: python day8_training_loop.py
  • Learn how to train this model to make accurate predictions!
""")
