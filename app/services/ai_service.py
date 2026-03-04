import httpx
import json

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"

async def generate_tasks_from_prompt(prompt: str):

    system_prompt = """
    You are a productivity assistant.
    Generate clear actionable tasks.
    Return ONLY valid JSON in this format:

    [
      { "title": "...", "description": "...", "priority": "low|medium|high" }
    ]
    """

    payload = {
        "model": "gemma:2b",
        "prompt": system_prompt + "\nUser request:\n" + prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)

        response.raise_for_status()

        result = response.json()

        print("OLLAMA RAW RESPONSE:", result)

        if "response" not in result:
            raise Exception(f"Unexpected Ollama response: {result}")

        return result["response"]

    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")