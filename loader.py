import asyncio
import os
import aioschedule

from adm_main import check_count_msg, logger
from My_sklad import update, data_loader, img_loader, img_count
from aiogram import Bot, Dispatcher
from midlware.isadmin import check_id

from dotenv import find_dotenv,load_dotenv
load_dotenv(find_dotenv())

from handlers.adm_panel import adm_panel_router

async def checker(step):
    check_update = 0
    while check_update == 0:
        await asyncio.sleep(10)
        check_update = await step

async def updated():
    await checker(update())
    await logger('update')

    await checker(data_loader())
    await logger('data_loader')

    await checker(img_loader())
    await logger('img_loader')

    await checker(img_count())
    await logger('img_count')

    await asyncio.sleep(3)
    await check_count_msg()
    await logger('check_count_msg')


async def timer():
    aioschedule.every().day.at("01:00").do(updated)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def start():
    asyncio.create_task(timer())

ALOW_UPD = ['message, edit_message']
ALLOWED_USER_ID = 1318370854

bot = Bot(token=os.getenv('LOADERTOKEN'))
dp = Dispatcher()
dp.message.middleware(check_id())
dp.include_router(adm_panel_router)



async def main():
    await start()
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=ALOW_UPD)

asyncio.run(main())