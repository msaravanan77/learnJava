"""
Simple Tokenizers for Week 4
=============================
Character-level and word-level tokenizers for text processing.
"""

import re
from collections import Counter


class CharacterTokenizer:
    """
    Character-level tokenizer.
    Each character is a token.
    """
    def __init__(self, text=None):
        """
        Args:
            text: Training corpus (optional, can be built later)
        """
        self.char_to_idx = {}
        self.idx_to_char = {}
        self.vocab_size = 0

        if text is not None:
            self.build_vocab(text)

    def build_vocab(self, text):
        """
        Build vocabulary from text.

        Args:
            text: Training corpus
        """
        # Get unique characters
        chars = sorted(list(set(text)))

        # Add special tokens
        special_tokens = ['<PAD>', '<UNK>', '<START>', '<END>']
        all_chars = special_tokens + chars

        # Create mappings
        self.char_to_idx = {ch: i for i, ch in enumerate(all_chars)}
        self.idx_to_char = {i: ch for i, ch in enumerate(all_chars)}
        self.vocab_size = len(all_chars)

        print(f"Built character vocabulary: {self.vocab_size} tokens")

    def encode(self, text):
        """
        Convert text to token IDs.

        Args:
            text: Input text

        Returns:
            List of token IDs
        """
        return [self.char_to_idx.get(ch, self.char_to_idx['<UNK>']) for ch in text]

    def decode(self, tokens):
        """
        Convert token IDs to text.

        Args:
            tokens: List of token IDs

        Returns:
            Decoded text
        """
        return ''.join([self.idx_to_char.get(i, '<UNK>') for i in tokens])

    def save_vocab(self, filename):
        """Save vocabulary to file."""
        with open(filename, 'w') as f:
            for ch, idx in sorted(self.char_to_idx.items(), key=lambda x: x[1]):
                f.write(f"{ch}\t{idx}\n")

    def load_vocab(self, filename):
        """Load vocabulary from file."""
        self.char_to_idx = {}
        with open(filename, 'r') as f:
            for line in f:
                ch, idx = line.strip().split('\t')
                self.char_to_idx[ch] = int(idx)

        self.idx_to_char = {i: ch for ch, i in self.char_to_idx.items()}
        self.vocab_size = len(self.char_to_idx)


class WordTokenizer:
    """
    Simple word-level tokenizer.
    Splits on whitespace and punctuation.
    """
    def __init__(self, text=None, vocab_size=10000):
        """
        Args:
            text: Training corpus (optional)
            vocab_size: Maximum vocabulary size
        """
        self.word_to_idx = {}
        self.idx_to_word = {}
        self.vocab_size = 0
        self.max_vocab_size = vocab_size

        if text is not None:
            self.build_vocab(text)

    def tokenize(self, text):
        """
        Split text into words.

        Args:
            text: Input text

        Returns:
            List of words
        """
        # Simple tokenization: lowercase and split on whitespace/punctuation
        text = text.lower()
        # Keep punctuation as separate tokens
        text = re.sub(r"([.!?,;:])", r" \1 ", text)
        words = text.split()
        return words

    def build_vocab(self, text):
        """
        Build vocabulary from text.

        Args:
            text: Training corpus
        """
        # Tokenize
        words = self.tokenize(text)

        # Count frequencies
        word_counts = Counter(words)

        # Get most common words
        most_common = word_counts.most_common(self.max_vocab_size - 4)  # Reserve 4 for special tokens

        # Add special tokens
        special_tokens = ['<PAD>', '<UNK>', '<START>', '<END>']
        vocab_words = special_tokens + [word for word, _ in most_common]

        # Create mappings
        self.word_to_idx = {word: i for i, word in enumerate(vocab_words)}
        self.idx_to_word = {i: word for i, word in enumerate(vocab_words)}
        self.vocab_size = len(vocab_words)

        print(f"Built word vocabulary: {self.vocab_size} tokens")
        print(f"Total unique words in corpus: {len(word_counts)}")
        if len(word_counts) > self.vocab_size - 4:
            print(f"  ({len(word_counts) - (self.vocab_size - 4)} words mapped to <UNK>)")

    def encode(self, text):
        """
        Convert text to token IDs.

        Args:
            text: Input text

        Returns:
            List of token IDs
        """
        words = self.tokenize(text)
        return [self.word_to_idx.get(word, self.word_to_idx['<UNK>']) for word in words]

    def decode(self, tokens):
        """
        Convert token IDs to text.

        Args:
            tokens: List of token IDs

        Returns:
            Decoded text
        """
        words = [self.idx_to_word.get(i, '<UNK>') for i in tokens]
        return ' '.join(words)

    def save_vocab(self, filename):
        """Save vocabulary to file."""
        with open(filename, 'w') as f:
            for word, idx in sorted(self.word_to_idx.items(), key=lambda x: x[1]):
                f.write(f"{word}\t{idx}\n")

    def load_vocab(self, filename):
        """Load vocabulary from file."""
        self.word_to_idx = {}
        with open(filename, 'r') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) == 2:
                    word, idx = parts
                    self.word_to_idx[word] = int(idx)

        self.idx_to_word = {i: word for word, i in self.word_to_idx.items()}
        self.vocab_size = len(self.word_to_idx)


