# backend/services/llm.py

import os
import requests

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")

def generate_answer(context: str, question: str, file_name: str = None, file_type: str = "uploaded data") -> str:
    file_label = f"the {file_type} '{file_name}'" if file_name else f"the {file_type}"

    system_prompt = (
        "You are a smart, helpful AI assistant who collaborates with users like a human data analyst.\n"
        f"You are reviewing data from {file_label}.\n"
        "This file may contain structured or unstructured information — your job is to:\n"
        "- Answer the user’s question accurately\n"
        "- Think critically and provide insight (not just summary)\n"
        "- Offer suggestions, highlight patterns, or raise questions\n"
        "- If the data is about performance, help diagnose causes or offer improvements\n"
        "- Always respond naturally, like a thoughtful teammate (not robotic)\n"
        "- If the question is vague or general, infer the intent using the context\n"
        "- If context is missing something, say so — don’t guess wildly"
    )

    full_prompt = (
        f"{system_prompt}\n\n"
        f"Here is the data context:\n{context}\n\n"
        f"Question:\n{question}"
    )

    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.RequestException as e:
        print("Ollama API Error:", str(e))
        raise RuntimeError(f"Ollama API request failed: {str(e)}")
