import requests

OLLAMA_URL = "http://localhost:11434"

def generate(model: str, prompt: str):
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    return response.json()["response"]

OLLAMA_URL = "http://localhost:11434"

def embed(text: str, model: str = "nomic-embed-text"):
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": model,
            "prompt": text
        },
        timeout=60
    )

    response.raise_for_status()

    data = response.json()

    if "embedding" not in data:
        raise ValueError(f"Invalid embedding response: {data}")

    return data["embedding"]