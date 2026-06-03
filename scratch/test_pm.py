import sys
import os
sys.path.append(os.getcwd())

from src.main import llama3_generate, GROQ_API_KEY
import urllib.request
import json

print("GROQ API KEY exists:", bool(GROQ_API_KEY))

# Test with no context
res_no_context = llama3_generate("Who is the Prime Minister of India?", "")
print("No Context Response:", res_no_context)

# Simulating context that defines what a Prime Minister is
context = "The Prime Minister of India is the leader of the executive branch of the Government of India. The Prime Minister is the chief adviser to the President of India and the head of the Union Council of Ministers."
res_with_context = llama3_generate("Who is the Prime Minister of India?", context)
print("With Context Response:", res_with_context)
