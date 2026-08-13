import os
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/journal", tags=["journal"])


class JournalEntry(BaseModel):
    content: str


@router.post("")
async def submit_journal(entry: JournalEntry):
    if not entry.content.strip():
        raise HTTPException(status_code=400, detail="Journal entry is empty")

    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        raise HTTPException(
            status_code=500,
            detail="Telegram configuration missing"
        )

    message = f"📔 NEW JOURNAL ENTRY\n\n{entry.content.strip()}"

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"

    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={
                "chat_id": chat_id,
                "text": message
            }
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=502,
            detail="Failed to send journal to Telegram"
        )

    return {
        "success": True,
        "message": "Journal entry sent"
    }
