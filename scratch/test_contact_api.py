import unittest
import sqlite3
import time
import os
import requests

# We assume the FastAPI app is running on localhost:8000
BASE_URL = "http://127.0.0.1:8000"
DB_PATH = "truthlens.db"

class TestContactAPI(unittest.TestCase):
    def test_01_validation_errors(self):
        print("\n--- Test 1: Validation Errors ---")
        
        # Test empty names
        payload = {
            "first_name": "",
            "last_name": "Doe",
            "email": "test@example.com",
            "inquiry_type": "support",
            "message": "This is a valid message that is longer than 10 characters.",
            "honeypot": ""
        }
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Empty first name response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 400)
        self.assertIn("required", res.json()["detail"].lower())

        # Test invalid email format
        payload["first_name"] = "John"
        payload["email"] = "invalid-email"
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Invalid email format response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 400)
        self.assertIn("email", res.json()["detail"].lower())

        # Test short message
        payload["email"] = "john@example.com"
        payload["message"] = "Short"
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Short message response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 400)
        self.assertIn("characters", res.json()["detail"].lower())

    def test_02_honeypot(self):
        print("\n--- Test 2: Honeypot ---")
        payload = {
            "first_name": "Bot",
            "last_name": "Spammer",
            "email": "bot@spammer.com",
            "inquiry_type": "partners",
            "message": "I am a bot sending spam messages.",
            "honeypot": "iamabot"
        }
        # Clear rate limit state by using a new mock request or just testing
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Honeypot response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")

        # Verify that honeypot submission was NOT inserted into database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM contact_submissions WHERE email = 'bot@spammer.com'")
        rows = cursor.fetchall()
        conn.close()
        print("DB Rows for bot@spammer.com (should be empty):", rows)
        self.assertEqual(len(rows), 0)

    def test_03_successful_submission(self):
        print("\n--- Test 3: Successful Submission ---")
        # Ensure we use a unique email to check the DB insert
        test_email = f"test_{int(time.time())}@example.com"
        payload = {
            "first_name": "Alice",
            "last_name": "Smith",
            "email": test_email,
            "inquiry_type": "enterprise",
            "message": "This is a legitimate inquiry from a potential enterprise customer.",
            "honeypot": ""
        }
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Successful submission response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "success")
        self.assertIn("sent successfully", res.json()["message"].lower())

        # Verify database entry
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT first_name, last_name, email, inquiry_type, message FROM contact_submissions WHERE email = ?", (test_email,))
        row = cursor.fetchone()
        conn.close()
        print("DB Row retrieved:", row)
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "Alice")
        self.assertEqual(row[1], "Smith")
        self.assertEqual(row[2], test_email)
        self.assertEqual(row[3], "enterprise")
        self.assertEqual(row[4], "This is a legitimate inquiry from a potential enterprise customer.")

    def test_04_rate_limiting(self):
        print("\n--- Test 4: Rate Limiting ---")
        # Since we just submitted in test_03, submitting again with the same client IP should trigger 429
        # (Assuming the API runs locally and client IP is 127.0.0.1)
        payload = {
            "first_name": "Bob",
            "last_name": "Jones",
            "email": "bob@example.com",
            "inquiry_type": "support",
            "message": "This is another message to trigger rate limiting.",
            "honeypot": ""
        }
        res = requests.post(f"{BASE_URL}/api/contact", json=payload)
        print("Rate limit response:", res.status_code, res.json())
        self.assertEqual(res.status_code, 429)
        self.assertIn("rate limit exceeded", res.json()["detail"].lower())

if __name__ == "__main__":
    unittest.main()
