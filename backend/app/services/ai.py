from __future__ import annotations

from dataclasses import dataclass

import httpx

from ..settings import settings


@dataclass
class AiResult:
    mode: str  # "online" | "offline"
    answer: str


def _has_key() -> bool:
    return bool(settings.openai_api_key and settings.openai_api_key.strip())


async def chat_online(system_prompt: str, user_prompt: str) -> str:
    """
    Uses an OpenAI-compatible Chat Completions endpoint.
    """
    url = settings.openai_base_url.rstrip("/") + "/chat/completions"
    headers = {"Authorization": f"Bearer {settings.openai_api_key}"}
    payload = {
        "model": settings.openai_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
    }

    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(url, headers=headers, json=payload)
        r.raise_for_status()
        data = r.json()

    return (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()


def offline_answer(question: str, context: str) -> str:
    q = question.lower()
    lines: list[str] = []
    lines.append("Offline mode (no AI key). Here is a structured summary from your data:\n")
    lines.append(context)

    if any(k in q for k in ["budget", "variance", "over", "under", "cost"]):
        lines.append(
            "\nSuggested checks:\n"
            "- Compare top cost heads vs budget (steel, cement/RMC, machinery, labour)\n"
            "- Verify high-value bills and payment mode for cash flow\n"
            "- Confirm quantities logged for pile boring/concreting match bills"
        )
    if any(k in q for k in ["dpr", "daily", "progress", "today"]):
        lines.append(
            "\nDPR format tip:\n"
            "- Mention location/chainage, activity, quantity, manpower, machinery, and constraints."
        )

    return "\n".join(lines).strip()


async def answer(question: str, context: str) -> AiResult:
    system_prompt = (
        "You are a construction planning and controls assistant for PWD/Indian Railways/MSRDC projects. "
        "You help create DPR summaries, highlight risks, and explain cost/budget variance. "
        "Be concise, use bullet points, and use site-appropriate terms (pile, pier, abutment, girder, deck slab)."
    )
    user_prompt = f"Question:\n{question}\n\nProject context (data extract):\n{context}"

    if not _has_key():
        return AiResult(mode="offline", answer=offline_answer(question, context))

    try:
        content = await chat_online(system_prompt, user_prompt)
        if not content:
            return AiResult(mode="offline", answer=offline_answer(question, context))
        return AiResult(mode="online", answer=content)
    except Exception:
        return AiResult(mode="offline", answer=offline_answer(question, context))

