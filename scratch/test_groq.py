import sys
import os

# Set PYTHONPATH to root directory to allow src imports
sys.path.append(os.getcwd())

from src.main import llama3_generate, GROQ_API_KEY

print("GROQ_API_KEY:", GROQ_API_KEY)
ans = llama3_generate("What is 2+2?", "")
print("Response:", ans)
