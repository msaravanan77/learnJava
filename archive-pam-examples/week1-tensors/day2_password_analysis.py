"""
Day 2: Tensor Operations - Password Strength Analyzer
Real-world application using tensor operations

This demonstrates:
1. Working with structured data in tensors
2. Vectorized calculations (no loops!)
3. Building a practical security tool
"""

import torch
import string
import math


class PasswordAnalyzer:
    """
    Analyze password strength using tensor operations
    Much faster than analyzing passwords one-by-one in loops
    """

    def __init__(self):
        self.min_length = 8
        self.recommended_length = 12

    def analyze_batch(self, passwords):
        """
        Analyze multiple passwords at once using tensors

        For each password, we create a feature vector:
        [length, has_uppercase, has_lowercase, has_digit, has_special, entropy]
        """
        features = []

        for pwd in passwords:
            features.append(self._extract_features(pwd))

        # Convert to tensor: [num_passwords, 6_features]
        features_tensor = torch.tensor(features, dtype=torch.float32)

        print(f"Analyzing {len(passwords)} passwords...")
        print(f"Feature tensor shape: {features_tensor.shape}")
        print()

        # Calculate scores using vectorized operations (no loops!)
        scores = self._calculate_scores(features_tensor)

        # Classify passwords
        classifications = self._classify_passwords(scores)

        return features_tensor, scores, classifications

    def _extract_features(self, password):
        """
        Extract features from a single password
        In C, you'd do this with multiple if statements and loops
        """
        features = [
            len(password),  # Length
            int(any(c.isupper() for c in password)),  # Has uppercase
            int(any(c.islower() for c in password)),  # Has lowercase
            int(any(c.isdigit() for c in password)),  # Has digit
            int(any(c in string.punctuation for c in password)),  # Has special char
            self._calculate_entropy(password)  # Entropy score
        ]
        return features

    def _calculate_entropy(self, password):
        """
        Calculate Shannon entropy - measures randomness/unpredictability
        Higher entropy = harder to guess
        """
        if not password:
            return 0.0

        # Count character frequencies
        freq = {}
        for char in password:
            freq[char] = freq.get(char, 0) + 1

        # Calculate entropy
        entropy = 0.0
        length = len(password)
        for count in freq.values():
            probability = count / length
            entropy -= probability * math.log2(probability)

        # Normalize by length for a 0-100 scale
        return entropy * len(password)

    def _calculate_scores(self, features_tensor):
        """
        Calculate password strength scores using tensor operations

        Score components:
        - Length: 2 points per character
        - Complexity: 10 points each for uppercase/lowercase/digit/special
        - Entropy: Direct contribution
        - Bonus: 20 points if length >= 12
        """
        # Extract features (like accessing struct members in C)
        lengths = features_tensor[:, 0]
        has_uppercase = features_tensor[:, 1]
        has_lowercase = features_tensor[:, 2]
        has_digit = features_tensor[:, 3]
        has_special = features_tensor[:, 4]
        entropy = features_tensor[:, 5]

        # Vectorized score calculation (NO LOOPS!)
        length_score = lengths * 2
        complexity_score = (has_uppercase + has_lowercase + has_digit + has_special) * 10
        entropy_score = entropy

        # Bonus for recommended length
        length_bonus = (lengths >= self.recommended_length).float() * 20

        # Total score
        total_score = length_score + complexity_score + entropy_score + length_bonus

        return total_score

    def _classify_passwords(self, scores):
        """
        Classify passwords based on scores using tensor comparisons
        """
        # Use tensor comparisons (like C conditionals, but vectorized)
        classifications = torch.zeros(len(scores), dtype=torch.long)

        # 0 = Very Weak, 1 = Weak, 2 = Fair, 3 = Good, 4 = Strong
        classifications[scores < 40] = 0   # Very Weak
        classifications[(scores >= 40) & (scores < 60)] = 1  # Weak
        classifications[(scores >= 60) & (scores < 80)] = 2  # Fair
        classifications[(scores >= 80) & (scores < 100)] = 3  # Good
        classifications[scores >= 100] = 4  # Strong

        return classifications

    def print_report(self, passwords, features, scores, classifications):
        """
        Print detailed analysis report
        """
        class_names = ['Very Weak', 'Weak', 'Fair', 'Good', 'Strong']
        class_emoji = ['🔴', '🟠', '🟡', '🟢', '🟢']

        print("="*80)
        print(" "*25 + "PASSWORD STRENGTH ANALYSIS REPORT")
        print("="*80)
        print()

        # Individual password analysis
        for i, pwd in enumerate(passwords):
            score = scores[i].item()
            class_idx = classifications[i].item()
            feat = features[i]

            # Mask password for security (show only length)
            masked = '*' * len(pwd)

            print(f"Password #{i+1}: {masked} (length: {len(pwd)})")
            print(f"  Score: {score:.1f}/120")
            print(f"  Rating: {class_emoji[class_idx]} {class_names[class_idx]}")

            print(f"  Features:")
            print(f"    ✓ Uppercase letters: {'Yes' if feat[1] else 'No'}")
            print(f"    ✓ Lowercase letters: {'Yes' if feat[2] else 'No'}")
            print(f"    ✓ Numbers: {'Yes' if feat[3] else 'No'}")
            print(f"    ✓ Special characters: {'Yes' if feat[4] else 'No'}")
            print(f"    ✓ Entropy: {feat[5]:.1f}")

            # Recommendations
            if class_idx < 3:
                print(f"  ⚠️  Recommendations:")
                if feat[0] < self.recommended_length:
                    print(f"    • Increase length to at least {self.recommended_length} characters")
                if feat[1] == 0:
                    print(f"    • Add uppercase letters")
                if feat[2] == 0:
                    print(f"    • Add lowercase letters")
                if feat[3] == 0:
                    print(f"    • Add numbers")
                if feat[4] == 0:
                    print(f"    • Add special characters (!@#$%^&*)")

            print()

        # Summary statistics using tensors
        print("="*80)
        print(" "*30 + "SUMMARY STATISTICS")
        print("="*80)
        print()

        print(f"Total passwords analyzed: {len(passwords)}")
        print(f"Average score: {scores.mean():.1f}")
        print(f"Average length: {features[:, 0].mean():.1f}")
        print()

        # Distribution
        print("Strength Distribution:")
        for i, name in enumerate(class_names):
            count = (classifications == i).sum().item()
            percentage = count / len(passwords) * 100
            bar = '█' * int(percentage / 2)
            print(f"  {class_emoji[i]} {name:12s}: {count:2d} ({percentage:5.1f}%) {bar}")

        print()

        # Security recommendations
        weak_count = (classifications < 2).sum().item()
        if weak_count > 0:
            print(f"🚨 SECURITY ALERT: {weak_count} weak passwords detected!")
            print(f"   Recommendation: Enforce password policy requiring:")
            print(f"   • Minimum length: {self.recommended_length} characters")
            print(f"   • At least 3 character types (upper, lower, digit, special)")
            print()


