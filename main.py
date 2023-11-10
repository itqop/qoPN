import yaml
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from handlers import router, update_data_periodically

async def main():
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    update_used = asyncio.create_task(update_data_periodically())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    await update_used



if __name__ == "__main__":
    with open('keys.yml', 'r') as file:
        data = yaml.safe_load(file)
        BOT_TOKEN = data['tg_api_key']
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

    
    
    