# Week 3: Building a Production ML System

> **Project: Complete Product Recommendation Engine**

## 🎯 Project Overview

In Week 3, you'll build a **complete, production-ready recommendation system** from scratch. This isn't a toy example - it's a real system you could deploy in production.

**What You're Building:**
- Collaborative filtering recommendation engine
- Complete data processing pipeline
- Model training with proper validation
- REST API for serving recommendations
- Performance monitoring and evaluation
- All ready for production deployment

**Business Impact:**
- Personalized product recommendations
- Increased user engagement
- Higher conversion rates
- Measurable revenue impact

## 📚 Learning Objectives

By the end of Week 3, you will:
- ✅ Build a complete ML system from raw data to API
- ✅ Implement collaborative filtering (user-based & item-based)
- ✅ Deploy a neural network recommendation model
- ✅ Create a REST API with FastAPI
- ✅ Evaluate recommendation quality properly
- ✅ Understand production ML best practices
- ✅ Handle real-world data challenges

## 📁 Project Structure

```
week3-real-project/
├── README.md                          # This file
├── Week3-Recommendation-System.svg    # Architecture diagram
│
├── data/
│   ├── products.csv                   # Product catalog (100 items)
│   ├── users.csv                      # User profiles (200 users)
│   ├── interactions.csv               # User-item interactions (5000+)
│   └── ratings.csv                    # User ratings (3000+)
│
├── step1_data_preparation.py          # Load & clean data
├── step2_feature_engineering.py       # Create features for ML
├── step3_train_model.py               # Train recommendation model
├── step4_evaluate_model.py            # Measure performance
├── step5_api_server.py                # REST API for serving
├── step6_complete_pipeline.py         # End-to-end workflow
│
├── helpers.py                         # Utility functions
├── requirements.txt                   # Python dependencies
└── models/                            # Saved trained models
    └── recommendation_model.pth
```

## 🚀 Quick Start

### Setup (5 minutes)
```bash
cd week3-real-project

# Install dependencies
pip install -r requirements.txt

# Verify data files
ls data/
```

### Run the Complete Pipeline (10 minutes)
```bash
# Option 1: Run everything at once
python step6_complete_pipeline.py

# Option 2: Step-by-step learning
python step1_data_preparation.py      # Load & explore data
python step2_feature_engineering.py   # Create features
python step3_train_model.py           # Train model
python step4_evaluate_model.py        # Evaluate results
python step5_api_server.py            # Start API server (in separate terminal)
```

### Test the API
```bash
# In a new terminal, test recommendations
curl http://localhost:8000/recommend/user/42
```

## 📊 Sample Data Included

### Products Catalog (100 items)
```csv
product_id,name,category,price,description,stock
1,Wireless Headphones,Electronics,79.99,Premium sound quality,150
2,Running Shoes,Sports,89.99,Lightweight and comfortable,80
...
```

### User Interactions (5000+ events)
```csv
user_id,product_id,interaction_type,timestamp,session_duration
15,42,view,2024-01-15 14:23:10,45
15,42,add_to_cart,2024-01-15 14:25:32,120
15,42,purchase,2024-01-15 14:27:18,180
...
```

### Ratings (3000+ ratings)
```csv
user_id,product_id,rating,timestamp
23,15,4.5,2024-01-10 10:15:22
23,28,5.0,2024-01-11 15:42:18
...
```

## 🏗️ Architecture Overview

**See `Week3-Recommendation-System.svg` for the complete visual architecture.**

### System Components

1. **Data Layer**
   - Raw data ingestion
   - Data validation & cleaning
   - Feature engineering

2. **Model Layer**
   - Collaborative filtering
   - Neural network embeddings
   - Model training & validation

3. **API Layer**
   - REST endpoints
   - Request validation
   - Response caching

4. **Monitoring Layer**
   - Performance metrics
   - A/B testing support
   - Logging & debugging

## 📖 Step-by-Step Guide

### Step 1: Data Preparation (Day 1)

**File**: `step1_data_preparation.py`

**What You'll Learn:**
- Load multiple data sources
- Explore data distributions
- Handle missing values
- Merge datasets properly

