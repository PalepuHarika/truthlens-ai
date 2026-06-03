import sys
import os
import unittest
from fastapi.testclient import TestClient

# Add workspace directory to python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import app, is_valid_generated_response
from src.evaluator import is_dynamic_fact_query

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # Register a test user to get a token
        self.email = "test_user_pipeline@truthlens.ai"
        self.password = "password123"
        self.name = "Pipeline Tester"
        
        resp = self.client.post("/api/register", json={
            "email": self.email,
            "password": self.password,
            "name": self.name
        })
        data = resp.json()
        if data.get("status") == "success":
            self.token = data.get("token")
        else:
            resp = self.client.post("/api/login", json={
                "email": self.email,
                "password": self.password
            })
            self.token = resp.json().get("token")
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_dynamic_query_classification(self):
        # Verify classification works as expected
        self.assertTrue(is_dynamic_fact_query("Who is the current President of India?"))
        self.assertTrue(is_dynamic_fact_query("who won IPL 2026"))

    def test_invalid_response_detection(self):
        # Verify invalid responses are correctly detected
        self.assertFalse(is_valid_generated_response("unable to generate a response"))
        self.assertFalse(is_valid_generated_response("Unable to generate response."))
        self.assertFalse(is_valid_generated_response("Knowledge source unavailable. Please try again."))
        self.assertFalse(is_valid_generated_response("Unable to verify this claim with available evidence."))
        self.assertTrue(is_valid_generated_response("Droupadi Murmu is the President of India."))

    def test_factual_query_success_flow(self):
        # We test a factual query. Let's see what is returned.
        payload = {
            "prompt": "Who is the current President of India?",
            "model": "llama",
            "evaluate": True
        }
        resp = self.client.post("/api/generate", json=payload, headers=self.headers)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        
        print("\n--- Factual Query Success Flow Output ---")
        print("Status:", data.get("status"))
        print("Generated Response:", data.get("generated_response"))
        print("Model:", data.get("model"))
        print("Context Char Count:", len(data.get("context", "")))
        print("Evaluation Available:", data.get("evaluation") is not None)
        
        # If it was successful, ensure status is either success or Verified/Contradicted
        if data.get("status") != "error":
            self.assertIsNotNone(data.get("evaluation"))
            # Make sure "Unable to generate a response" is not displayed as verified answer
            self.assertNotEqual(data.get("generated_response"), "Unable to generate a response")

    def test_failed_generation_flow(self):
        # We will mock the llm pipeline to return an invalid response
        from unittest.mock import patch
        
        # We mock app.state.llm_pipeline inside main
        # But wait, run_generation also calls llama3_generate, so we can mock both or just llama3_generate to return invalid response
        with patch("src.main.llama3_generate") as mock_llama:
            # Force llama3_generate to return invalid keyword response
            mock_llama.return_value = "unable to generate response"
            
            payload = {
                "prompt": "Who is the current President of India?",
                "model": "llama",
                "evaluate": True
            }
            resp = self.client.post("/api/generate", json=payload, headers=self.headers)
            self.assertEqual(resp.status_code, 200)
            data = resp.json()
            
            print("\n--- Factual Query Failed Flow Output ---")
            print("Status:", data.get("status"))
            print("Generated Response:", data.get("generated_response"))
            print("Evaluation Available:", data.get("evaluation") is not None)
            
            # Verify status is error
            self.assertEqual(data.get("status"), "error")
            # Verify response is "Knowledge source unavailable. Please try again."
            self.assertEqual(data.get("generated_response"), "Knowledge source unavailable. Please try again.")
            # Verify evaluation is None (hallucination score not calculated)
            self.assertIsNone(data.get("evaluation"))

if __name__ == "__main__":
    unittest.main()
