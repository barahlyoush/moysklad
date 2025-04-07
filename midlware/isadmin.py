from typing import Callable, Awaitable, Dict, Any
import json
import main
import asyncio
from aiogram.methods import SendMessage

from aiogram import BaseMiddleware
from aiogram.types import Message

adm_list = {}

class check_id(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str,Any]], Awaitable[Any]], event: Message, data: Dict[str,Any]) -> Any:
        id = event.from_user.id
        if id not in adm_list:
            await event.answer('Данный бот доступен только администраторам')
        else:
            return await handler(event,data)

class check_status(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str,Any]], Awaitable[Any]], event: Message, data: Dict[str,Any]) -> Any:
        id = event.from_user.id
        user = str(id)
        with open('data/user_data.JSON', 'r') as file:
            user_data = json.load(file)
        if user in user_data:
            if 'status' in user_data[user]:
                if user_data[user].get('status') == 1:
                    return await handler(event,data)
                if user_data[user].get('status') == 0:
                    await asyncio.sleep(2)
                    await main.user_data_upd(event.from_user.id, 'status', 1)
                    return SendMessage(chat_id=event.chat.id, text='Слишком частая отправка сообщений')

            else:
                return await handler(event,data)
        else:
            return await handler(event, data)


