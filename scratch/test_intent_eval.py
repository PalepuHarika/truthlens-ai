import requests
import json

base_url = "http://127.0.0.1:8000"

print("--- Running Backend Intent and Evaluation Verification Tests ---")

# Step 1: Auth Session Token retrieval
register_data = {
    "email": "test_user_intent_test@truthlens.ai",
    "password": "testpassword123",
    "name": "Test User"
}
session_token = None
try:
    resp = requests.post(f"{base_url}/api/register", json=register_data)
    res_json = resp.json()
    if res_json.get("status") == "success":
        session_token = res_json.get("token")
        print("[AUTH] Successfully registered test user.")
    else:
        resp = requests.post(f"{base_url}/api/login", json=register_data)
        res_json = resp.json()
        if res_json.get("status") == "success":
            session_token = res_json.get("token")
            print("[AUTH] Successfully logged in test user.")
        else:
            print("[AUTH] Auth failed:", res_json)
except Exception as e:
    print("[AUTH] Auth exception:", e)

headers = {"Authorization": f"Bearer {session_token}"} if session_token else {}

# Test 1: Person Lookup Query Intent and Output formatting
print("\n[TEST 1] Testing person lookup intent generation for 'who is prime minister of india'...")
try:
    generate_req = {
        "prompt": "who is prime minister of india",
        "model": "llama",
        "evaluate": True
    }
    resp = requests.post(f"{base_url}/api/generate", json=generate_req, headers=headers)
    gen_result = resp.json()
    print("Model Used:", gen_result.get("model"))
    print("Generated Response:", gen_result.get("generated_response"))
    
    # Assert formatting
    response_text = gen_result.get("generated_response", "")
    if "Current Prime Minister of India:" in response_text or "Narendra Modi" in response_text:
        print("-> [PASS] Generation formatted correctly as person lookup entity.")
    else:
        print("-> [FAIL] Generation did not follow formatting expectations:", response_text)
except Exception as e:
    print("-> [ERROR] Test 1 failed:", e)

# Test 2: Irrelevant Factual Response evaluation
print("\n[TEST 2] Testing irrelevant factual response (Factual but Irrelevant)...")
try:
    eval_req = {
        "prompt": "who is prime minister of india",
        "response": "Gravity is a fundamental force that attracts objects towards each other.",
        "context": "Gravity is a natural phenomenon by which all things with mass or energy are brought toward one another. It is a fundamental interaction.",
        "language": "English"
    }
    resp = requests.post(f"{base_url}/api/evaluate", json=eval_req, headers=headers)
    eval_result = resp.json()
    status = eval_result.get("status")
    verdict = eval_result.get("trust_verdict")
    relevance = eval_result.get("relevance_score")
    factuality = eval_result.get("factual_score")
    
    print(f"Status returned: {status}")
    print(f"Verdict returned: {verdict}")
    print(f"Relevance Score: {relevance}")
    print(f"Factuality Score: {factuality}")
    
    if status == "Irrelevant Response" and verdict == "Irrelevant Response":
        print("-> [PASS] Correctly flagged as Irrelevant Response.")
    else:
        print("-> [FAIL] Status/Verdict not flagged as Irrelevant Response.")
except Exception as e:
    print("-> [ERROR] Test 2 failed:", e)

# Test 3: Relevant and Factual Response (Verified threshold checks)
print("\n[TEST 3] Testing relevant and factual response (Should be Verified)...")
try:
    eval_req = {
        "prompt": "who is prime minister of india",
        "response": "Current Prime Minister of India: Narendra Modi.",
        "context": "Narendra Modi has served as the Prime Minister of India since 2014.",
        "language": "English"
    }
    resp = requests.post(f"{base_url}/api/evaluate", json=eval_req, headers=headers)
    eval_result = resp.json()
    status = eval_result.get("status")
    verdict = eval_result.get("trust_verdict")
    needs_correction = eval_result.get("needs_correction")
    corrected_answer = eval_result.get("corrected_answer")
    explanation = eval_result.get("explanation")
    sentence_analysis = eval_result.get("sentence_analysis", [])
    
    print(f"Status returned: {status}")
    print(f"Verdict returned: {verdict}")
    print(f"needs_correction: {needs_correction}")
    print(f"corrected_answer: {corrected_answer}")
    print(f"Explanation: {explanation}")
    
    if sentence_analysis:
        s = sentence_analysis[0]
        print(f"Sentence Text: {s.get('text')}")
        print(f"Category: {s.get('category')}")
        print(f"Score (Confidence): {s.get('score')}%")
        print(f"Relevance Score: {s.get('relevance_score')}")
        print(f"Factual Score: {s.get('factual_score')}")
        
        expected_conf = int(round(min(s.get('relevance_score'), s.get('factual_score')) * 100))
        
        if (s.get('category') == "verified" and 
            status == "Verified" and 
            needs_correction is False and 
            corrected_answer == "No correction required" and 
            explanation is None and
            s.get('score') == expected_conf):
            print("-> [PASS] Verified correct response correctly bypassed flagging and used single confidence score.")
        else:
            print("-> [FAIL] Score/Correction assertions failed.")
    else:
        print("-> [FAIL] No sentence analysis returned.")
except Exception as e:
    print("-> [ERROR] Test 3 failed:", e)