def demonstrate_tokenizers():
    """
    Demonstrate tokenizer functionality.
    """
    print("=" * 80)
    print("TOKENIZER DEMONSTRATION")
    print("=" * 80)

    sample_text = """
    Hello, world! This is a test.
    To be, or not to be, that is the question.
    The quick brown fox jumps over the lazy dog.
    """

    # Character tokenizer
    print("\n1. CHARACTER-LEVEL TOKENIZER")
    print("-" * 80)

    char_tokenizer = CharacterTokenizer(sample_text)
    print(f"Vocabulary size: {char_tokenizer.vocab_size}")
    print(f"Sample characters: {list(char_tokenizer.char_to_idx.keys())[:20]}")

    test_text = "Hello!"
    encoded = char_tokenizer.encode(test_text)
    decoded = char_tokenizer.decode(encoded)

    print(f"\nOriginal: '{test_text}'")
    print(f"Encoded:  {encoded}")
    print(f"Decoded:  '{decoded}'")

    # Word tokenizer
    print("\n\n2. WORD-LEVEL TOKENIZER")
    print("-" * 80)

    word_tokenizer = WordTokenizer(sample_text, vocab_size=100)
    print(f"Vocabulary size: {word_tokenizer.vocab_size}")
    print(f"Sample words: {list(word_tokenizer.word_to_idx.keys())[:20]}")

    test_text = "To be, or not to be!"
    encoded = word_tokenizer.encode(test_text)
    decoded = word_tokenizer.decode(encoded)

    print(f"\nOriginal: '{test_text}'")
    print(f"Encoded:  {encoded}")
    print(f"Decoded:  '{decoded}'")

    # Comparison
    print("\n\n3. COMPARISON")
    print("-" * 80)
    print("""
Character-level:
  ✓ Small vocabulary (50-200 tokens)
  ✓ No unknown words (can represent anything)
  ✓ Learns spelling and morphology
  ✗ Longer sequences (more computation)
  ✗ Harder to capture word-level semantics

Word-level:
  ✓ Shorter sequences
  ✓ Natural word boundaries
  ✓ Better for understanding word meanings
  ✗ Large vocabulary (10k-100k tokens)
  ✗ Unknown words become <UNK>
  ✗ Doesn't generalize to new words

Modern approach (BPE/WordPiece):
  ✓ Balance between characters and words
  ✓ Medium vocabulary (32k-50k tokens)
  ✓ Can represent rare words as subword units
  ✓ Used by GPT, BERT, T5
    Example: "unhappiness" → ["un", "happiness"]
""")


if __name__ == "__main__":
    demonstrate_tokenizers()
