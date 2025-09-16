import httpx
from fastapi import HTTPException
from tenacity import retry, stop_after_attempt, wait_fixed
from logging_config import setup_logger
import os

logger = setup_logger("order_service")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
async def validate_current_user(token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{USER_SERVICE_URL}/verify-token", headers=headers)
            response.raise_for_status()
            logger.info("User validated", extra={"token": token[:10] + "..."})
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error("User validation failed", extra={"token": token[:10] + "...", "error": str(e)})
            raise HTTPException(status_code=401, detail="Invalid token")

