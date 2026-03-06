import httpx
import json
import re

OLLAMA_URL = "http://host.docker.internal:11434/api/generate"


async def generate_tasks_from_prompt(prompt: str):
    """
    Sends prompt to Ollama and returns structured task data.
    """

    system_prompt = """
You are a productivity assistant.

Generate clear actionable tasks from the user request.

Return ONLY valid JSON in this format:

[
  {
    "title": "Task title",
    "description": "Task description",
    "priority": "low"
  }
]

Rules:
- Do NOT include markdown
- Do NOT include explanations
- Only return JSON
"""

    payload = {
        "model": "gemma:2b",
        "prompt": f"{system_prompt}\nUser request:\n{prompt}",
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

        ai_text = result["response"]

        # Remove markdown code blocks if model adds them
        ai_text = re.sub(r"```json", "", ai_text)
        ai_text = re.sub(r"```", "", ai_text).strip()

        # Convert string -> JSON
        tasks = json.loads(ai_text)

        # Ensure list format
        if isinstance(tasks, dict):
            tasks = [tasks]

        return tasks

    except json.JSONDecodeError:
        raise Exception("AI returned invalid JSON format")

    except httpx.RequestError as e:
        raise Exception(f"Ollama connection error: {str(e)}")

    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")