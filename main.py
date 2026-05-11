import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN

from handlers.start import router

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    dp.include_router(router)

    print("Bot started...")

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
