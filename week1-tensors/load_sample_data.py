"""
Helper script to load sample CSV data into tensors

This shows how to load real data from files into PyTorch tensors
"""

import torch
import csv


def load_sales_data(filename='sample_sales_data.csv'):
    """
    Load sales data from CSV into a tensor

    Returns:
        products: List of product names
        days: List of day names
        data_tensor: Tensor of shape [num_products, num_days]
    """
    print(f"Loading sales data from {filename}...")

    # Read CSV file
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Extract unique products and days
    products = []
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

    # Count unique products
    product_set = set()
    for row in data:
        product_set.add(row['product'])
    products = sorted(list(product_set))

    # Create tensor
    num_products = len(products)
    num_days = len(days_order)
    sales_tensor = torch.zeros(num_products, num_days)

    # Fill tensor
    for row in data:
        product_idx = products.index(row['product'])
        day_idx = days_order.index(row['day'])
        units = int(row['units_sold'])
        sales_tensor[product_idx, day_idx] = units

    print(f"✓ Loaded {num_products} products × {num_days} days")
    print(f"✓ Total units: {sales_tensor.sum():.0f}\n")

    return products, days_order, sales_tensor


def load_movie_data(filename='sample_movie_ratings.csv'):
    """
    Load movie ratings from CSV into a tensor

    Returns:
        movies_info: List of dictionaries with movie metadata
        data_tensor: Tensor of shape [num_movies, num_features]
                     Features: [rating, num_reviews, genre_id, year, runtime]
    """
    print(f"Loading movie data from {filename}...")

    # Read CSV file
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    # Genre mapping
    genre_to_id = {
        'Action': 0,
        'Comedy': 1,
        'Drama': 2,
        'Sci-Fi': 3,
        'Horror': 4
    }

    # Create feature tensor
    num_movies = len(data)
    num_features = 5  # rating, num_reviews, genre_id, year, runtime
    movies_tensor = torch.zeros(num_movies, num_features)

    # Store movie info
    movies_info = []

    for i, row in enumerate(data):
        # Extract features
        rating = float(row['rating'])
        num_reviews = int(row['num_reviews'])
        genre_id = genre_to_id.get(row['genre'], 0)
        year = int(row['year'])
        runtime = int(row['runtime_minutes'])

        # Fill tensor
        movies_tensor[i] = torch.tensor([rating, num_reviews, genre_id, year, runtime])

        # Store metadata
        movies_info.append({
            'id': int(row['movie_id']),
            'title': row['title'],
            'genre': row['genre'],
            'year': year,
            'runtime': runtime,
            'rating': rating,
            'num_reviews': num_reviews
        })

    print(f"✓ Loaded {num_movies} movies")
    print(f"✓ Average rating: {movies_tensor[:, 0].mean():.2f}")
    print(f"✓ Total reviews: {movies_tensor[:, 1].sum():.0f}\n")

    return movies_info, movies_tensor, genre_to_id


def demo_sales_analysis():
    """
    Demonstrate loading and analyzing sales data
    """
    print("="*60)
    print("DEMO: Sales Data Analysis")
    print("="*60)
    print()

    # Load data
    products, days, sales_data = load_sales_data()

    # Analysis
    print("Quick Analysis:")
    print(f"  Best selling product: {products[sales_data.sum(dim=1).argmax()]}")
    print(f"  Best day for sales: {days[sales_data.sum(dim=0).argmax()]}")

    # Weekend vs weekday
    weekend_sales = sales_data[:, 5:7].sum()
    weekday_sales = sales_data[:, 0:5].sum()
    print(f"  Weekend sales: {weekend_sales:.0f} units")
    print(f"  Weekday sales: {weekday_sales:.0f} units")
    print()


def demo_movie_analysis():
    """
    Demonstrate loading and analyzing movie data
    """
    print("="*60)
    print("DEMO: Movie Ratings Analysis")
    print("="*60)
    print()

    # Load data
    movies_info, movies_data, genre_map = load_movie_data()

    # Analysis
    ratings = movies_data[:, 0]
    num_reviews = movies_data[:, 1]

    print("Quick Analysis:")
    best_idx = ratings.argmax()
    print(f"  Highest rated: {movies_info[best_idx]['title']} ({ratings[best_idx]:.1f}/5.0)")

    most_reviewed_idx = num_reviews.argmax()
    print(f"  Most reviewed: {movies_info[most_reviewed_idx]['title']} ({num_reviews[most_reviewed_idx]:.0f} reviews)")

    # Genre stats
    print(f"\n  Movies by genre:")
    for genre, genre_id in sorted(genre_map.items(), key=lambda x: x[1]):
        genre_mask = movies_data[:, 2] == genre_id
        count = genre_mask.sum()
        if count > 0:
            avg_rating = ratings[genre_mask].mean()
            print(f"    {genre}: {count} movies (avg rating: {avg_rating:.2f})")

    print()


if __name__ == "__main__":
    print("\n")
    print("📂 Sample Data Loader")
    print("="*60)
    print()

    try:
        # Demo both datasets
        demo_sales_analysis()
        demo_movie_analysis()

        print("="*60)
        print("✅ Data loading successful!")
        print("="*60)
        print("\nYou can use these functions in your own code:")
        print("  from load_sample_data import load_sales_data, load_movie_data")
        print("\nOr create your own CSV files and modify the loader functions!")
        print()

    except FileNotFoundError as e:
        print(f"❌ Error: Could not find data file")
        print(f"   Make sure you're running this from the week1-tensors directory")
        print(f"   {e}")
    except Exception as e:
        print(f"❌ Error loading data: {e}")
