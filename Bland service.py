import httpx
from config import settings

HEADERS = {
    "authorization": settings.BLAND_AI_API_KEY,
    "Content-Type": "application/json",
}


async def initiate_call(
    phone_number: str,
    task: str,
    first_sentence: str = "",
    voice: str = "maya",
    max_duration: int = 12,
    record: bool = True,
) -> dict:
    """Initiate an AI phone call via Bland AI."""
    payload = {
        "phone_number": phone_number,
        "task": task,
        "voice": voice,
        "record": record,
        "max_duration": max_duration,
        "wait_for_response": False,
        "language": "en-US",
        "model": "enhanced",
        "interruption_threshold": 100,
    }
    if first_sentence:
        payload["first_sentence"] = first_sentence

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.BLAND_AI_BASE_URL}/calls",
            headers=HEADERS,
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def get_call_details(call_id: str) -> dict:
    """Fetch details + transcript for a completed call."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{settings.BLAND_AI_BASE_URL}/calls/{call_id}",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


async def list_calls(page: int = 0, limit: int = 50) -> dict:
    """List all Bland AI calls."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{settings.BLAND_AI_BASE_URL}/calls",
            headers=HEADERS,
            params={"page": page, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()


async def stop_call(call_id: str) -> dict:
    """Stop an active call."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{settings.BLAND_AI_BASE_URL}/calls/{call_id}/stop",
            headers=HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


async def get_recording(call_id: str) -> str | None:
    """Return the recording URL for a completed call."""
    data = await get_call_details(call_id)
    return data.get("recording_url")
