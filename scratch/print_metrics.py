import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluator import TruthLensEvaluator

evaluator = TruthLensEvaluator(use_mock=False)
res = evaluator.evaluate(
    prompt="Who is the president of the USA?",
    response="Joe Biden is the president of the USA.",
    context="Joe Biden is the current president of the United States."
)

print(f"Relevance: {res['relevance_score']}")
print(f"Factual: {res['factual_score']}")
print(f"Status: {res['status']}")
print(f"Reason: {res['reason']}")
print(f"Confidence: {res['confidence']}")
