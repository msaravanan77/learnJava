# Hands-On AI/ML Roadmap for Experienced Programmers
## From C Programming to PyTorch: A Practical Journey

> **Your Background**: 20 years C programming, PAM product experience
> **Your Goal**: Understand AI/ML fundamentals through hands-on projects
> **Philosophy**: See it work first, understand why, then go deeper

---

## 🎯 Week 1: Understanding Tensors (The Foundation)

### Day 1-2: From C Arrays to Tensors

**What You Know (C)**:
```c
// 1D Array - list of numbers
int temperatures[7] = {72, 75, 68, 70, 73, 71, 69};

// 2D Array - table/matrix
int login_attempts[24][7];  // hours x days
```

**What's New (Python/PyTorch)**:
```python
import torch

# Same 1D array - but can run on GPU!
temperatures = torch.tensor([72, 75, 68, 70, 73, 71, 69])

# 2D array
login_attempts = torch.zeros(24, 7)  # hours x days

# 3D tensor - this is where it gets powerful
# Imagine: [users][days][metrics]
user_behavior = torch.zeros(1000, 30, 10)
```

**HANDS-ON PROJECT 1: Security Log Analyzer**
```python
# File: day1_tensor_basics.py
import torch

# Real-world: Analyze failed login patterns
# Shape: [hour_of_day, day_of_week]
failed_logins = torch.tensor([
    [5, 3, 2, 1, 2, 8, 12],   # Hour 0 (midnight)
    [2, 1, 1, 0, 1, 3, 5],    # Hour 1
    # ... 24 hours
])

# Find suspicious patterns
total_by_hour = failed_logins.sum(dim=1)  # Sum across days
total_by_day = failed_logins.sum(dim=0)   # Sum across hours

print("Suspicious hours:", torch.where(total_by_hour > 30))
print("Suspicious days:", torch.where(total_by_day > 50))
```

**Why This Matters**: Instead of writing loops in C, tensors let you operate on entire datasets at once - millions of times faster on GPUs.

---

### Day 3-4: Tensor Operations (Like Pointer Math, But Safer)

**What You Know (C)**:
```c
// Pointer arithmetic
int arr[5] = {1, 2, 3, 4, 5};
int* ptr = arr;
for(int i = 0; i < 5; i++) {
    arr[i] = arr[i] * 2;  // Double each element
}
```

**What's New (PyTorch)**:
```python
arr = torch.tensor([1, 2, 3, 4, 5])
arr = arr * 2  # All elements doubled - in parallel!

# Reshape (like casting, but smart)
matrix = arr.reshape(5, 1)  # Column vector

# Slicing (like C, but multi-dimensional)
batch = user_data[0:100, :, :]  # First 100 users, all days, all metrics
```

**HANDS-ON PROJECT 2: Password Strength Analyzer**
```python
# File: day3_password_analysis.py
import torch

# Each password represented as vector:
# [length, has_uppercase, has_digit, has_special, entropy_score]
passwords = torch.tensor([
    [8, 1, 1, 0, 42.5],   # Password: "Admin123"
    [12, 1, 1, 1, 68.2],  # Strong password
    [6, 0, 1, 0, 28.1],   # Weak: "pass12"
])

# Simple scoring (vectorized - no loops!)
length_score = passwords[:, 0] * 2
complexity_score = passwords[:, 1:4].sum(dim=1) * 10
entropy_score = passwords[:, 4]

total_score = length_score + complexity_score + entropy_score

print("Password Strengths:", total_score)
print("Weak passwords:", torch.where(total_score < 50))
```

---

## 🧠 Week 2: PyTorch Basics (Building Your First Model)

### Day 5-7: Neural Networks (Pattern Matchers)

**The Paradigm Shift**:
- **C Way**: You write `if (condition) { action }`
- **ML Way**: Model learns the conditions from examples

**HANDS-ON PROJECT 3: Detect Suspicious Logins**

