import urllib.request
import ssl
import json
import time

url = "https://router.huggingface.co/hf-inference/v1/chat/completions"
import os
token = os.getenv("HF_TOKEN", "")

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

payload = {
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "messages": [
        {"role": "user", "content": "hi"}
    ]
}

data = json.dumps(payload).encode("utf-8")
req = urllib.request.Request(url, data=data, headers=headers, method="POST")
ctx = ssl._create_unverified_context()

start = time.time()
try:
    with urllib.request.urlopen(req, context=ctx, timeout=5) as resp:
        print("Success:", resp.read())
except Exception as e:
    print("Error:", e)
print("Time taken:", time.time() - start)
