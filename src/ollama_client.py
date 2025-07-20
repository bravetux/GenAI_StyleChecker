import requests
import json

class OllamaClient:
    def __init__(self, api_key=None):
        # Local Ollama API endpoint. This is the URL that the Ollama
        # API is listening on. The Ollama API is a local service that
        # runs on the user's machine, and it is responsible for
        # generating code based on human instructions. The API is
        # accessed via HTTP requests to the above URL.
        self.base_url = "http://localhost:11434/api"

    def send_request(self, prompt, model):
        """
        Send a request to the Ollama API to generate code based on a human instruction
        and a code model.

        Args:
            prompt (str): A human instruction that describes the code to be generated.
            model (str): The name of the code model to use to generate the code.

        Returns:
            str: The generated code as a string.
        """

        # The URL of the Ollama API endpoint.
        url = "http://localhost:11434/api/generate"

        # The data to send in the request body.
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True
        }

        # Make the request.
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120)

            # Initialize the result to an empty string.
            result = ""

            # Iterate over the lines of the response. The response is a stream of
            # JSON objects, where each object contains a single line of generated
            # code.
            for line in response.iter_lines():
                if line:
                    # Decode the line from bytes to a string and parse it as JSON.
                    data = json.loads(line.decode('utf-8'))

                    # If the line contains a "response" key, then it contains
                    # generated code. Append that code to the result.
                    if "response" in data:
                        result += data["response"]

            # Return the generated code.
            return result

        # If any exception occurs during the request, return an empty string.
        except Exception as e:
            return ""
