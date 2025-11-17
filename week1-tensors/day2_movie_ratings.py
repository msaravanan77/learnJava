"""
Day 2: Tensor Operations - Movie Ratings Analysis
Real-world application using tensor operations

This demonstrates:
1. Working with structured data in tensors
2. Vectorized calculations (no loops!)
3. Building a practical recommendation system
"""

import torch
import numpy as np


class MovieAnalyzer:
    """
    Analyze movie ratings using tensor operations
    Much faster than analyzing ratings one-by-one
    """

    def __init__(self):
        self.genres = ['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror']
        self.min_rating = 1.0
        self.max_rating = 5.0

    def generate_sample_data(self, num_movies=50):
        """
        Generate sample movie ratings data
        In real world, this would come from your database
        """
        np.random.seed(42)

        # Each movie has: [rating, num_reviews, genre_id, year, runtime_minutes]
        movies = []
        for i in range(num_movies):
            rating = np.random.uniform(2.5, 5.0)
            num_reviews = np.random.randint(10, 5000)
            genre_id = np.random.randint(0, len(self.genres))
            year = np.random.randint(1990, 2024)
            runtime = np.random.randint(80, 180)

            movies.append([rating, num_reviews, genre_id, year, runtime])

        return torch.tensor(movies, dtype=torch.float32)

    def analyze_batch(self, movies_tensor):
        """
        Analyze multiple movies at once using tensors

        Input tensor shape: [num_movies, 5 features]
        Features: [rating, num_reviews, genre_id, year, runtime]
        """
        print(f"Analyzing {len(movies_tensor)} movies...")
        print(f"Feature tensor shape: {movies_tensor.shape}\n")

        # Extract features (like accessing columns in a table)
        ratings = movies_tensor[:, 0]
        num_reviews = movies_tensor[:, 1]
        genre_ids = movies_tensor[:, 2]
        years = movies_tensor[:, 3]
        runtimes = movies_tensor[:, 4]

        # Calculate popularity scores using vectorized operations
        scores = self._calculate_popularity_scores(movies_tensor)

        # Find recommendations
        recommendations = self._find_recommendations(movies_tensor, scores)

        return ratings, num_reviews, genre_ids, years, runtimes, scores, recommendations

    def _calculate_popularity_scores(self, movies_tensor):
        """
        Calculate popularity scores using tensor operations (NO LOOPS!)

        Score = rating_score + review_score + recency_score
        """
        ratings = movies_tensor[:, 0]
        num_reviews = movies_tensor[:, 1]
        years = movies_tensor[:, 3]

        # Rating score: normalize to 0-100 scale
        rating_score = (ratings / 5.0) * 50

        # Review score: more reviews = more popular (log scale to prevent dominance)
        review_score = torch.log10(num_reviews + 1) * 10

        # Recency score: newer movies get a boost
        current_year = 2024
        years_old = current_year - years
        recency_score = torch.clamp(20 - years_old, min=0, max=20)

        # Total score
        total_score = rating_score + review_score + recency_score

        return total_score

    def _find_recommendations(self, movies_tensor, scores):
        """
        Find top movies to recommend based on scores
        """
        # Get indices of top 10 movies
        top_indices = torch.argsort(scores, descending=True)[:10]
        return top_indices

    def print_report(self, movies_tensor, ratings, num_reviews, genre_ids, years, runtimes, scores, recommendations):
        """
        Print comprehensive analysis report
        """
        print("="*80)
        print(" "*25 + "MOVIE RATINGS ANALYSIS REPORT")
        print("="*80)
        print()

        # Overall statistics
        print("OVERALL STATISTICS")
        print("-" * 80)
        print(f"Total movies analyzed: {len(movies_tensor)}")
        print(f"Average rating: {ratings.mean():.2f} / 5.0")
        print(f"Median rating: {ratings.median():.2f}")
        print(f"Highest rated: {ratings.max():.2f}")
        print(f"Lowest rated: {ratings.min():.2f}")
        print(f"Total reviews: {num_reviews.sum():.0f}")
        print(f"Average reviews per movie: {num_reviews.mean():.0f}")
        print()

        # Genre analysis
        print("GENRE ANALYSIS")
        print("-" * 80)
        for genre_id, genre_name in enumerate(self.genres):
            # Boolean indexing to filter by genre
            genre_mask = genre_ids == genre_id
            genre_movies = movies_tensor[genre_mask]

            if len(genre_movies) > 0:
                genre_ratings = genre_movies[:, 0]
                genre_reviews = genre_movies[:, 1]

                print(f"{genre_name:10s}: {len(genre_movies):2d} movies | "
                      f"Avg rating: {genre_ratings.mean():.2f} | "
                      f"Total reviews: {genre_reviews.sum():.0f}")
        print()

        # Year analysis
        print("DECADE ANALYSIS")
        print("-" * 80)
        decades = [(1990, 1999), (2000, 2009), (2010, 2019), (2020, 2024)]
        for start, end in decades:
            decade_mask = (years >= start) & (years <= end)
            decade_movies = movies_tensor[decade_mask]

            if len(decade_movies) > 0:
                decade_ratings = decade_movies[:, 0]
                print(f"{start}s: {len(decade_movies):2d} movies | "
                      f"Avg rating: {decade_ratings.mean():.2f}")
        print()

        # Runtime analysis
        print("RUNTIME ANALYSIS")
        print("-" * 80)
        short_mask = runtimes < 90
        medium_mask = (runtimes >= 90) & (runtimes < 120)
        long_mask = runtimes >= 120

        for mask, label in [(short_mask, "Short (<90 min)"),
                            (medium_mask, "Medium (90-120 min)"),
                            (long_mask, "Long (120+ min)")]:
            runtime_movies = movies_tensor[mask]
            if len(runtime_movies) > 0:
                runtime_ratings = runtime_movies[:, 0]
                print(f"{label:20s}: {len(runtime_movies):2d} movies | "
                      f"Avg rating: {runtime_ratings.mean():.2f}")
        print()

        # Top recommendations
        print("TOP 10 RECOMMENDED MOVIES")
        print("-" * 80)
        print(f"{'#':<3} {'Rating':<8} {'Reviews':<10} {'Genre':<10} {'Year':<6} {'Score':<8}")
        print("-" * 80)

        for i, idx in enumerate(recommendations):
            movie = movies_tensor[idx]
            rating = movie[0].item()
            reviews = int(movie[1].item())
            genre = self.genres[int(movie[2].item())]
            year = int(movie[3].item())
            score = scores[idx].item()

            print(f"{i+1:<3} {rating:<8.2f} {reviews:<10d} {genre:<10s} {year:<6d} {score:<8.2f}")
        print()

        # Statistical insights
        print("INSIGHTS")
        print("-" * 80)

        # High rated but underreviewed
        high_rating_mask = ratings > 4.5
        low_review_mask = num_reviews < 100
        hidden_gems = high_rating_mask & low_review_mask

        if hidden_gems.sum() > 0:
            print(f"🌟 Found {hidden_gems.sum()} hidden gems:")
            print(f"   High ratings (>4.5) but fewer than 100 reviews")

        # Popular but lower rated
        high_review_mask = num_reviews > 1000
        medium_rating_mask = (ratings >= 3.0) & (ratings < 4.0)
        overrated = high_review_mask & medium_rating_mask

        if overrated.sum() > 0:
            print(f"📊 Found {overrated.sum()} potentially overrated movies:")
            print(f"   Many reviews (>1000) but mediocre ratings (3.0-4.0)")

        # Best genre by rating
        best_genre_id = 0
        best_avg_rating = 0
        for genre_id in range(len(self.genres)):
            genre_mask = genre_ids == genre_id
            if genre_mask.sum() > 0:
                avg = ratings[genre_mask].mean()
                if avg > best_avg_rating:
                    best_avg_rating = avg
                    best_genre_id = genre_id

        print(f"🏆 Best genre by rating: {self.genres[best_genre_id]} ({best_avg_rating:.2f})")

        print()