```python
# File: day5_login_detector.py
import torch
import torch.nn as nn

# Define a simple neural network
class LoginDetector(nn.Module):
    def __init__(self):
        super().__init__()
        # Input: 5 features (time, location_distance, device_new, etc.)
        # Output: 1 score (0=normal, 1=suspicious)
        self.layer1 = nn.Linear(5, 10)  # 5 inputs → 10 neurons
        self.layer2 = nn.Linear(10, 1)  # 10 → 1 output

    def forward(self, x):
        x = torch.relu(self.layer1(x))  # Activation function
        x = torch.sigmoid(self.layer2(x))  # Squash to 0-1
        return x

# Create model
model = LoginDetector()

# Example login attempt:
# [hour, distance_km, is_new_device, failed_attempts_today, vpn_used]
login = torch.tensor([[2.0, 5000.0, 1.0, 3.0, 1.0]])

# Get prediction
suspicion_score = model(login)
print(f"Suspicion Score: {suspicion_score.item():.2f}")

# 0.0 = Normal, 1.0 = Highly Suspicious
```

**What Just Happened?**
1. Instead of writing rules, we created a structure that CAN learn rules
2. Currently untrained - it gives random predictions
3. Next: We'll train it with real examples

---

### Day 8-10: Training (Teaching the Model)

**HANDS-ON PROJECT 4: Train the Login Detector**

```python
# File: day8_train_model.py
import torch
import torch.nn as nn
import torch.optim as optim

# Same model from Day 5
model = LoginDetector()

# Training data: Features + Labels
# Label: 0 = Normal, 1 = Suspicious
training_data = torch.tensor([
    # hour, distance, new_device, failed_attempts, vpn
    [14.0, 5.0, 0.0, 0.0, 0.0],      # Normal
    [3.0, 5000.0, 1.0, 5.0, 1.0],    # Suspicious
    [9.0, 10.0, 0.0, 0.0, 0.0],      # Normal
    [2.0, 8000.0, 1.0, 8.0, 1.0],    # Suspicious
    # ... add 1000+ real examples
])

labels = torch.tensor([[0.0], [1.0], [0.0], [1.0]])  # Ground truth

# Training setup
criterion = nn.BCELoss()  # Measures how wrong we are
optimizer = optim.Adam(model.parameters(), lr=0.01)  # Adjusts weights

# Training loop
for epoch in range(100):
    # Forward pass
    predictions = model(training_data)
    loss = criterion(predictions, labels)

    # Backward pass (this is where learning happens!)
    optimizer.zero_grad()
    loss.backward()  # Calculate gradients
    optimizer.step()  # Update weights

    if epoch % 10 == 0:
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")

# Now model has learned patterns!
test_login = torch.tensor([[2.0, 9000.0, 1.0, 10.0, 1.0]])
print(f"New prediction: {model(test_login).item():.2f}")  # Should be close to 1.0
```

**Key Insight**: You provided examples, PyTorch adjusted millions of tiny weights to find patterns. This is learning!

---

## 🚀 Week 3: Real-World Project

### Project: PAM Privilege Escalation Detector

**HANDS-ON PROJECT 5: Complete System**

```python
# File: pam_escalation_detector.py
import torch
import torch.nn as nn
from datetime import datetime

class PrivilegeEscalationDetector(nn.Module):
    """
    Detects suspicious privilege escalation patterns
    Input features:
    - User risk score
    - Time since last escalation
    - Number of resources accessed
    - Deviation from normal pattern
    - Cross-account activity
    """
    def __init__(self):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(5, 20),
            nn.ReLU(),
            nn.Dropout(0.2),  # Prevents overfitting
            nn.Linear(20, 10),
            nn.ReLU(),
            nn.Linear(10, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)

# Load your PAM logs (CSV format)
def load_pam_logs(csv_path):
    # Convert your logs to tensors
    # This is where your C experience helps - data preprocessing!
    pass

# Train on historical data
def train_on_historical_incidents():
    model = PrivilegeEscalationDetector()
    # Load known incidents (labeled data)
    # Train model
    # Save model: torch.save(model.state_dict(), 'pam_detector.pth')
    pass

# Real-time detection
def analyze_live_escalation(user_id, features):
    model = PrivilegeEscalationDetector()
    model.load_state_dict(torch.load('pam_detector.pth'))
    model.eval()

    with torch.no_grad():
        risk = model(torch.tensor([features]))

    if risk > 0.8:
        alert_security_team(user_id, risk.item())

    return risk.item()
```

