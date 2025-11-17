"""
Day 1: From C Arrays to PyTorch Tensors
A hands-on introduction for C programmers

This demonstrates:
1. How tensors are like C arrays but more powerful
2. Basic tensor operations
3. Real-world security log analysis example
"""

import torch
import numpy as np

def c_style_thinking():
    """
    Compare C-style programming with PyTorch tensors
    """
    print("="*60)
    print("PART 1: C Arrays vs PyTorch Tensors")
    print("="*60)

    # In C, you would write:
    # int temperatures[7] = {72, 75, 68, 70, 73, 71, 69};

    # In PyTorch:
    temperatures = torch.tensor([72, 75, 68, 70, 73, 71, 69])
    print(f"Temperatures tensor: {temperatures}")
    print(f"Type: {temperatures.dtype}")
    print(f"Shape: {temperatures.shape}")  # Like sizeof, but smarter
    print(f"Device: {temperatures.device}")  # cpu or cuda (GPU)

    # In C: Calculate average with a loop
    # float sum = 0;
    # for(int i = 0; i < 7; i++) { sum += temperatures[i]; }
    # float avg = sum / 7;

    # In PyTorch: No loop needed!
    avg = temperatures.float().mean()
    print(f"\nAverage temperature: {avg:.2f}°F")

    # Find values above average (in C: another loop!)
    above_avg = temperatures[temperatures > avg]
    print(f"Days above average: {above_avg}")
    print()


def multidimensional_arrays():
    """
    2D and 3D tensors - like C arrays but easier to work with
    """
    print("="*60)
    print("PART 2: Multi-dimensional Tensors")
    print("="*60)

    # In C: int login_attempts[24][7];  // hours x days
    # In PyTorch:
    login_attempts = torch.randint(0, 20, (24, 7))  # Random data for demo

    print(f"Login attempts (24 hours x 7 days):\n{login_attempts}\n")
    print(f"Shape: {login_attempts.shape}")

    # Aggregate data (in C: nested loops!)
    total_by_hour = login_attempts.sum(dim=1)  # Sum across days
    total_by_day = login_attempts.sum(dim=0)   # Sum across hours

    print(f"\nTotal logins by hour (24 values): {total_by_hour}")
    print(f"Total logins by day (7 values): {total_by_day}")

    # Find suspicious hours (>100 total attempts)
    suspicious_hours = torch.where(total_by_hour > 100)[0]
    if len(suspicious_hours) > 0:
        print(f"\nSuspicious hours detected: {suspicious_hours.tolist()}")
    else:
        print(f"\nNo suspicious hours detected (threshold: 100)")
    print()


def real_world_security_analysis():
    """
    Practical example: Analyze failed login patterns
    This is something you'd actually use in PAM systems
    """
    print("="*60)
    print("PART 3: Real-World Security Log Analysis")
    print("="*60)

    # Simulate failed login data: [hour][day]
    # In a real system, you'd load this from logs
    failed_logins = torch.tensor([
        # Mon, Tue, Wed, Thu, Fri, Sat, Sun
        [  5,   3,   2,   1,   2,   8,  12],  # 00:00 - midnight
        [  2,   1,   1,   0,   1,   3,   5],  # 01:00
        [  1,   0,   0,   1,   0,   2,   4],  # 02:00 - suspicious hour
        [  0,   1,   0,   0,   1,   5,   8],  # 03:00 - suspicious hour
        [  1,   0,   1,   0,   0,   3,   6],  # 04:00
        [  2,   1,   2,   1,   2,   4,   5],  # 05:00
        [  5,   4,   6,   5,   7,   3,   2],  # 06:00 - business hours start
        [ 10,  12,  11,  13,  14,   5,   3],  # 07:00
        [ 15,  18,  16,  17,  19,   8,   4],  # 08:00
        [ 20,  22,  21,  23,  24,  10,   6],  # 09:00
        [ 12,  14,  13,  15,  16,   8,   5],  # 10:00
        [  8,   9,   8,  10,  11,   6,   4],  # 11:00
        [  6,   7,   6,   8,   9,   5,   3],  # 12:00
        [  7,   8,   7,   9,  10,   6,   4],  # 13:00
        [  9,  10,   9,  11,  12,   7,   5],  # 14:00
        [ 11,  12,  11,  13,  14,   8,   6],  # 15:00
        [ 13,  14,  13,  15,  16,   9,   7],  # 16:00
        [ 10,  11,  10,  12,  13,   8,   6],  # 17:00
        [  8,   9,   8,  10,  11,   7,   5],  # 18:00
        [  6,   7,   6,   8,   9,   6,   4],  # 19:00
        [  5,   6,   5,   7,   8,   5,   3],  # 20:00
        [  4,   5,   4,   6,   7,   4,   2],  # 21:00
        [  3,   4,   3,   5,   6,   6,   8],  # 22:00
        [  4,   5,   4,   6,   7,  10,  15],  # 23:00
    ])

    print(f"Failed login data shape: {failed_logins.shape}")
    print(f"Total failed logins this week: {failed_logins.sum()}\n")

    # Analysis 1: Find suspicious hours (high average failures)
    avg_by_hour = failed_logins.float().mean(dim=1)
    overall_avg = avg_by_hour.mean()

    suspicious_hours = torch.where(avg_by_hour < overall_avg * 0.3)[0]
    print(f"Overall average failures per hour: {overall_avg:.2f}")
    print(f"Low-activity hours (potential bot attacks): {suspicious_hours.tolist()}")

    # Analysis 2: Find anomalous days
    total_by_day = failed_logins.sum(dim=0)
    day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    print(f"\nFailed logins by day:")
    for i, (day, total) in enumerate(zip(day_names, total_by_day)):
        status = "🚨 HIGH" if total > 200 else "✅ Normal"
        print(f"  {day}: {total:3d} {status}")

    # Analysis 3: Weekend pattern detection
    weekday_avg = failed_logins[:, 0:5].float().mean()  # Mon-Fri
    weekend_avg = failed_logins[:, 5:7].float().mean()  # Sat-Sun

    print(f"\nPattern Analysis:")
    print(f"  Weekday average: {weekday_avg:.2f}")
    print(f"  Weekend average: {weekend_avg:.2f}")

    if weekend_avg > weekday_avg * 1.5:
        print("  ⚠️  WARNING: Suspicious weekend activity detected!")
        print("      Recommendation: Review weekend access policies")

    # Analysis 4: Find specific suspicious time windows
    # Late night on weekends
    late_night_weekend = failed_logins[0:6, 5:7]  # Midnight-6AM, Sat-Sun
    if late_night_weekend.sum() > 50:
        print(f"\n  🚨 ALERT: High late-night weekend activity: {late_night_weekend.sum()} failures")
        print(f"      This is {late_night_weekend.sum() / failed_logins.sum() * 100:.1f}% of all failures")

    print()


