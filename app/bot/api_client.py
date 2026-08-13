import os
import httpx

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("API_BEARER_TOKEN")
HEADERS = {"Authorization": f"Bearer {TOKEN}"}


async def get(path: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_BASE}{path}", headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()


async def post(path: str, json: dict) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{API_BASE}{path}", headers=HEADERS, json=json, timeout=15)
        r.raise_for_status()
        return r.json()


async def patch(path: str) -> dict:
    async with httpx.AsyncClient() as client:
        r = await client.patch(f"{API_BASE}{path}", headers=HEADERS, timeout=15)
        r.raise_for_status()
        return r.json()
