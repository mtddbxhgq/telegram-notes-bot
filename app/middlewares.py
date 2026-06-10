import logging
import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message


logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, limit_seconds: int = 3) -> None:
        self.limit_seconds = limit_seconds
        self.users_last_message: Dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if event.from_user is None:
            return await handler(event, data)

        user_id = event.from_user.id
        now = time.time()
        last_message_time = self.users_last_message[user_id]

        if now - last_message_time < self.limit_seconds:
            logger.warning(
                "Rate limit triggered | user_id=%s | username=%s",
                user_id,
                event.from_user.username,
            )

            await event.answer(
                "Too many requests. Please wait a few seconds and try again."
            )
            return None

        self.users_last_message[user_id] = now
        return await handler(event, data)