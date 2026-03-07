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

        if not isinstance(tasks, list):
            raise Exception("AI did not return a valid task list")

        # ✅ LIMIT AI OUTPUT (important for safety)
        tasks = tasks[:5]

        return tasks

    except json.JSONDecodeError:
        raise Exception("AI returned invalid JSON format")

    except httpx.RequestError as e:
        raise Exception(f"Ollama connection error: {str(e)}")

    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")
    

async def generate_task_breakdown(task: str):
    """
    Break a large task into smaller actionable subtasks using AI.
    """

    system_prompt = """
You are a productivity assistant.

Break the user task into smaller actionable subtasks.

Return ONLY valid JSON in this format:

[
  "Subtask 1",
  "Subtask 2",
  "Subtask 3"
]

Rules:
- Maximum 7 subtasks
- Each subtask must be clear and actionable
- Do NOT include explanations
- Do NOT include markdown
- Only return JSON
"""

    payload = {
        "model": "gemma:2b",
        "prompt": f"{system_prompt}\nUser task:\n{task}",
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)

        response.raise_for_status()
        result = response.json()

        if "response" not in result:
            raise Exception(f"Unexpected Ollama response: {result}")

        ai_text = result["response"]

        # Remove markdown
        ai_text = re.sub(r"```json", "", ai_text)
        ai_text = re.sub(r"```", "", ai_text).strip()

        print("RAW AI TEXT:", ai_text)

        # --------------------------------
        # 1️⃣ Try normal JSON parsing
        # --------------------------------
        try:
            parsed = json.loads(ai_text)

            if isinstance(parsed, list):
                return parsed[:7]

            if isinstance(parsed, dict):
                return list(parsed.values())[:7]

        except json.JSONDecodeError:
            pass

        # --------------------------------
        # 2️⃣ Extract values from dictionary text
        # --------------------------------
        matches = re.findall(r':\s*"([^"]+)"', ai_text)

        if matches:
            return matches[:7]

        # --------------------------------
        # 3️⃣ Extract numbered list
        # --------------------------------
        matches = re.findall(r'\d+\.\s*(.*)', ai_text)

        if matches:
            return matches[:7]

        raise Exception("AI returned invalid subtask format")

    except httpx.RequestError as e:
        raise Exception(f"Ollama connection error: {str(e)}")

    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")
    
async def prioritize_tasks(tasks: list[str]):
    """
    Use AI to assign priority to tasks.
    """

    system_prompt = """
You are a productivity assistant.

Assign a priority level to each task.

Priority options:
- high
- medium
- low

Return ONLY valid JSON in this format:

{
  "tasks": [
    {"task": "Task name", "priority": "high"},
    {"task": "Task name", "priority": "medium"}
  ]
}

Rules:
- Do NOT include explanations
- Do NOT include markdown
- Only return JSON
"""

    task_list = "\n".join(tasks)

    payload = {
        "model": "gemma:2b",
        "prompt": f"{system_prompt}\nTasks:\n{task_list}",
        "stream": False,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(OLLAMA_URL, json=payload)

        response.raise_for_status()
        result = response.json()

        if "response" not in result:
            raise Exception(f"Unexpected Ollama response: {result}")

        ai_text = result["response"]

        # Clean markdown
        ai_text = re.sub(r"```json", "", ai_text)
        ai_text = re.sub(r"```", "", ai_text).strip()

        parsed = json.loads(ai_text)

        if isinstance(parsed, dict) and "tasks" in parsed:
            return parsed["tasks"]

        raise Exception("Invalid AI priority response")

    except Exception as e:
        raise Exception(f"AI service error: {str(e)}")