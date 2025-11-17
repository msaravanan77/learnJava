"""
Step 5: Evaluation & Testing
=============================
Evaluate the QA system with test questions and metrics.

This step:
- Loads test questions with ground truth answers
- Evaluates accuracy metrics (EM, F1)
- Analyzes performance
- Identifies strengths and weaknesses

Run: python step5_evaluation.py
"""

import json
import os
from typing import List, Dict, Tuple
from collections import Counter
from step4_qa_engine import QuestionAnsweringEngine
from step1_document_processor import DocumentProcessor
from step2_build_encoder import BERTEncoder, SimpleTokenizer
from step3_answer_extractor import AnswerExtractor


def normalize_answer(s: str) -> str:
    """
    Normalize answer for comparison (lowercase, remove articles/punctuation).
    """
    import re
    import string

    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def exact_match_score(prediction: str, ground_truth: str) -> float:
    """
    Compute exact match score (1.0 if match, 0.0 otherwise).
    """
    return 1.0 if normalize_answer(prediction) == normalize_answer(ground_truth) else 0.0


def f1_score(prediction: str, ground_truth: str) -> float:
    """
    Compute F1 score (token-level overlap).
    """
    pred_tokens = normalize_answer(prediction).split()
    truth_tokens = normalize_answer(ground_truth).split()

    if len(pred_tokens) == 0 or len(truth_tokens) == 0:
        return int(pred_tokens == truth_tokens)

    common_tokens = Counter(pred_tokens) & Counter(truth_tokens)
    num_common = sum(common_tokens.values())

    if num_common == 0:
        return 0.0

    precision = num_common / len(pred_tokens)
    recall = num_common / len(truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    return f1


class QAEvaluator:
    """
    Evaluate QA system performance.
    """
    def __init__(self, qa_engine: QuestionAnsweringEngine):
        self.qa_engine = qa_engine
        self.results = []

    def evaluate(self, test_questions: List[Dict]) -> Dict:
        """
        Evaluate on test questions.

        Args:
            test_questions: List of {'question': str, 'answer': str} dicts

        Returns:
            Evaluation metrics dictionary
        """
        self.results = []
        total_em = 0.0
        total_f1 = 0.0

        print(f"\nEvaluating on {len(test_questions)} questions...")
        print("-" * 80)

        for i, test_case in enumerate(test_questions, 1):
            question = test_case['question']
            ground_truth = test_case['answer']

            # Get prediction
            answer_dict = self.qa_engine.get_best_answer(question)
            prediction = answer_dict['answer']
            confidence = answer_dict['confidence']

            # Compute metrics
            em = exact_match_score(prediction, ground_truth)
            f1 = f1_score(prediction, ground_truth)

            total_em += em
            total_f1 += f1

            # Store result
            result = {
                'question': question,
                'predicted': prediction,
                'ground_truth': ground_truth,
                'exact_match': em,
                'f1': f1,
                'confidence': confidence
            }
            self.results.append(result)

            # Print progress
            status = "✓" if em == 1.0 else "✗"
            print(f"{status} {i:2d}. Q: {question[:50]:50s} | F1: {f1:.2f} | Conf: {confidence:.2f}")

        # Compute averages
        avg_em = total_em / len(test_questions) if test_questions else 0.0
        avg_f1 = total_f1 / len(test_questions) if test_questions else 0.0

        metrics = {
            'exact_match': avg_em,
            'f1': avg_f1,
            'num_questions': len(test_questions),
            'num_correct': int(total_em)
        }

        return metrics

    def print_evaluation_report(self, metrics: Dict):
        """Print detailed evaluation report."""
        print("\n" + "=" * 80)
        print("EVALUATION REPORT")
        print("=" * 80)

        print(f"\nOverall Metrics:")
        print(f"  Total questions:  {metrics['num_questions']}")
        print(f"  Exact matches:    {metrics['num_correct']}")
        print(f"  Exact Match (EM): {metrics['exact_match']:.1%}")
        print(f"  F1 Score:         {metrics['f1']:.1%}")

        # Show some examples
        print(f"\n{'-' * 80}")
        print("Sample Predictions:")
        print("-" * 80)

        for i, result in enumerate(self.results[:5], 1):
            print(f"\n{i}. Question: {result['question']}")
            print(f"   Predicted:    '{result['predicted']}'")
            print(f"   Ground Truth: '{result['ground_truth']}'")
            print(f"   F1: {result['f1']:.2f} | EM: {result['exact_match']:.0f} | Confidence: {result['confidence']:.3f}")

        # Analysis
        print(f"\n{'-' * 80}")
        print("Performance Analysis:")
        print("-" * 80)

        correct = [r for r in self.results if r['exact_match'] == 1.0]
        partial = [r for r in self.results if 0 < r['f1'] < 1.0]
        incorrect = [r for r in self.results if r['f1'] == 0.0]

        print(f"  Correct answers:  {len(correct):2d} ({len(correct) / len(self.results):.1%})")
        print(f"  Partial matches:  {len(partial):2d} ({len(partial) / len(self.results):.1%})")
        print(f"  Incorrect:        {len(incorrect):2d} ({len(incorrect) / len(self.results):.1%})")

        if incorrect:
            print(f"\n  Failed questions:")
            for r in incorrect[:3]:
                print(f"    - {r['question']}")

    def save_results(self, filepath: str = "evaluation_results.json"):
        """Save evaluation results to file."""
        with open(filepath, 'w') as f:
            json.dump(self.results, f, indent=2)
        print(f"\n✓ Results saved to {filepath}")


def create_test_questions() -> List[Dict]:
    """
    Create test questions with ground truth answers.
    """
    return [
        {
            "question": "What is attention?",
            "answer": "a mechanism that allows neural networks to focus on relevant information"
        },
        {
            "question": "What does BERT stand for?",
            "answer": "Bidirectional Encoder Representations from Transformers"
        },
        {
            "question": "What can transformers process in parallel?",
            "answer": "all tokens"
        },
        {
            "question": "What runs in parallel in multi-head attention?",
            "answer": "multiple attention mechanisms"
        },
        {
            "question": "What is BERT excellent for?",
            "answer": "text classification, named entity recognition, and question answering"
        },
        {
            "question": "How is BERT pre-trained?",
            "answer": "using masked language modeling"
        },
        {
            "question": "What computes weighted sum in attention?",
            "answer": "attention mechanism"
        },
        {
            "question": "When were transformers introduced?",
            "answer": "2017"
        }
    ]


def demonstrate_evaluation():
    """
    Demonstrate QA system evaluation.
    """
    print("=" * 80)
    print("STEP 5: EVALUATION & TESTING DEMONSTRATION")
    print("=" * 80)

    # Setup QA engine (reusing from step 4)
    print("\n1. Setting up QA engine...")
    from step4_qa_engine import demonstrate_qa_engine

    qa_engine = demonstrate_qa_engine()

    # Create test questions
    print("\n2. Loading test questions...")
    test_questions = create_test_questions()
    print(f"   Loaded {len(test_questions)} test questions")

    # Save test questions to file
    test_file = "test_questions.json"
    with open(test_file, 'w') as f:
        json.dump(test_questions, f, indent=2)
    print(f"   Saved to {test_file}")

    # Create evaluator
    print("\n3. Creating evaluator...")
    evaluator = QAEvaluator(qa_engine)

    # Run evaluation
    print("\n4. Running evaluation...")
    metrics = evaluator.evaluate(test_questions)

    # Print report
    evaluator.print_evaluation_report(metrics)

    # Save results
    evaluator.save_results()

    print("\n" + "=" * 80)
    print("✓ Step 5 Complete: Evaluation done!")
    print("=" * 80)

    print("\n📊 IMPORTANT NOTES:")
    print("-" * 80)
    print("This is a RANDOMLY INITIALIZED model, so low scores are expected!")
    print("\nFor production-quality results, you need to:")
    print("  1. Load pre-trained BERT weights (from Hugging Face)")
    print("  2. Fine-tune on SQuAD dataset (100k+ QA pairs)")
    print("  3. Train for 2-3 epochs with proper hyperparameters")
    print("\nExpected scores after proper training:")
    print("  - Exact Match (EM): 80-85%")
    print("  - F1 Score: 88-92%")
    print("-" * 80)

    return evaluator, metrics


if __name__ == "__main__":
    evaluator, metrics = demonstrate_evaluation()
