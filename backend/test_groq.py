import os
from groq import Groq

client = Groq(api_key=os.getenv("GROQ_API_KEY", ""))

# Try current models
models_to_try = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant"]

for model in models_to_try:
    try:
        chat = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say hello in one sentence."}],
            model=model,
            max_tokens=50
        )
        print(f"SUCCESS with model: {model}")
        print(f"Response: {chat.choices[0].message.content}")
        print()
    except Exception as e:
        print(f"FAILED {model}: {e}\n")
