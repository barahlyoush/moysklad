import asyncio
import os

from aiogram import Bot, Dispatcher
from midlware.isadmin import check_status
from dotenv import find_dotenv,load_dotenv
load_dotenv(find_dotenv())

from handlers.usr_prvt import usr_prvt_router

ALOW_UPD = ['message, edit_message']

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()
dp.message.middleware(check_status())
dp.include_router(usr_prvt_router)


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALOW_UPD)

asyncio.run(main())