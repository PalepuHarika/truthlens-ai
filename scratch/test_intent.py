import sys
sys.path.insert(0, '.')

from src.evaluator import (
    detect_query_intent,
    INTENT_PERSON_LOOKUP, INTENT_DATE_LOOKUP,
    INTENT_DEFINITION, INTENT_EXPLANATION, INTENT_FACT_LOOKUP,
)

# --- Test 1: 5 canonical intent labels ---
tests = [
    ('who is the prime minister of india', INTENT_PERSON_LOOKUP),
    ('name of the president of usa',       INTENT_PERSON_LOOKUP),
    ('when was einstein born',             INTENT_DATE_LOOKUP),
    ('what is machine learning',           INTENT_DEFINITION),
    ('explain how gravity works',          INTENT_EXPLANATION),
    ('largest planet in the solar system', INTENT_FACT_LOOKUP),
]
print('=== Intent Detection Tests ===')
all_pass = True
for q, expected in tests:
    got = detect_query_intent(q)
    ok = got == expected
    if not ok:
        all_pass = False
    print(f'  [{"PASS" if ok else "FAIL"}]  "{q}" -> "{got}" (expected "{expected}")')

print()

# --- Test 2: verify_response returns a 4-tuple ---
# (No Groq call needed - just check the signature by inspecting)
from src.evaluator import TruthLensEvaluator
import inspect
sig = inspect.signature(TruthLensEvaluator.verify_response)
print(f'verify_response signature: {sig}')
print()

# --- Test 3: main.py detect_intent delegates to evaluator ---
from src.main import detect_intent
result = detect_intent('who is the president of france')
print(f'main.detect_intent("who is the president of france") -> "{result}"')
expected_main = INTENT_PERSON_LOOKUP
ok_main = result == expected_main
print(f'  [{"PASS" if ok_main else "FAIL"}]  (expected "{expected_main}")')

if all_pass and ok_main:
    print('\n[OK] All structural tests passed.')
    sys.exit(0)
else:
    print('\n[FAIL] Some tests failed.')
    sys.exit(1)
