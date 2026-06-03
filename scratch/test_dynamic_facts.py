import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.evaluator import TruthLensEvaluator, is_dynamic_fact_query

print("--- Testing Dynamic Fact Detection ---")
dynamic_queries = [
    "Who is the current President of France?",
    "current prime minister of the UK",
    "Who is the CEO of Twitter right now?",
    "What is the date today?",
    "latest news about stock market",
    "Who won the 2026 Super Bowl?",
    "What is the weather today?"
]

static_queries = [
    "What is the definition of photosynthesis?",
    "Who wrote Romeo and Juliet?",
    "Explain how gravity works.",
    "How to write a binary search in Python?"
]

for q in dynamic_queries:
    assert is_dynamic_fact_query(q) is True, f"Failed on dynamic: {q}"
    print(f"[PASS] Detected dynamic: {q}")

for q in static_queries:
    assert is_dynamic_fact_query(q) is False, f"Failed on static: {q}"
    print(f"[PASS] Detected static: {q}")

print("\n--- Testing Outdated Information Verification ---")
evaluator = TruthLensEvaluator(use_mock=False)

# Scenario A: Contradicted (Outdated Information)
# Prompt asks for President of USA, response says Barack Obama (outdated), context says Joe Biden.
res_a = evaluator.evaluate(
    prompt="Who is the president of the USA?",
    response="The president of the USA is Barack Obama.",
    context="Joe Biden is the current president of the USA in 2024. Before him, Donald Trump was president, and Barack Obama served from 2009 to 2017."
)
print("Scenario A (Outdated/Contradicted):")
print(f"  Status: {res_a['status']}")
print(f"  Reason: {res_a['reason']}")
print(f"  Corrected Answer: {res_a['corrected_answer']}")
print(f"  Explanation correction: {res_a['explanation']['correction'] if res_a['explanation'] else 'None'}")
assert res_a['status'] == "Contradicted"
assert res_a['reason'] == "Outdated information"
assert res_a['corrected_answer'] != "No correction required"

# Scenario B: Verified (No Correction Required)
# Prompt asks for President of USA, response says Joe Biden, context says Joe Biden.
res_b = evaluator.evaluate(
    prompt="Who is the president of the USA?",
    response="Joe Biden is the president of the USA.",
    context="Joe Biden is the current president of the United States."
)
print("\nScenario B (Verified/Match):")
print(f"  Status: {res_b['status']}")
print(f"  Reason: {res_b['reason']}")
print(f"  Corrected Answer: {res_b['corrected_answer']}")
assert res_b['status'] == "Verified"
assert res_b['corrected_answer'] == "No correction required"

# Scenario C: Weak (Low confidence)
# Prompt asks for some fact, context has no info, relevance or factual score is low.
res_c = evaluator.evaluate(
    prompt="Tell me about the latest space mission in detail.",
    response="SpaceX launched a new satellite last week.",
    context="There are various space missions planned by different countries."
)
print("\nScenario C (Weak):")
print(f"  Status: {res_c['status']}")
print(f"  Reason: {res_c['reason']}")
print(f"  Confidence: {res_c.get('confidence')}")
print(f"  Corrected Answer: {res_c['corrected_answer']}")

print("\nAll dynamic facts verification tests completed successfully!")
