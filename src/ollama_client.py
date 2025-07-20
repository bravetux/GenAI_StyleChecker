import requests
import json

class OllamaClient:
    def __init__(self, api_key=None):
        # Local Ollama API endpoint
        self.base_url = "http://localhost:11434/api"

    def send_request(self, prompt, model):
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)
            result = ""
            for line in response.iter_lines():
                if line:
                    data = json.loads(line.decode('utf-8'))
                    if "response" in data:
                        result += data["response"]
            return result
        except Exception as e:
            return ""