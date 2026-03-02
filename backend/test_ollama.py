"""
Quick test to verify Ollama is running and the configured model works.
Run from the backend directory with the venv active:
    python test_ollama.py
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = "http://localhost:11434"
model = os.environ.get("OLLAMA_MODEL", "llama3.2")

print("=== Ollama Connection Test ===\n")
print(f"Model from .env: {model}\n")

# 1. Check Ollama is reachable
print("Checking Ollama is running...")
try:
    r = httpx.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5.0)
    r.raise_for_status()
    print("OK    Ollama is running\n")
except httpx.ConnectError:
    print("FAIL  Could not connect to Ollama at localhost:11434")
    print("      Run: ollama serve")
    exit(1)
except Exception as e:
    print(f"FAIL  {e}")
    exit(1)

# 2. Check the configured model is available
print("Checking model is available...")
available = [m["name"] for m in r.json().get("models", [])]
if not available:
    print("FAIL  No models found. Pull one with: ollama pull <model-name>")
    exit(1)

match = next((m for m in available if m.startswith(model.split(":")[0])), None)
if not match:
    print(f"FAIL  Model '{model}' not found.")
    print(f"      Available models: {', '.join(available)}")
    print(f"      Update OLLAMA_MODEL in .env to one of the above.")
    exit(1)

print(f"OK    Model found: {match}\n")

# 3. Send a small test prompt
print("Sending test prompt...")
try:
    resp = httpx.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": 'Say exactly: hello',
            "stream": False,
        },
        timeout=120.0,
    )
    resp.raise_for_status()
    raw = resp.json().get("response", "").strip()
    if raw:
        print(f"OK    Model responded: \"{raw[:80]}\"\n")
    else:
        print("FAIL  Model returned an empty response.")
        exit(1)
except httpx.ReadTimeout:
    print("FAIL  Model timed out. It may still be loading — try again in a moment.")
    exit(1)
except Exception as e:
    print(f"FAIL  {e}")
    exit(1)

print("=== All checks passed. Ollama is ready. ===")
