import unittest
import requests
import json

class TestTruthLensDynamicQueries(unittest.TestCase):
    BASE_URL = "http://127.0.0.1:8000"

    @classmethod
    def setUpClass(cls):
        # Register and login to obtain auth header
        cls.headers = {}
        register_data = {
            "email": "dynamic_test_user@truthlens.ai",
            "password": "testpassword123",
            "name": "Dynamic Test User"
        }
        try:
            resp = requests.post(f"{cls.BASE_URL}/api/register", json=register_data, timeout=10)
            res_json = resp.json()
            if res_json.get("status") == "success":
                token = res_json.get("token")
                cls.headers = {"Authorization": f"Bearer {token}"}
            else:
                # Try logging in
                resp = requests.post(f"{cls.BASE_URL}/api/login", json=register_data, timeout=10)
                res_json = resp.json()
                if res_json.get("status") == "success":
                    token = res_json.get("token")
                    cls.headers = {"Authorization": f"Bearer {token}"}
        except Exception as e:
            print("[Warning] Auth setup failed, tests will run unauthenticated:", e)

    def test_1_who_won_ipl_2026(self):
        print("\n--- Running Test: who won IPL 2026 ---")
        payload = {
            "prompt": "who won IPL 2026",
            "model": "llama",
            "evaluate": True
        }
        resp = requests.post(f"{self.BASE_URL}/api/generate", json=payload, headers=self.headers, timeout=90)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        print("Model Output:", data.get("generated_response"))
        # Ensure it doesn't return hallucinations like 'Tata Cricket Corporation'
        response_text = data.get("generated_response", "").lower()
        self.assertNotIn("tata cricket corporation", response_text)
        
    def test_2_who_received_ipl_title_2026(self):
        print("\n--- Running Test: who received IPL title 2026 ---")
        payload = {
            "prompt": "who received IPL title 2026",
            "model": "llama",
            "evaluate": True
        }
        resp = requests.post(f"{self.BASE_URL}/api/generate", json=payload, headers=self.headers, timeout=90)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        print("Model Output:", data.get("generated_response"))
        response_text = data.get("generated_response", "").lower()
        self.assertNotIn("tata cricket corporation", response_text)

    def test_3_current_president_of_usa(self):
        print("\n--- Running Test: current president of USA ---")
        payload = {
            "prompt": "current president of USA",
            "model": "llama",
            "evaluate": True
        }
        resp = requests.post(f"{self.BASE_URL}/api/generate", json=payload, headers=self.headers, timeout=90)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        print("Model Output:", data.get("generated_response"))
        self.assertTrue(len(data.get("generated_response", "")) > 0)

    def test_4_current_prime_minister_of_india(self):
        print("\n--- Running Test: current prime minister of India ---")
        payload = {
            "prompt": "current prime minister of India",
            "model": "llama",
            "evaluate": True
        }
        resp = requests.post(f"{self.BASE_URL}/api/generate", json=payload, headers=self.headers, timeout=90)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        print("Model Output:", data.get("generated_response"))
        self.assertTrue(len(data.get("generated_response", "")) > 0)

    def test_5_founder_of_whatsapp(self):
        print("\n--- Running Test: founder of WhatsApp ---")
        payload = {
            "prompt": "founder of WhatsApp",
            "model": "llama",
            "evaluate": True
        }
        resp = requests.post(f"{self.BASE_URL}/api/generate", json=payload, headers=self.headers, timeout=90)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        print("Model Output:", data.get("generated_response"))
        self.assertTrue(len(data.get("generated_response", "")) > 0)

if __name__ == "__main__":
    unittest.main()
