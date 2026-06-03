import os
from dotenv import load_dotenv
load_dotenv()
from groq import Groq
import json

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", None)

def extract_facts(prompt: str, response: str, context: str) -> tuple:
    generated_fact = response.strip()
    verified_fact = context.strip()
    
    if not context or len(context.strip()) < 5:
        return generated_fact, ""

    if GROQ_API_KEY:
        try:
            client = Groq(api_key=GROQ_API_KEY)
            system_prompt = (
                "You are a fact extraction and comparison assistant.\n"
                "Analyze the user's query, the generated response, and the verified context.\n"
                "Identify the core dynamic entity/fact being asked about (e.g. current president, PM, date, news, score, etc.).\n"
                "Extract the value of this fact as asserted by the generated response (this is 'generated_fact').\n"
                "Extract the value of this fact as verified by the context (this is 'verified_fact').\n"
                "Normalize both facts so they can be compared directly:\n"
                "- For names, use standard full name (e.g., 'Joe Biden').\n"
                "- For dates, use standard format or just the main event date.\n"
                "- If the generated response and verified context refer to the SAME entity/fact/value, you MUST make both 'generated_fact' and 'verified_fact' EXACTLY IDENTICAL strings.\n"
                "- If they differ, output the actual differing values.\n"
                "Return a JSON object with exactly two keys: 'generated_fact' and 'verified_fact'. E.g.\n"
                "{\"generated_fact\": \"Narendra Modi\", \"verified_fact\": \"Narendra Modi\"}"
            )
            
            user_msg = (
                f"Query: {prompt}\n"
                f"Generated Response: {response}\n"
                f"Verified Context: {context}\n"
            )
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_msg}
                ],
                temperature=0.0,
                max_tokens=150,
                response_format={"type": "json_object"}
            )
            
            data = json.loads(completion.choices[0].message.content.strip())
            g_fact = data.get("generated_fact", "").strip()
            v_fact = data.get("verified_fact", "").strip()
            if g_fact or v_fact:
                return g_fact, v_fact
        except Exception as e:
            print(f"[Error] {e}")
            
    return generated_fact, verified_fact

# Test cases
tests = [
    {
        "prompt": "Who is the Prime Minister of India?",
        "response": "The Prime Minister of India is Rahul Gandhi.",
        "context": "Narendra Modi is the Prime Minister of India since 2014."
    },
    {
        "prompt": "Who is the Prime Minister of India?",
        "response": "The current PM is Narendra Modi.",
        "context": "Narendra Modi is the Prime Minister of India since 2014."
    }
]

for t in tests:
    g, v = extract_facts(t["prompt"], t["response"], t["context"])
    print(f"Prompt: {t['prompt']}")
    print(f"Response: {t['response']}")
    print(f"Context: {t['context']}")
    print(f"Generated Fact: {g} | Verified Fact: {v}")
    print(f"Match: {g == v}")
    print("-" * 40)
