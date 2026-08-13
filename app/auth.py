import os
from fastapi import Header, HTTPException

EXPECTED_TOKEN = os.getenv("API_BEARER_TOKEN")


def verify_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not EXPECTED_TOKEN or token != EXPECTED_TOKEN:
        raise HTTPException(status_code=401, detail="Invalid token")
    return True
