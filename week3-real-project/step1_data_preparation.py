"""
Step 1: Data Preparation
Load and prepare all data for the recommendation system
"""
import pandas as pd
import numpy as np

print("="*70)
print("STEP 1: DATA PREPARATION")
print("="*70)
print("\nLoading all datasets...\n")

# Note: Sample data files should be in data/ directory
# Run this from week3-real-project/ directory

print("Sample code - demonstrates data loading pattern:")
print("""
# Load products
products = pd.read_csv('data/products.csv')
print(f"Products: {len(products)} items")

# Load users  
users = pd.read_csv('data/users.csv')
print(f"Users: {len(users)} users")

# Load interactions
interactions = pd.read_csv('data/interactions.csv') 
print(f"Interactions: {len(interactions)} events")

# Load ratings
ratings = pd.read_csv('data/ratings.csv')
print(f"Ratings: {len(ratings)} ratings")

# Data quality checks
print("\\nData Quality:")
print(f"  Missing values: {ratings.isnull().sum().sum()}")
print(f"  Duplicate ratings: {ratings.duplicated().sum()}")
print(f"  Rating range: {ratings['rating'].min():.1f} - {ratings['rating'].max():.1f}")

# Merge datasets
user_item_matrix = ratings.pivot(index='user_id', columns='product_id', values='rating')
print(f"\\nUser-Item Matrix: {user_item_matrix.shape}")
print(f"Sparsity: {(1 - user_item_matrix.notna().sum().sum() / user_item_matrix.size) * 100:.1f}%")
""")

print("\n✅ Data preparation template ready")
print("Add your CSV files to data/ directory and uncomment the code above")
