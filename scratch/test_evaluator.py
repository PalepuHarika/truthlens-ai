import sys
import os
sys.path.append(os.getcwd())

from src.evaluator import TruthLensEvaluator, get_verdict_label

print("--- Testing get_verdict_label directly ---")
test_cases = [
    (0, "High Trust"),
    (10, "High Trust"),
    (20, "High Trust"),
    (21, "Moderate Risk"),
    (30, "Moderate Risk"),
    (40, "Moderate Risk"),
    (41, "High Risk"),
    (50, "High Risk"),
    (60, "High Risk"),
    (61, "Severe Risk"),
    (80, "Severe Risk"),
    (100, "Severe Risk"),
]

for score, expected in test_cases:
    actual = get_verdict_label(score)
    assert actual == expected, f"Failed for score {score}: expected {expected}, got {actual}"
    print(f"Score {score}% -> {actual} (Pass)")

print("\n--- Testing _mock_evaluate returns ---")
evaluator = TruthLensEvaluator(use_mock=True)
result = evaluator.evaluate("test prompt", "test response", "test context")
print("Mock Result Structure:")
for k, v in result.items():
    if k not in ["components", "details"]:
        v_safe = str(v).encode('ascii', errors='replace').decode('ascii')
        print(f"  {k}: {v_safe}")

# Verify matching components keys
print("Mock Result Components keys:")
print(list(result["components"].keys()))

assert "trust_verdict" in result, "trust_verdict missing in mock results"
assert "trust_score" in result, "trust_score missing in mock results"
assert "overall_risk" in result, "overall_risk missing in mock results"
assert result["trust_score"] == 100 - round(result["overall_risk"] * 100), "trust_score mismatch with overall_risk"
expected_verdict = get_verdict_label(round(result["overall_risk"] * 100))
assert result["trust_verdict"] == expected_verdict, f"verdict mismatch: expected {expected_verdict}, got {result['trust_verdict']}"
print("\nMock evaluation consistency check passed successfully!")
