"""
Day 1: From Arrays to PyTorch Tensors
A hands-on introduction for programmers

This demonstrates:
1. How tensors are like multi-dimensional arrays but more powerful
2. Basic tensor operations
3. Real-world sales data analysis example
"""

import torch
import numpy as np

def basic_tensors():
    """
    Introduction to tensors - think of them as arrays on steroids
    """
    print("="*60)
    print("PART 1: Creating and Using Tensors")
    print("="*60)

    # Creating a 1D tensor (like a simple array/list)
    daily_sales = torch.tensor([120, 135, 98, 156, 189, 210, 145])
    print(f"Daily sales (units): {daily_sales}")
    print(f"Data type: {daily_sales.dtype}")
    print(f"Shape: {daily_sales.shape}")  # How many elements
    print(f"Device: {daily_sales.device}")  # cpu or cuda (GPU)

    # Basic operations (no loops needed!)
    avg_sales = daily_sales.float().mean()
    total_sales = daily_sales.sum()
    max_sales = daily_sales.max()

    print(f"\nWeekly Statistics:")
    print(f"  Average daily sales: {avg_sales:.2f} units")
    print(f"  Total weekly sales: {total_sales} units")
    print(f"  Best day: {max_sales} units")

    # Finding specific values (boolean indexing - powerful!)
    above_avg = daily_sales[daily_sales > avg_sales]
    print(f"\nDays above average: {above_avg}")
    print(f"Number of above-average days: {len(above_avg)}")
    print()


def multidimensional_tensors():
    """
    2D and 3D tensors - working with tables and cubes of data
    """
    print("="*60)
    print("PART 2: Multi-dimensional Tensors")
    print("="*60)

    # 2D tensor: Sales data for 4 products over 7 days
    # Rows = Products, Columns = Days (Mon-Sun)
    sales_data = torch.tensor([
        [45, 52, 38, 61, 73, 89, 67],   # Product A
        [32, 28, 35, 42, 48, 55, 41],   # Product B
        [78, 82, 71, 88, 95, 102, 86],  # Product C
        [12, 15, 11, 18, 22, 28, 19]    # Product D
    ])

    print(f"Sales data shape: {sales_data.shape}")
    print(f"(4 products × 7 days)\n")
    print("Sales matrix:")
    print(sales_data)
    print()

    # Aggregate operations
    total_by_product = sales_data.sum(dim=1)  # Sum across days
    total_by_day = sales_data.sum(dim=0)      # Sum across products

    products = ['Product A', 'Product B', 'Product C', 'Product D']
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    print("Total sales by product:")
    for product, total in zip(products, total_by_product):
        print(f"  {product}: {total} units")

    print("\nTotal sales by day:")
    for day, total in zip(days, total_by_day):
        print(f"  {day}: {total} units")

    # Find best performing product
    best_product_idx = total_by_product.argmax()
    print(f"\nBest performing product: {products[best_product_idx]} ({total_by_product[best_product_idx]} units)")

    # Weekend analysis
    weekend_sales = sales_data[:, 5:7]  # Slicing: all products, Sat-Sun only
    weekend_total = weekend_sales.sum()
    weekday_total = sales_data[:, 0:5].sum()

    print(f"\nWeekend vs Weekday:")
    print(f"  Weekend total: {weekend_total} units")
    print(f"  Weekday total: {weekday_total} units")
    print(f"  Weekend is {weekend_total / weekday_total * 100:.1f}% of weekday sales")
    print()


def real_world_analysis():
    """
    Practical example: Analyzing e-commerce sales patterns
    """
    print("="*60)
    print("PART 3: Real-World E-Commerce Analysis")
    print("="*60)

    # Simulate hourly sales data for a week (24 hours × 7 days)
    # This is what you might get from your database/API
    np.random.seed(42)  # For reproducible results

    # Create realistic hourly sales pattern
    hours = 24
    days = 7
    hourly_sales = torch.zeros(hours, days)

    for day in range(days):
        for hour in range(hours):
            # Business logic: Sales peak during day hours (9-21)
            if 9 <= hour <= 21:
                base_sales = 50 + np.random.randint(-10, 20)
            else:
                base_sales = 10 + np.random.randint(-5, 10)

            # Weekend boost
            if day >= 5:  # Saturday, Sunday
                base_sales = int(base_sales * 1.3)

            hourly_sales[hour, day] = base_sales

    print(f"Hourly sales data shape: {hourly_sales.shape}")
    print(f"Total sales this week: ${hourly_sales.sum():.0f}\n")

    # Analysis 1: Find peak hours
    avg_by_hour = hourly_sales.mean(dim=1)  # Average across days
    peak_hour = avg_by_hour.argmax()

    print(f"Analysis: Peak Sales Hours")
    print(f"  Peak hour: {peak_hour}:00 (${avg_by_hour[peak_hour]:.2f} avg)")

    # Find all hours above 50% of peak
    threshold = avg_by_hour[peak_hour] * 0.5
    high_sales_hours = torch.where(avg_by_hour > threshold)[0]
    print(f"  High-traffic hours (>{threshold:.0f} avg): {high_sales_hours.tolist()}")

    # Analysis 2: Day of week patterns
    total_by_day = hourly_sales.sum(dim=0)
    days_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    print(f"\nAnalysis: Daily Revenue")
    for i, (day, total) in enumerate(zip(days_names, total_by_day)):
        bar = '█' * int(total / 50)
        print(f"  {day}: ${total:6.0f} {bar}")

    # Analysis 3: Weekend vs Weekday comparison
    weekday_avg = hourly_sales[:, 0:5].mean()
    weekend_avg = hourly_sales[:, 5:7].mean()

    print(f"\nAnalysis: Weekend Impact")
    print(f"  Weekday average: ${weekday_avg:.2f}/hour")
    print(f"  Weekend average: ${weekend_avg:.2f}/hour")
    print(f"  Weekend lift: {((weekend_avg / weekday_avg - 1) * 100):.1f}%")

    # Analysis 4: Identify unusual patterns
    # Hours with very low sales during typically busy times
    busy_hours = torch.arange(9, 22)  # 9 AM to 9 PM
    low_sales_threshold = 30

    print(f"\nAnalysis: Anomaly Detection")
    for day_idx, day_name in enumerate(days_names):
        day_sales = hourly_sales[busy_hours, day_idx]
        low_hours = busy_hours[day_sales < low_sales_threshold]
        if len(low_hours) > 0:
            print(f"  ⚠️  {day_name}: Unusually low sales at hours {low_hours.tolist()}")

    print()


