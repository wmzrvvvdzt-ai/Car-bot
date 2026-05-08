import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

# 📊 тестовые данные (потом заменим на парсинг)
cars = [
    {
        "model": "BMW 3 Series 2018",
        "price": 1650000,
        "market": 2000000,
        "link": "https://example.com"
    },
    {
        "model": "Toyota Camry 2019",
        "price": 1800000,
        "market": 2000000,
        "link": "https://example.com"
    },
    {
        "model": "Audi A4 2017",
        "price": 1350000,
        "market": 1700000,
        "link": "https://example.com"
    }
]

def is_good_deal(car):
    return (car["market"] - car["price"]) / car["market"] >= 0.1


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("🚗 Бот запущен! Ищу выгодные авто...")

    text = "🔥 Лучшие предложения:\n\n"

    found = False

    for car in cars:
        if is_good_deal(car):
            found = True
            discount = int((car["market"] - car["price"]) / car["market"] * 100)

            text += (
                f"🚘 {car['model']}\n"
                f"💰 Цена: {car['price']} ₽\n"
                f"📊 Рынок: {car['market']} ₽\n"
                f"📉 -{discount}% ниже рынка\n"
                f"🔗 {car['link']}\n\n"
            )

    if not found:
        text = "❌ Сейчас выгодных предложений нет"

    await message.answer(text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