**Output:**
- Clean, merged dataset
- Data quality report
- Basic statistics

```python
# Example usage
from step1_data_preparation import DataLoader

loader = DataLoader()
data = loader.load_all_data()
loader.print_summary()
```

### Step 2: Feature Engineering (Day 1-2)

**File**: `step2_feature_engineering.py`

**What You'll Learn:**
- Create user features (preferences, history, behavior)
- Create item features (popularity, category, price tier)
- Interaction features (recency, frequency, engagement)
- Feature normalization

**Output:**
- User-item feature matrix
- Feature importance analysis

```python
# Example usage
from step2_feature_engineering import FeatureEngineer

engineer = FeatureEngineer(data)
features = engineer.create_all_features()
```

### Step 3: Train Model (Day 2-3)

**File**: `step3_train_model.py`

**What You'll Learn:**
- Build collaborative filtering model
- Train neural network embeddings
- Hyperparameter tuning
- Model validation strategies

**Output:**
- Trained recommendation model
- Training curves
- Saved model checkpoint

```python
# Example usage
from step3_train_model import RecommendationModel

model = RecommendationModel()
model.train(train_data, val_data)
model.save('models/recommendation_model.pth')
```

### Step 4: Evaluate Model (Day 3)

**File**: `step4_evaluate_model.py`

**What You'll Learn:**
- Recommendation metrics (Precision@K, Recall@K, NDCG)
- A/B testing setup
- Business metrics (CTR, conversion rate)
- Model debugging techniques

**Output:**
- Performance report
- Recommendation examples
- Error analysis

```python
# Example usage
from step4_evaluate_model import ModelEvaluator

evaluator = ModelEvaluator(model, test_data)
metrics = evaluator.evaluate()
evaluator.print_report()
```

### Step 5: API Server (Day 4)

**File**: `step5_api_server.py`

**What You'll Learn:**
- Build REST API with FastAPI
- Input validation
- Response formatting
- Error handling
- Performance optimization

**Endpoints:**
```
GET  /recommend/user/{user_id}          # Get personalized recommendations
GET  /recommend/similar/{product_id}    # Get similar products
POST /recommend/batch                   # Batch recommendations
GET  /health                            # Health check
```

```python
# Example usage
# Run server
python step5_api_server.py

# Test endpoint
curl http://localhost:8000/recommend/user/42
```

### Step 6: Complete Pipeline (Day 4-5)

**File**: `step6_complete_pipeline.py`

**What You'll Learn:**
- End-to-end workflow orchestration
- Error handling & recovery
- Logging & monitoring
- Production deployment considerations

**Output:**
- Fully trained and deployed system
- Performance dashboard
- Deployment checklist

## 📊 Evaluation Metrics

### Recommendation Quality
- **Precision@K**: % of recommended items that user likes
- **Recall@K**: % of user's liked items that are recommended
- **NDCG@K**: Normalized discounted cumulative gain (ranking quality)
- **Hit Rate@K**: % of users who have at least 1 relevant item in top K

### Business Metrics
- **Click-Through Rate (CTR)**: Recommendations clicked / shown
- **Conversion Rate**: Purchases / clicks
- **Average Order Value**: Revenue per recommendation
- **User Engagement**: Time spent, pages viewed

### Technical Metrics
- **Latency**: API response time (should be < 100ms)
- **Throughput**: Requests per second
- **Model Size**: Memory footprint
- **Training Time**: Time to retrain model

## 🎨 Visual Architecture

**Open `Week3-Recommendation-System.svg`** to see:
- Complete system architecture
- Data flow diagram
- API structure
- Model training pipeline
- Deployment setup

## 🔧 Technologies Used

- **PyTorch**: Neural network framework
- **FastAPI**: Modern web framework for APIs
- **Pandas**: Data manipulation
- **NumPy**: Numerical computing
- **Scikit-learn**: ML utilities
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation

## 💡 Key Concepts

### Collaborative Filtering
Recommend items based on user similarity:
- **User-based**: "Users like you also liked..."
- **Item-based**: "People who liked X also liked Y..."