def demonstrate_tensor_operations():
    """
    Show how tensor operations work with movie data
    """
    print("="*80)
    print(" "*20 + "TENSOR OPERATIONS DEMONSTRATION")
    print("="*80)
    print()

    # Create sample ratings matrix: 5 movies × 3 users
    ratings = torch.tensor([
        [5.0, 4.0, 5.0],  # Movie 1: Action movie
        [3.0, 3.5, 4.0],  # Movie 2: Comedy
        [4.5, 5.0, 4.5],  # Movie 3: Drama
        [2.0, 2.5, 3.0],  # Movie 4: Horror
        [4.0, 4.5, 4.0],  # Movie 5: Sci-Fi
    ])

    print("Rating matrix (movies × users):")
    print(ratings)
    print(f"Shape: {ratings.shape}\n")

    # Average rating per movie
    avg_per_movie = ratings.mean(dim=1)
    print(f"Average rating per movie: {avg_per_movie}")

    # Average rating per user
    avg_per_user = ratings.mean(dim=0)
    print(f"Average rating per user: {avg_per_user}")

    # Find movies rated above 4.0 by all users
    all_liked = (ratings > 4.0).all(dim=1)
    print(f"\nMovies liked by everyone (>4.0): {torch.where(all_liked)[0].tolist()}")

    # Find users who are generous raters
    generous_users = avg_per_user > 4.0
    print(f"Generous raters (avg >4.0): {torch.where(generous_users)[0].tolist()}")

    # Similarity between users (cosine similarity)
    # Normalize ratings
    user1 = ratings[:, 0]
    user2 = ratings[:, 1]

    similarity = torch.nn.functional.cosine_similarity(
        user1.unsqueeze(0),
        user2.unsqueeze(0)
    )
    print(f"\nSimilarity between User 1 and User 2: {similarity.item():.3f}")
    print("(1.0 = identical taste, 0.0 = no correlation, -1.0 = opposite)")

    print()


