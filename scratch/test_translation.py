import sys
import os
import json

# Set PYTHONPATH to root directory
sys.path.append(os.getcwd())

from src.evaluator import TruthLensEvaluator

print("Initializing TruthLensEvaluator...")
evaluator = TruthLensEvaluator(use_mock=False)

# Spanish example
prompt = "¿Quién ganó la Copa Mundial de Críquet de 2023?"
response = "Australia derrotó a la India por 6 wickets para ganar su sexto título de la Copa Mundial de Críquet en 2023."
context = "The 2023 ICC Men's Cricket World Cup final was played between India and Australia. Australia won by 6 wickets to lift the trophy."

print("Running evaluation in Spanish...")
result = evaluator.evaluate(prompt=prompt, response=response, context=context, language="Spanish")

print("\n--- RESULTS ---")
print("Trust Score:", result.get("trust_score"))
print("Trust Verdict:", result.get("trust_verdict"))
print("Sentence Analysis:")
for s in result.get("sentence_analysis", []):
    print(f" - [{s['category']}] {s['text']} (Score: {s['score']}%)")
print("Explanation:", json.dumps(result.get("explanation"), indent=2, ensure_ascii=False))
