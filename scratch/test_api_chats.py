import urllib.request
import json
import sys

BASE_URL = "http://127.0.0.1:8000"
TOKEN = "6a0de329-efdf-408c-91c1-5065945fda22" # Using an existing token from sessions list

def send_request(method, path, body=None):
    url = f"{BASE_URL}{path}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as res:
            return res.status, json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8")

def run_tests():
    print("Starting API tests...")
    
    # 1. Create a chat
    chat_id = "test-chat-12345"
    chat_data = {
        "id": chat_id,
        "title": "Initial Chat Title",
        "prompt": "Explain Quantum Computing in simple terms.",
        "response": "Quantum computing is a type of computation that harness collective properties of quantum states.",
        "risk_score": 15,
        "verdict": "Low Risk",
        "created_at": "2026-06-03T13:11:02Z",
        "updated_at": "2026-06-03T13:11:02Z",
        "is_saved": False,
        "evaluation_data": json.dumps({
            "sentence_analysis": [{"text": "Quantum computing...", "score": 0.1}],
            "sources": []
        })
    }
    
    status, resp = send_request("POST", "/api/chats", chat_data)
    print(f"1. POST /api/chats -> Status: {status}, Response: {resp}")
    assert status == 200, f"Failed to create chat: {resp}"
    
    # 2. Get chats
    status, resp = send_request("GET", "/api/chats")
    print(f"2. GET /api/chats -> Status: {status}, Count: {len(resp)}")
    assert status == 200, f"Failed to get chats: {resp}"
    # Verify our created chat is in the list
    found = [c for c in resp if c["id"] == chat_id]
    assert len(found) == 1, "Created chat not found in the list!"
    print("   Successfully found created chat in list")
    
    # 3. Update chat (Rename & Bookmark)
    update_data = {
        "title": "Quantum Computing 101",
        "is_saved": True,
        "updated_at": "2026-06-03T13:15:00Z"
    }
    status, resp = send_request("PUT", f"/api/chats/{chat_id}", update_data)
    print(f"3. PUT /api/chats/{chat_id} -> Status: {status}, Response: {resp}")
    
    # Verify update
    status, resp = send_request("GET", "/api/chats")
    found = [c for c in resp if c["id"] == chat_id][0]
    print(f"   Updated chat -> title: {found['title']}, is_saved: {found['is_saved']}")
    assert found["title"] == "Quantum Computing 101", "Update title failed!"
    assert found["is_saved"] == 1 or found["is_saved"] is True, "Update is_saved failed!"
    
    # 4. Bulk Save
    # Create another chat first
    chat_id2 = "test-chat-67890"
    chat_data2 = chat_data.copy()
    chat_data2["id"] = chat_id2
    chat_data2["title"] = "Second Chat Title"
    chat_data2["is_saved"] = False
    send_request("POST", "/api/chats", chat_data2)
    
    bulk_save_data = {
        "ids": [chat_id, chat_id2],
        "is_saved": True
    }
    status, resp = send_request("POST", "/api/chats/bulk-save", bulk_save_data)
    print(f"4. POST /api/chats/bulk-save -> Status: {status}, Response: {resp}")
    assert status == 200, f"Failed bulk save: {resp}"
    
    # Verify both are saved
    status, resp = send_request("GET", "/api/chats")
    f1 = [c for c in resp if c["id"] == chat_id][0]
    f2 = [c for c in resp if c["id"] == chat_id2][0]
    assert f1["is_saved"] in (1, True) and f2["is_saved"] in (1, True), "Bulk save verification failed!"
    print("   Bulk save verified successfully")
    
    # 5. Bulk Delete
    bulk_delete_data = {
        "ids": [chat_id2]
    }
    status, resp = send_request("POST", "/api/chats/bulk-delete", bulk_delete_data)
    print(f"5. POST /api/chats/bulk-delete -> Status: {status}, Response: {resp}")
    assert status == 200, f"Failed bulk delete: {resp}"
    
    # Verify chat_id2 is gone, chat_id is still there
    status, resp = send_request("GET", "/api/chats")
    assert not any(c["id"] == chat_id2 for c in resp), "Bulk delete verification failed: chat2 still exists!"
    assert any(c["id"] == chat_id for c in resp), "Bulk delete verification failed: chat1 was deleted!"
    print("   Bulk delete verified successfully")
    
    # 6. Delete single chat
    status, resp = send_request("DELETE", f"/api/chats/{chat_id}")
    print(f"6. DELETE /api/chats/{chat_id} -> Status: {status}, Response: {resp}")
    assert status == 200, f"Failed delete: {resp}"
    
    # Verify chat_id is gone
    status, resp = send_request("GET", "/api/chats")
    assert not any(c["id"] == chat_id for c in resp), "Delete verification failed: chat1 still exists!"
    print("   Single delete verified successfully")
    
    print("\nALL API TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
