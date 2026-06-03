import requests
import json

base_url = "http://127.0.0.1:8000"

print("--- Testing API Generation and Evaluation ---")

# Step 1: Login to get token (since API endpoints have verify_token dependency)
# Let's register a test user if login fails, or try registering first.
register_data = {
    "email": "test_user_api_test@truthlens.ai",
    "password": "testpassword123",
    "name": "Test User"
}
session_token = None
try:
    resp = requests.post(f"{base_url}/api/register", json=register_data)
    res_json = resp.json()
    if res_json.get("status") == "success":
        session_token = res_json.get("token")
        print("Successfully registered test user.")
    else:
        # Try login
        resp = requests.post(f"{base_url}/api/login", json=register_data)
        res_json = resp.json()
        if res_json.get("status") == "success":
            session_token = res_json.get("token")
            print("Successfully logged in test user.")
        else:
            print("Auth failed:", res_json)
except Exception as e:
    print("Auth exception:", e)

if not session_token:
    print("Failed to get session token, using empty auth.")
    headers = {}
else:
    headers = {"Authorization": f"Bearer {session_token}"}

# Test 1: Prompt generator for "name of prime minister of india"
# It should bypass Direct Answer Extractor and give Narendra Modi (from Llama 3 or Qwen model)
generate_req = {
    "prompt": "name of prime minister of india",
    "model": "llama", # or "tiny"
    "evaluate": True
}
print("\n[TEST 1] Generating response for: 'name of prime minister of india'...")
try:
    resp = requests.post(f"{base_url}/api/generate", json=generate_req, headers=headers)
    gen_result = resp.json()
    print("Model Used:", gen_result.get("model"))
    print("Generated Response:", gen_result.get("generated_response"))
    print("Context (len):", len(gen_result.get("context", "")))
    
    # Test 2: Heatmap structure and explanation
    print("\n[TEST 2] Verifying sentence analysis and tooltips in evaluation result:")
    evaluation = gen_result.get("evaluation")
    if evaluation:
        print("Overall Risk:", evaluation.get("overall_risk"))
        print("Trust Score:", evaluation.get("trust_score"))
        print("Trust Verdict:", evaluation.get("trust_verdict"))
        
        print("\nSentence Analysis Details:")
        for idx, s in enumerate(evaluation.get("sentence_analysis", [])):
            print(f"  Sentence #{idx+1}:")
            print(f"    Text:     {s.get('text')}")
            print(f"    Category: {s.get('category')}")
            print(f"    Type:     {s.get('type')}")
            print(f"    Score:    {s.get('score')}%")
            print(f"    Reason:   {s.get('reason')}")
            
        print("\nExplanation:")
        print(json.dumps(evaluation.get("explanation"), indent=2))
    else:
        print("Evaluation was not returned.")
except Exception as e:
    print("Generation/Evaluation request failed:", e)