---

## 🔧 Week 4: Advanced Topics (MCP, RAG, Embeddings)

### Understanding Embeddings (The Secret Sauce)

**What Problem Does This Solve?**
- Traditional: Search logs with regex/keywords → misses similar but differently-worded issues
- Embeddings: Convert text to numbers that capture meaning → finds semantically similar issues

**HANDS-ON PROJECT 6: Intelligent Log Search**

```python
# File: intelligent_log_search.py
from sentence_transformers import SentenceTransformer
import torch

# Load pre-trained embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Your PAM logs
logs = [
    "User admin attempted sudo access at 2 AM",
    "Failed authentication for root user",
    "Successful privilege escalation for john_doe",
    "Database connection timeout",
    "Memory allocation failed",
]

# Convert to embeddings (vectors that capture meaning)
log_embeddings = model.encode(logs, convert_to_tensor=True)

# Search query
query = "unauthorized admin access"
query_embedding = model.encode(query, convert_to_tensor=True)

# Find similar logs (cosine similarity)
similarities = torch.nn.functional.cosine_similarity(
    query_embedding.unsqueeze(0),
    log_embeddings
)

# Get most similar
top_match = torch.argmax(similarities)
print(f"Most relevant log: {logs[top_match]}")
print(f"Similarity: {similarities[top_match]:.2f}")
```

**Why This Is Powerful**: Even though your query didn't use exact words from logs, it found semantically similar entries!

---

### RAG (Retrieval-Augmented Generation)

**What Is It?**
- Traditional: Ask ChatGPT about YOUR company data → It doesn't know
- RAG: Find relevant docs from YOUR data → Send to ChatGPT with context → Get accurate answer

**HANDS-ON PROJECT 7: PAM Documentation Assistant**

```python
# File: pam_assistant.py
import anthropic
from sentence_transformers import SentenceTransformer
import torch

class PAMDocAssistant:
    def __init__(self, doc_folder):
        self.embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.docs = self.load_docs(doc_folder)
        self.doc_embeddings = self.embed_model.encode(self.docs, convert_to_tensor=True)
        self.client = anthropic.Anthropic()

    def load_docs(self, folder):
        # Load all your PAM documentation, runbooks, etc.
        docs = []
        # ... read files ...
        return docs

    def find_relevant_docs(self, query, top_k=3):
        query_emb = self.embed_model.encode(query, convert_to_tensor=True)
        similarities = torch.nn.functional.cosine_similarity(
            query_emb.unsqueeze(0),
            self.doc_embeddings
        )
        top_indices = torch.topk(similarities, top_k).indices
        return [self.docs[i] for i in top_indices]

    def ask(self, question):
        # 1. Find relevant docs (Retrieval)
        relevant_docs = self.find_relevant_docs(question)

        # 2. Create context
        context = "\n\n".join(relevant_docs)

        # 3. Ask Claude with context (Augmented Generation)
        response = self.client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{
                "role": "user",
                "content": f"""Based on this documentation:

{context}

Answer this question: {question}"""
            }]
        )

        return response.content[0].text

# Usage
assistant = PAMDocAssistant("/path/to/pam/docs")
answer = assistant.ask("How do I configure password rotation for AWS accounts?")
print(answer)
```

**This Is What You're Using Now!** Claude Code uses similar techniques to understand your codebase.

---

### MCP (Model Context Protocol)

**What Problem Does It Solve?**
- Claude doesn't know about YOUR live systems
- MCP: Let Claude safely interact with your tools/databases/APIs

**HANDS-ON PROJECT 8: MCP Server for PAM System**

