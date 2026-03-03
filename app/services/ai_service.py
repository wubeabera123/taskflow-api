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
        "model": "gemma3:4b",  # since your UI shows this installed
        "prompt": system_prompt + "\nUser request:\n" + prompt,
        "stream": False
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(OLLAMA_URL, json=payload)

    result = response.json()

    return result["response"]