def tensor_operations_cheatsheet():
    """
    Quick reference for common tensor operations
    """
    print("="*60)
    print("PART 4: Tensor Operations Cheat Sheet")
    print("="*60)

    # Create sample data
    prices = torch.tensor([29.99, 49.99, 19.99, 89.99, 34.99])
    quantities = torch.tensor([3, 1, 5, 2, 4])

    print("Sample Data:")
    print(f"  Prices: {prices}")
    print(f"  Quantities: {quantities}")

    # Element-wise operations
    print(f"\nBasic Operations:")
    print(f"  Total cost per item: {prices * quantities}")
    print(f"  Grand total: ${(prices * quantities).sum():.2f}")
    print(f"  Average price: ${prices.mean():.2f}")

    # Reductions
    print(f"\nReductions (aggregate operations):")
    print(f"  sum: {quantities.sum()}")
    print(f"  mean: {prices.mean():.2f}")
    print(f"  max: {prices.max():.2f}")
    print(f"  min: {prices.min():.2f}")

    # Reshaping
    print(f"\nReshaping:")
    matrix = prices.reshape(5, 1)  # Convert to column vector
    print(f"  Original shape: {prices.shape}")
    print(f"  Reshaped to column: {matrix.shape}")

    # Slicing (0-indexed)
    print(f"\nSlicing:")
    print(f"  First item: ${prices[0]:.2f}")
    print(f"  Items 1-3: ${prices[1:4]}")
    print(f"  Last item: ${prices[-1]:.2f}")

    # Boolean indexing (super powerful!)
    print(f"\nBoolean Indexing:")
    expensive = prices > 40
    print(f"  Prices > $40: {expensive}")
    print(f"  Expensive items: ${prices[expensive]}")
    print(f"  Number of expensive items: {expensive.sum()}")

    # Combining conditions
    mid_range = (prices > 20) & (prices < 50)
    print(f"  Mid-range items ($20-$50): ${prices[mid_range]}")

    print()


def performance_comparison():
    """
    Show why tensors are faster than loops
    """
    print("="*60)
    print("PART 5: Performance - Why Use Tensors?")
    print("="*60)

    import time

    # Large dataset
    size = 1000000
    data = torch.randn(size)

    # Tensor operation (vectorized)
    start = time.time()
    result_tensor = (data * 2 + 5).sum()
    tensor_time = time.time() - start

    # Python loop (on smaller data)
    small_data = data[:10000].tolist()
    start = time.time()
    result_loop = sum([x * 2 + 5 for x in small_data])
    loop_time = time.time() - start

    # Extrapolate to full size
    extrapolated_loop_time = loop_time * (size / 10000)

    print(f"Processing {size:,} numbers:")
    print(f"  Tensor operation: {tensor_time*1000:.2f} ms")
    print(f"  Python loop (extrapolated): {extrapolated_loop_time*1000:.2f} ms")
    print(f"  Speedup: {extrapolated_loop_time/tensor_time:.0f}x faster!")

    print(f"\n  💡 This is on CPU. On GPU, it can be 100-1000x faster!")
    print(f"  💡 This is why AI/ML uses tensors - they scale!")
    print()


def main():
    """
    Run all demonstrations
    """
    print("\n")
    print("🚀 " + "="*56 + " 🚀")
    print("   Welcome to PyTorch Tensors for Programmers!")
    print("🚀 " + "="*56 + " 🚀")
    print()

    basic_tensors()
    multidimensional_tensors()
    real_world_analysis()
    tensor_operations_cheatsheet()
    performance_comparison()

    print("="*60)
    print("✅ Day 1 Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("  1. Tensors are multi-dimensional arrays that run on GPUs")
    print("  2. No loops needed - vectorized operations are 10-100x faster")
    print("  3. Perfect for analyzing large datasets (sales, logs, metrics)")
    print("  4. Boolean indexing lets you filter data instantly")
    print("\nNext Steps:")
    print("  • Try modifying the sales data with your own numbers")
    print("  • Experiment with different analyses")
    print("  • Run: python day2_movie_ratings.py")
    print()


if __name__ == "__main__":
    # Check if PyTorch is installed
    try:
        import torch
        print(f"✅ PyTorch {torch.__version__} detected")
        main()
    except ImportError:
        print("❌ PyTorch not installed!")
        print("\nInstall with: pip install torch")
        print("Or: pip3 install torch")
