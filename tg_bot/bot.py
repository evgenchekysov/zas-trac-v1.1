import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Твой токен из BotFather
TOKEN = "_______________"

# Настройка логирования, чтобы видеть ошибки в терминале
logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Обработка команды /start
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    await message.answer(
        f"✅ Бот системы эксплуатации запущен!\n\n"
        f"Твой Telegram ID: `{user_id}`\n"
        f"Скопируй это число и пришли мне в чат."
    )

async def main():
    print("--- Бот запущен и слушает команды ---")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