def tensor_operations_cheatsheet():
    """
    Quick reference for common tensor operations
    """
    print("="*60)
    print("PART 4: Tensor Operations Cheat Sheet")
    print("="*60)

    # Create tensors
    a = torch.tensor([1, 2, 3, 4, 5])
    b = torch.tensor([10, 20, 30, 40, 50])

    print("Basic Operations:")
    print(f"  a = {a}")
    print(f"  b = {b}")
    print(f"  a + b = {a + b}")
    print(f"  a * b = {a * b} (element-wise)")
    print(f"  a * 2 = {a * 2} (scalar multiply)")

    # Reductions
    print(f"\nReductions:")
    print(f"  sum: {a.sum()}")
    print(f"  mean: {a.float().mean():.2f}")
    print(f"  max: {a.max()}")
    print(f"  min: {a.min()}")

    # Reshaping
    print(f"\nReshaping:")
    matrix = a.reshape(5, 1)
    print(f"  Original shape: {a.shape}")
    print(f"  Reshaped to column: {matrix.shape}")
    print(f"  {matrix.T}")  # Transpose

    # Slicing (like C arrays)
    print(f"\nSlicing (0-indexed like C):")
    print(f"  a[0] = {a[0]}")
    print(f"  a[1:4] = {a[1:4]}")
    print(f"  a[-1] = {a[-1]} (last element)")

    # Boolean indexing (powerful!)
    print(f"\nBoolean Indexing:")
    mask = a > 3
    print(f"  a > 3: {mask}")
    print(f"  a[a > 3] = {a[mask]}")

    print()


def performance_comparison():
    """
    Show why tensors are faster than Python loops
    """
    print("="*60)
    print("PART 5: Performance - Why Use Tensors?")
    print("="*60)

    # Create large array
    size = 1000000
    data = torch.randn(size)

    # Time tensor operation
    import time

    start = time.time()
    result_tensor = (data * 2).sum()
    tensor_time = time.time() - start

    # Time Python loop (on smaller data to not wait forever)
    small_data = data[:10000].tolist()
    start = time.time()
    result_loop = sum([x * 2 for x in small_data])
    loop_time = time.time() - start

    # Extrapolate
    extrapolated_loop_time = loop_time * (size / 10000)

    print(f"Processing {size:,} numbers:")
    print(f"  Tensor operation: {tensor_time*1000:.2f} ms")
    print(f"  Python loop (extrapolated): {extrapolated_loop_time*1000:.2f} ms")
    print(f"  Speedup: {extrapolated_loop_time/tensor_time:.0f}x faster!")

    print(f"\n  💡 This is on CPU. On GPU, it's 100-1000x faster!")
    print()


def main():
    """
    Run all demonstrations
    """
    print("\n")
    print("🚀 " + "="*56 + " 🚀")
    print("   Welcome to PyTorch Tensors for C Programmers!")
    print("🚀 " + "="*56 + " 🚀")
    print()

    c_style_thinking()
    multidimensional_arrays()
    real_world_security_analysis()
    tensor_operations_cheatsheet()
    performance_comparison()

    print("="*60)
    print("✅ Day 1 Complete!")
    print("="*60)
    print("\nKey Takeaways:")
    print("  1. Tensors are like C arrays, but run on GPUs")
    print("  2. No loops needed - vectorized operations are faster")
    print("  3. Perfect for analyzing large datasets (logs, metrics, etc.)")
    print("  4. You can do real security analysis with just basic tensors!")
    print("\nNext Steps:")
    print("  • Try modifying the failed_logins data with your own patterns")
    print("  • Experiment with different thresholds")
    print("  • Run: python day2_tensor_operations.py")
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