### Neural Collaborative Filtering
Use neural networks to learn user/item embeddings:
```python
User Embedding (32-dim) + Item Embedding (32-dim)
    → Neural Network → Predicted Rating
```

### Cold Start Problem
Handling new users/items with no history:
- Use content-based features
- Popularity-based fallback
- Hybrid approaches

## 🚨 Common Challenges & Solutions

### Challenge 1: Sparse Data
**Problem**: Most users interact with few items
**Solution**: Matrix factorization, negative sampling

### Challenge 2: Cold Start
**Problem**: New users/products have no history
**Solution**: Content-based features, popularity fallback

### Challenge 3: Scalability
**Problem**: Millions of users × products
**Solution**: Approximate nearest neighbors, caching

### Challenge 4: Diversity
**Problem**: Recommendations too similar
**Solution**: Diversity re-ranking, exploration bonus

## 📈 Expected Results

After training, you should see:
- **Precision@10**: 15-25%
- **Recall@10**: 30-50%
- **NDCG@10**: 0.4-0.6
- **API Latency**: < 50ms

These are realistic production metrics!

## 🎯 Success Criteria

By the end of Week 3, you should be able to:
1. ✅ Explain how collaborative filtering works
2. ✅ Build a complete ML pipeline from scratch
3. ✅ Deploy a model as a REST API
4. ✅ Evaluate recommendation quality properly
5. ✅ Debug and improve model performance
6. ✅ Handle real-world data challenges
7. ✅ Understand production ML considerations

## 🚀 Beyond Week 3

### Further Improvements
- Add real-time learning (online updates)
- Implement A/B testing framework
- Add user feedback loop
- Build recommendation explanation feature
- Add multi-armed bandit for exploration
- Implement context-aware recommendations

### Deployment
- Containerize with Docker
- Deploy to cloud (AWS, GCP, Azure)
- Add load balancing
- Implement caching (Redis)
- Set up monitoring (Prometheus, Grafana)

## 📚 Additional Resources

### Included Documentation
- Architecture diagram (SVG)
- Code with extensive comments
- Sample data with realistic patterns
- API documentation
- Deployment guide

### External Resources (Optional)
- "Recommender Systems Handbook"
- FastAPI documentation
- PyTorch recommendation tutorials
- Production ML best practices

## 🤝 Getting Help

**If you get stuck:**

1. **Check the logs**: All scripts print detailed progress
2. **Verify data**: Run `step1_data_preparation.py` first
3. **Test components**: Each step can run independently
4. **Debug mode**: Set `DEBUG=True` in scripts
5. **API testing**: Use included curl commands

**Common Issues:**
- Missing dependencies: `pip install -r requirements.txt`
- Data not found: Check you're in `week3-real-project/` directory
- Model not training: Check data has enough samples
- API not starting: Check port 8000 is available

## 📝 Project Checklist

- [ ] Set up environment and install dependencies
- [ ] Run data preparation and explore data
- [ ] Create features and understand distributions
- [ ] Train model and monitor convergence
- [ ] Evaluate model on test set (metrics > baseline)
- [ ] Deploy API and test endpoints
- [ ] Run complete pipeline end-to-end
- [ ] Generate recommendations for sample users
- [ ] Measure API latency (< 100ms)
- [ ] Review code and understand all components

## 🎓 Learning Path

**Day 1**: Data preparation & exploration
- Understand the business problem
- Load and clean data
- Basic exploratory analysis

**Day 2**: Feature engineering & model building
- Create meaningful features
- Build recommendation model
- Start training

**Day 3**: Training & evaluation
- Complete model training
- Evaluate performance
- Iterate on improvements

**Day 4**: API & deployment
- Build REST API
- Test endpoints
- Performance optimization

**Day 5**: Integration & polish
- End-to-end testing
- Documentation
- Deployment preparation

## 🔥 Key Takeaway

**You're not just learning ML concepts - you're building a real production system that solves actual business problems.**

This recommendation engine is similar to what Netflix, Amazon, and Spotify use. The principles you learn here apply to any production ML system.

---

**Ready to build your first production ML system?**

**Start with:** `python step1_data_preparation.py`

Let's go! 🚀
