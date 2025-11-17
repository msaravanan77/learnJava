"""
Day 8-10: Training Neural Networks
The complete training loop

Learn: Training, validation, evaluation, saving models
Project: Train the Customer Churn Predictor
"""

import torch
import torch.nn as nn
import torch.optim as optim
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

print("="*60)
print("WEEK 2 - DAY 8-10: TRAINING NEURAL NETWORKS")
print("="*60)
print()

# Model Definition (same as Day 5)
class ChurnPredictor(nn.Module):
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(9, 16),
            nn.ReLU(),
            nn.Linear(16, 8),
            nn.ReLU(),
            nn.Linear(8, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        return self.network(x)

# Load and Prepare Data
print("Loading data...")
try:
    df = pd.read_csv('sample_customer_data.csv')
    
    # Prepare features
    df['gender_M'] = (df['gender'] == 'M').astype(int)
    df['location_Urban'] = (df['location'] == 'Urban').astype(int)
    
    feature_cols = ['age', 'months_subscribed', 'login_frequency', 
                   'session_duration_mins', 'features_used', 
                   'support_tickets', 'satisfaction_score',
                   'gender_M', 'location_Urban']
    
    X = df[feature_cols].values
    y = df['churned'].values
    
    # Normalize features (important for training!)
    X = (X - X.mean(axis=0)) / (X.std(axis=0) + 1e-8)
    
    # Split: 70% train, 15% val, 15% test
    X_temp, X_test, y_temp, y_test = train_test_split(X, y, test_size=0.15, random_state=42)
    X_train, X_val, y_train, y_val = train_test_split(X_temp, y_temp, test_size=0.176, random_state=42)
    
    # Convert to tensors
    X_train_t = torch.tensor(X_train, dtype=torch.float32)
    y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
    X_val_t = torch.tensor(X_val, dtype=torch.float32)
    y_val_t = torch.tensor(y_val, dtype=torch.float32).unsqueeze(1)
    X_test_t = torch.tensor(X_test, dtype=torch.float32)
    y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)
    
    print(f"✓ Train set: {len(X_train)} samples")
    print(f"✓ Val set: {len(X_val)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    print()
    
except FileNotFoundError:
    print("⚠ Using synthetic data")
    X_train_t = torch.randn(350, 9)
    y_train_t = torch.randint(0, 2, (350, 1)).float()
    X_val_t = torch.randn(75, 9)
    y_val_t = torch.randint(0, 2, (75, 1)).float()
    X_test_t = torch.randn(75, 9)
    y_test_t = torch.randint(0, 2, (75, 1)).float()

# Initialize Model, Loss, Optimizer
model = ChurnPredictor()
criterion = nn.BCELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

print("THE TRAINING LOOP")
print("="*60)
print()

# Training Loop
num_epochs = 100
train_losses = []
val_losses = []

for epoch in range(num_epochs):
    # 1. FORWARD PASS (Training)
    model.train()
    train_predictions = model(X_train_t)
    train_loss = criterion(train_predictions, y_train_t)
    
    # 2. BACKWARD PASS
    optimizer.zero_grad()  # Clear old gradients
    train_loss.backward()  # Compute new gradients
    
    # 3. UPDATE WEIGHTS
    optimizer.step()
    
    # 4. VALIDATION (no gradient updates)
    model.eval()
    with torch.no_grad():
        val_predictions = model(X_val_t)
        val_loss = criterion(val_predictions, y_val_t)
    
    train_losses.append(train_loss.item())
    val_losses.append(val_loss.item())
    
    # Print progress every 10 epochs
    if (epoch + 1) % 10 == 0:
        print(f"Epoch {epoch+1:3d}/{num_epochs} | "
              f"Train Loss: {train_loss.item():.4f} | "
              f"Val Loss: {val_loss.item():.4f}")

print()
print("="*60)
print("TRAINING COMPLETE!")
print("="*60)
print()

# Evaluation on Test Set
print("FINAL EVALUATION (on unseen test set)")
print("-"*60)

model.eval()
with torch.no_grad():
    test_predictions = model(X_test_t)
    test_loss = criterion(test_predictions, y_test_t)
    
    # Convert probabilities to binary predictions
    test_pred_binary = (test_predictions > 0.5).float()
    y_test_np = y_test_t.numpy()
    test_pred_np = test_pred_binary.numpy()
    
    # Calculate metrics
    accuracy = accuracy_score(y_test_np, test_pred_np)
    precision = precision_score(y_test_np, test_pred_np, zero_division=0)
    recall = recall_score(y_test_np, test_pred_np, zero_division=0)
    f1 = f1_score(y_test_np, test_pred_np, zero_division=0)

print(f"Test Loss: {test_loss.item():.4f}")
print(f"Accuracy: {accuracy*100:.2f}%")
print(f"Precision: {precision*100:.2f}%")
print(f"Recall: {recall*100:.2f}%")
print(f"F1-Score: {f1:.4f}")
print()

print("What these metrics mean:")
print(f"  • Accuracy: {accuracy*100:.1f}% of predictions were correct")
print(f"  • Precision: {precision*100:.1f}% of predicted churns were actual churns")
print(f"  • Recall: {recall*100:.1f}% of actual churns were detected")
print()

# Save Model
torch.save(model.state_dict(), 'churn_model.pth')
print("✓ Model saved to 'churn_model.pth'")
print()

# Demo: Predict on new customer
print("DEMO: Predict on a New Customer")
print("-"*60)
print("""
New customer profile:
  Age: 45, Months: 6, Logins: 8, Session: 20 mins
  Features used: 3, Support tickets: 3, Satisfaction: 2.5
  Gender: Female, Location: Suburban
""")

new_customer = torch.tensor([[
    0.5,   # age (normalized)
    -0.8,  # months_subscribed  
    -0.9,  # login_frequency
    -1.0,  # session_duration
    -1.1,  # features_used
    1.2,   # support_tickets (high!)
    -1.5,  # satisfaction_score (low!)
    0.0,   # gender (F=0)
    0.0    # location (Suburban=0)
]], dtype=torch.float32)

with torch.no_grad():
    churn_prob = model(new_customer).item()

print(f"Churn Probability: {churn_prob*100:.1f}%")
print(f"Prediction: {'HIGH RISK - Likely to churn' if churn_prob > 0.5 else 'Low risk'}")
print()

# Summary
print("="*60)
print("✅ DAY 8-10 COMPLETE!")
print("="*60)
print("""
You've successfully:
  1. ✓ Trained a neural network from scratch
  2. ✓ Monitored training with validation set
  3. ✓ Evaluated performance on test set
  4. ✓ Saved the trained model
  5. ✓ Made predictions on new data

Next Steps:
  • Experiment with different architectures (more layers, neurons)
  • Try different learning rates and optimizers
  • Week 3: Build a complete production system!
""")
