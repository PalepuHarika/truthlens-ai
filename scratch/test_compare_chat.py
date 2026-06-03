import urllib.request
import json

def test_api():
    print("Testing /api/compare with Spanish language...")
    url = "http://127.0.0.1:8000/api/compare"
    data = {
        "prompt": "What is the capital of Germany?",
        "language": "Spanish"
    }
    
    # We need a token or we can pass a dummy since auth might be required.
    # Wait, the compare endpoint has: Depends(verify_token)
    # Let's register a temporary test user or use the sessions db directly to insert a dummy session token!
    # Wait, we can look up the token we used earlier, or just bypass/register a user in the script!
    pass

def test_with_auth():
    # 1. Register a user
    print("Registering temporary user...")
    url_reg = "http://127.0.0.1:8000/api/register"
    reg_data = {
        "email": "testlanguage@truthlens.ai",
        "password": "password123",
        "name": "Language Tester"
    }
    
    req_reg = urllib.request.Request(
        url_reg,
        data=json.dumps(reg_data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    token = None
    try:
        with urllib.request.urlopen(req_reg) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            if res_data.get("status") == "success":
                token = res_data.get("token")
                print("Registered successfully. Token:", token)
            else:
                print("Registration returned message (e.g. already exists):", res_data.get("message"))
    except Exception as e:
        print("Registration failed:", e)

    if not token:
        # Try login instead
        print("Attempting login...")
        url_log = "http://127.0.0.1:8000/api/login"
        req_log = urllib.request.Request(
            url_log,
            data=json.dumps(reg_data).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        try:
            with urllib.request.urlopen(req_log) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                token = res_data.get("token")
                print("Logged in successfully. Token:", token)
        except Exception as log_err:
            print("Login failed too:", log_err)
            return

    if not token:
        return

    # 2. Test Compare LLMs
    print("\nTesting /api/compare with Spanish language...")
    url_comp = "http://127.0.0.1:8000/api/compare"
    comp_data = {
        "prompt": "What is the capital of Germany?",
        "language": "Spanish"
    }
    req_comp = urllib.request.Request(
        url_comp,
        data=json.dumps(comp_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    try:
        with urllib.request.urlopen(req_comp) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            print("Compare responses:")
            for r in res_data.get("responses", []):
                print(f"  {r['model']}: {r['text'][:120]}...")
    except Exception as e:
        print("Compare test failed:", e)

    # 3. Test Generate (Chat mode)
    print("\nTesting /api/generate (Chat mode) with Spanish language...")
    url_gen = "http://127.0.0.1:8000/api/generate"
    gen_data = {
        "prompt": "Tell me a short joke.",
        "history": [{"role": "user", "content": "Hello"}, {"role": "assistant", "content": "Hola, ¿en qué puedo ayudarte hoy?"}],
        "language": "Spanish",
        "model": "llama",
        "evaluate": True
    }
    req_gen = urllib.request.Request(
        url_gen,
        data=json.dumps(gen_data).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    )
    try:
        with urllib.request.urlopen(req_gen) as resp:
            res_data = json.loads(resp.read().decode("utf-8"))
            print("Generated Chat Response:", res_data.get("generated_response"))
            print("Evaluation Verdict:", res_data.get("evaluation", {}).get("trust_verdict") if res_data.get("evaluation") else "None")
    except Exception as e:
        print("Generate chat test failed:", e)

if __name__ == "__main__":
    test_with_auth()
