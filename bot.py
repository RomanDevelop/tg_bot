import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from dotenv import load_dotenv
from aiogram.exceptions import TelegramNetworkError  # ✅ Исправленный импорт

# Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")

if not TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env!")
if not TARGET_CHANNEL_ID:
    raise ValueError("❌ Ошибка: TARGET_CHANNEL_ID не найден в .env!")

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)

# 🔹 Каналы для мониторинга
MONITORED_CHANNELS = {
    "SCAIH Fund": -1001149489055,
    "seamensclubstudio": -1002250547491
}

# 🔹 Ключевые слова
KEYWORDS = ["Trade"]

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def filter_channel_messages(message: types.Message):
    """Фильтруем сообщения из каналов и пересылаем их в целевой канал"""
    print(f"📩 Сообщение из {message.chat.id}: {message.text if message.text else '[Не текстовое сообщение]'}")

    if message.chat.id not in MONITORED_CHANNELS.values():
        return

    text = message.text.lower() if message.text else ""
    for keyword in KEYWORDS:
        if keyword.lower() in text:
            print(f"✅ Найдено ключевое слово: {keyword}")
            chat_info = f"📢 Новость из канала {message.chat.title or 'Неизвестный'}"
            await bot.send_message(TARGET_CHANNEL_ID, f"{chat_info}\n{text}")
            return

dp.message.register(filter_channel_messages, F.text)

async def start_bot():
    while True:
        try:
            logging.basicConfig(level=logging.INFO)
            await dp.start_polling(bot)
        except TelegramNetworkError:  # ✅ Исправленный обработчик ошибки
            print("🌐 Ошибка сети! Перезапуск через 5 секунд...")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"🔥 Ошибка: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(start_bot())