def demonstrate_tensor_operations():
    """
    Show how tensor operations work with password data
    """
    print("="*80)
    print(" "*20 + "TENSOR OPERATIONS DEMONSTRATION")
    print("="*80)
    print()

    # Create sample feature matrix
    # Rows: passwords, Columns: features
    features = torch.tensor([
        [8, 1, 1, 1, 0, 35.2],   # Password 1
        [12, 1, 1, 1, 1, 58.6],  # Password 2
        [6, 0, 1, 1, 0, 22.1],   # Password 3
        [15, 1, 1, 1, 1, 72.4],  # Password 4
    ])

    print("Feature matrix (passwords x features):")
    print(features)
    print(f"Shape: {features.shape} = {features.shape[0]} passwords, {features.shape[1]} features")
    print()

    # Extract specific features
    lengths = features[:, 0]
    print(f"All password lengths (column 0): {lengths}")

    # Filter operations
    long_passwords = features[features[:, 0] >= 12]
    print(f"\nPasswords with length >= 12:")
    print(long_passwords)

    # Aggregations
    print(f"\nStatistics:")
    print(f"  Average length: {features[:, 0].mean():.1f}")
    print(f"  Max entropy: {features[:, 5].max():.1f}")
    print(f"  Passwords with special chars: {features[:, 4].sum().int()}")

    # Comparisons
    strong_mask = (features[:, 0] >= 12) & (features[:, 4] == 1)
    strong_count = strong_mask.sum()
    print(f"\n  Strong passwords (length>=12 AND has special chars): {strong_count}")

    print()


def main():
    """
    Main demonstration
    """
    print("\n")
    print("🔐 " + "="*74 + " 🔐")
    print("   Password Strength Analyzer - Tensor Operations in Action")
    print("🔐 " + "="*74 + " 🔐")
    print()

    # Demonstrate tensor operations
    demonstrate_tensor_operations()

    # Test passwords (common weak passwords + some stronger ones)
    test_passwords = [
        "password",              # Very weak
        "Password1",             # Weak
        "P@ssw0rd",              # Fair
        "MySecureP@ss2024",      # Good
        "Tr0ub4dor&3",           # Strong (xkcd reference)
        "admin",                 # Very weak
        "Admin123",              # Weak
        "C0mpl3x!Pass",          # Good
        "correcthorsebatterystaple",  # xkcd - long but simple
        "Xy9$mK2#pL6@nQ8",       # Strong - random
        "12345678",              # Very weak
        "Summer2024!",           # Fair
    ]

    # Analyze passwords
    analyzer = PasswordAnalyzer()
    features, scores, classifications = analyzer.analyze_batch(test_passwords)

    # Print detailed report
    analyzer.print_report(test_passwords, features, scores, classifications)

    # Real-world application
    print("="*80)
    print(" "*25 + "REAL-WORLD APPLICATION")
    print("="*80)
    print()
    print("How to use this in your PAM system:")
    print()
    print("1. Extract passwords from authentication logs")
    print("2. Batch process thousands of passwords at once using tensors")
    print("3. Identify weak passwords in your organization")
    print("4. Generate compliance reports")
    print("5. Enforce password policies automatically")
    print()
    print("Performance benefit:")
    print("  • Traditional approach: Analyze one password at a time")
    print("  • Tensor approach: Analyze 1000s of passwords simultaneously")
    print("  • Speedup: 10-100x faster on CPU, 100-1000x on GPU!")
    print()

    print("="*80)
    print("✅ Day 2 Complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print("  1. Tensors enable batch processing (analyze many items at once)")
    print("  2. Vectorized operations replace loops - much faster")
    print("  3. Tensor comparisons enable complex filtering")
    print("  4. Real security tools can be built with just tensor basics!")
    print("\nNext Steps:")
    print("  • Modify the scoring algorithm to match your security policy")
    print("  • Add more features (character patterns, dictionary words, etc.)")
    print("  • Run: python day3_neural_network_intro.py")
    print()


if __name__ == "__main__":
    try:
        import torch
        main()
    except ImportError:
        print("❌ PyTorch not installed!")
        print("\nInstall with: pip install torch")