def main():
    """
    Main demonstration
    """
    print("\n")
    print("🎬 " + "="*74 + " 🎬")
    print("   Movie Ratings Analyzer - Tensor Operations in Action")
    print("🎬 " + "="*74 + " 🎬")
    print()

    # Demonstrate tensor operations
    demonstrate_tensor_operations()

    # Create analyzer and generate data
    analyzer = MovieAnalyzer()
    movies = analyzer.generate_sample_data(num_movies=50)

    # Analyze movies
    ratings, num_reviews, genre_ids, years, runtimes, scores, recommendations = \
        analyzer.analyze_batch(movies)

    # Print comprehensive report
    analyzer.print_report(movies, ratings, num_reviews, genre_ids, years,
                         runtimes, scores, recommendations)

    # Real-world application
    print("="*80)
    print(" "*25 + "REAL-WORLD APPLICATIONS")
    print("="*80)
    print()
    print("How to use this in production:")
    print()
    print("1. DATA COLLECTION")
    print("   • Load ratings from your database (PostgreSQL, MongoDB, etc.)")
    print("   • Convert to tensors for fast processing")
    print()
    print("2. BATCH PROCESSING")
    print("   • Analyze millions of ratings in seconds")
    print("   • Update recommendations in real-time")
    print("   • No loops needed - everything is vectorized")
    print()
    print("3. RECOMMENDATION ENGINE")
    print("   • Calculate similarity between users")
    print("   • Find similar movies using embeddings (Week 4!)")
    print("   • Personalize recommendations")
    print()
    print("4. A/B TESTING")
    print("   • Compare different recommendation algorithms")
    print("   • Measure which generates more engagement")
    print("   • All calculations done with tensors")
    print()
    print("Performance benefits:")
    print("  • Traditional: Process one rating at a time → Slow")
    print("  • Tensor approach: Process 1M ratings simultaneously → Fast!")
    print("  • Speedup: 10-100x on CPU, 100-1000x on GPU")
    print()

    print("="*80)
    print("✅ Day 2 Complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Tensors enable batch processing (analyze many items at once)")
    print("  2. Vectorized operations replace loops - much faster")
    print("  3. Boolean indexing enables powerful filtering")
    print("  4. Real recommendation systems use these exact techniques!")
    print("\nNext Steps:")
    print("  • Try loading your own data (CSV file with ratings)")
    print("  • Experiment with different scoring formulas")
    print("  • Build your own recommendation algorithm")
    print("  • Next: Week 2 - Neural Networks (where the real magic happens!)")
    print()


if __name__ == "__main__":
    try:
        import torch
        main()
    except ImportError:
        print("❌ PyTorch not installed!")
        print("\nInstall with: pip install torch")
