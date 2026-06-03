import urllib.request
import json

def test_api():
    print("Testing /api/generate with Spanish language...")
    url = "http://127.0.0.1:8000/api/generate"
    data = {
        "prompt": "What is the capital of France?",
        "model": "tiny",
        "language": "Spanish"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("Status Code: 200")
            print("Keys returned:", list(res_data.keys()))
            print("Response:", res_data.get("generated_response"))
            print("Model:", res_data.get("model"))
            print("RAG Chunks:", res_data.get("rag_chunks"))
    except Exception as e:
        print("Error calling /api/generate:", e)

    print("\nTesting /api/evaluate with Spanish response...")
    url_eval = "http://127.0.0.1:8000/api/evaluate"
    data_eval = {
        "prompt": "What is the capital of France?",
        "response": "La capital de Francia es París.",
        "context": "París es la capital de Francia y su ciudad más poblada.",
        "language": "Spanish"
    }
    
    req_eval = urllib.request.Request(
        url_eval,
        data=json.dumps(data_eval).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    
    try:
        with urllib.request.urlopen(req_eval) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("Status Code: 200")
            print("Keys returned:", list(res_data.keys()))
            print("Trust Verdict:", res_data.get("trust_verdict"))
            print("Trust Score:", res_data.get("trust_score"))
            print("RAG Chunks:", res_data.get("rag_chunks"))
    except Exception as e:
        print("Error calling /api/evaluate:", e)

if __name__ == "__main__":
    test_api()
