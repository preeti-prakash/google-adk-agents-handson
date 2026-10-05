import requests

response = requests.post(
    "http://localhost:11434/api/chat",
    json={
        "model": "gemma3",
        "messages": [
            {
                "role": "user",
                "content": "What is RAG?"
            }
        ],
        "stream": False
    }
)

print(response.json())
