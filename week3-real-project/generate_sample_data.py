"""Generate realistic sample data for the recommendation system"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)

# Products
categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Sports', 'Books', 
              'Toys', 'Beauty', 'Automotive', 'Health', 'Garden']
products = []
for i in range(1, 101):
    products.append({
        'product_id': i,
        'name': f'Product_{i}',
        'category': random.choice(categories),
        'price': round(random.uniform(9.99, 299.99), 2),
        'description': f'High quality {random.choice(categories).lower()} item',
        'stock': random.randint(0, 500),
        'rating_avg': round(random.uniform(3.0, 5.0), 1),
        'num_reviews': random.randint(0, 1000)
    })
df_products = pd.DataFrame(products)
df_products.to_csv('data/products.csv', index=False)
print(f"✓ Created products.csv: {len(products)} products")

# Users  
locations = ['Urban', 'Suburban', 'Rural']
users = []
for i in range(1, 201):
    users.append({
        'user_id': i,
        'age': random.randint(18, 70),
        'gender': random.choice(['M', 'F']),
        'location': random.choice(locations),
        'account_age_days': random.randint(30, 1825),
        'total_purchases': random.randint(0, 50),
        'avg_purchase_value': round(random.uniform(20, 200), 2),
        'preferred_category': random.choice(categories)
    })
df_users = pd.DataFrame(users)
df_users.to_csv('data/users.csv', index=False)
print(f"✓ Created users.csv: {len(users)} users")

# Interactions
interaction_types = ['view', 'click', 'add_to_cart', 'purchase']
interactions = []
start_date = datetime(2024, 1, 1)
for i in range(5000):
    user_id = random.randint(1, 200)
    product_id = random.randint(1, 100)
    interaction_type = random.choice(interaction_types)
    timestamp = start_date + timedelta(days=random.randint(0, 60),
                                       hours=random.randint(0, 23),
                                       minutes=random.randint(0, 59))
    interactions.append({
        'interaction_id': i + 1,
        'user_id': user_id,
        'product_id': product_id,
        'interaction_type': interaction_type,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'session_duration_sec': random.randint(10, 600) if interaction_type != 'view' else random.randint(5, 120),
        'device': random.choice(['mobile', 'desktop', 'tablet'])
    })
df_interactions = pd.DataFrame(interactions)
df_interactions.to_csv('data/interactions.csv', index=False)
print(f"✓ Created interactions.csv: {len(interactions)} interactions")

# Ratings
ratings = []
rated_pairs = set()
for i in range(3000):
    while True:
        user_id = random.randint(1, 200)
        product_id = random.randint(1, 100)
        if (user_id, product_id) not in rated_pairs:
            rated_pairs.add((user_id, product_id))
            break
    rating = round(random.triangular(3.0, 5.0, 4.5), 1)
    timestamp = start_date + timedelta(days=random.randint(0, 60))
    ratings.append({
        'rating_id': i + 1,
        'user_id': user_id,
        'product_id': product_id,
        'rating': rating,
        'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'verified_purchase': random.choice([True, False])
    })
df_ratings = pd.DataFrame(ratings)
df_ratings.to_csv('data/ratings.csv', index=False)
print(f"✓ Created ratings.csv: {len(ratings)} ratings")

print(f"\n✅ All sample data generated successfully!")
print(f"\nData summary:")
print(f"  Products: {len(products)} items across {len(set([p['category'] for p in products]))} categories")
print(f"  Users: {len(users)} users")
print(f"  Interactions: {len(interactions)} events ({len(df_interactions[df_interactions['interaction_type']=='purchase'])} purchases)")
print(f"  Ratings: {len(ratings)} ratings (avg: {df_ratings['rating'].mean():.2f})")
