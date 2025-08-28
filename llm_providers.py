import requests
import json
import re

def plan_slides_with_llm(provider, api_key, input_text, guidance, add_notes, model=None, max_slides=10):
    system_prompt = """You are a slide planner. Convert text into JSON:
{
  "slides": [
    {"title": "...", "bullets": ["..."], "notes": "..."}
  ]
}"""
    user_prompt = f"""
Text:
{input_text}

Guidance: {guidance}
Add speaker notes: {add_notes}
Max slides: {max_slides}
Return JSON only.
"""

    if provider == "OpenAI":
        url = "https://aipipe.org/openai/v1/chat/completions"
        headers = {"Authorization": f"Bearer {api_key}"}
        data = {
            "model": model or "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2
        }
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"]

    elif provider == "Anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        data = {
            "model": model or "claude-3-5-sonnet-latest",
            "max_tokens": 4096,
            "temperature": 0.2,
            "system": system_prompt,
            "messages": [{"role": "user", "content": user_prompt}]
        }
        resp = requests.post(url, headers=headers, json=data)
        resp.raise_for_status()
        blocks = resp.json()["content"]
        text = "".join([b.get("text","") for b in blocks if b.get("type")=="text"])

    elif provider == "Gemini":
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model or 'gemini-1.5-flash'}:generateContent?key={api_key}"
        data = {
            "contents": [
                {"parts": [{"text": system_prompt}]},
                {"parts": [{"text": user_prompt}]}
            ],
            "generationConfig": {"temperature": 0.2}
        }
        resp = requests.post(url, json=data)
        resp.raise_for_status()
        candidates = resp.json().get("candidates", [])
        text = ""
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            text = "".join([p.get("text","") for p in parts])
    else:
        raise ValueError("Unsupported provider")

    json_match = re.search(r"\{.*\}", text, re.S)
    return json.loads(json_match.group(0)) if json_match else {"slides": []}

def simple_heuristic_plan(text, guidance, max_slides=10):
    import re
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    slides = []
    for i, block in enumerate(blocks[:max_slides]):
        title = block.split("\n")[0][:50]
        bullets = [line.strip("-*• ") for line in block.split("\n")[1:6] if line.strip()]
        if not bullets:
            bullets = [block[:80]]
        slides.append({"title": title, "bullets": bullets})
    return {"slides": slides}