```python
# File: pam_mcp_server.py
# This lets Claude query your PAM system directly!

from mcp.server import Server
from mcp.server.stdio import stdio_server
import json

# Your PAM API wrapper
class PAMSystem:
    def get_user_privileges(self, user_id):
        # Query your actual PAM database
        return {"user": user_id, "roles": ["admin", "db_reader"]}

    def get_recent_escalations(self, hours=24):
        # Query escalation logs
        return [{"user": "john", "time": "2025-01-15T14:30", "resource": "prod-db"}]

pam = PAMSystem()
server = Server("pam-mcp")

@server.list_tools()
async def list_tools():
    return [
        {
            "name": "get_user_privileges",
            "description": "Get current privileges for a user",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "string"}
                }
            }
        },
        {
            "name": "get_recent_escalations",
            "description": "Get recent privilege escalations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "hours": {"type": "number"}
                }
            }
        }
    ]

@server.call_tool()
async def call_tool(name, arguments):
    if name == "get_user_privileges":
        return pam.get_user_privileges(arguments["user_id"])
    elif name == "get_recent_escalations":
        return pam.get_recent_escalations(arguments.get("hours", 24))

# Run server
async def main():
    async with stdio_server() as streams:
        await server.run(streams[0], streams[1])

# Now Claude can ask: "Show me john's privileges" and get LIVE data!
```

---

## 📚 Your Learning Path Summary

### Week 1: Tensors
- ✅ Understand multi-dimensional arrays
- ✅ Build security log analyzer
- ✅ See GPU acceleration benefits

### Week 2: PyTorch
- ✅ Build first neural network
- ✅ Train a model
- ✅ Understand forward/backward pass

### Week 3: Real Project
- ✅ PAM escalation detector
- ✅ Use real company data
- ✅ See actual value

### Week 4: Advanced
- ✅ Embeddings for semantic search
- ✅ RAG for documentation assistant
- ✅ MCP for live system integration

---

## 🎓 Key Insights for C Programmers

| C Concept | ML Equivalent | Why It Matters |
|-----------|---------------|----------------|
| `int arr[100]` | `torch.tensor([...])` | Same concept, runs on GPU |
| `for` loops | Vectorized operations | Millions of times faster |
| `if/else` rules | Trained model | Discovers patterns you didn't know |
| Pointers | Tensor views/slicing | Memory-efficient, no copies |
| `malloc/free` | Auto memory management | PyTorch handles it |
| Debugging with `gdb` | `model.eval()`, `torch.no_grad()` | Different tools, same concept |

---

## 🚦 Getting Started TODAY

### Setup (15 minutes)
```bash
# Install Python & PyTorch
pip install torch torchvision sentence-transformers anthropic

# Create project folder
mkdir ai-learning
cd ai-learning
```

### Run First Example (5 minutes)
```python
# test.py
import torch

# Your first tensor!
data = torch.tensor([1, 2, 3, 4, 5])
print("Original:", data)
print("Doubled:", data * 2)
print("Sum:", data.sum())

# Congratulations - you just did tensor math!
```

---

## 📖 Resources (NOT 1000-page books!)

### Interactive & Hands-on:
1. **Fast.ai** - Practical Deep Learning (top-down approach)
2. **PyTorch Tutorials** - Official hands-on examples
3. **Kaggle Learn** - Micro-courses with real datasets

### For C Programmers:
1. **PyTorch C++ API** - If you want to stay close to C
2. **CUDA Programming** - Understand GPU parallel processing

---

## ✨ Final Motivation

**You have 20 years of system programming experience.**
**You understand memory, performance, and building real products.**

AI/ML is just:
- **New data structures** (tensors instead of arrays)
- **New algorithms** (gradient descent instead of sorting)
- **New paradigm** (learning instead of coding rules)

The fundamentals you know - debugging, optimization, production systems - are STILL the hard parts.

PyTorch is just a library. Tensors are just arrays. Neural networks are just function approximators.

**You've got this. Start building today.**

---

*Next: Pick Day 1 project and run it. See it work. Then ask "why?" That's how you'll learn 10x faster than reading books.*
