import logging
import sqlite3
import os
import asyncio
from aiogram import Bot, Dispatcher
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 🔹 Загружаем переменные из .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))  # API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # API HASH из my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен Telegram-бота
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# 🔹 Читаем список ключевых слов и каналов из `.env`
KEYWORDS = set(os.getenv("KEYWORDS", "").split(","))  # Разделяем по запятой
MONITORED_CHANNELS = list(map(int, os.getenv("MONITORED_CHANNELS", "").split(",")))  # Преобразуем в int

# 🔹 Настройки бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔹 Настройки Telethon
client = TelegramClient("my_bot_session", API_ID, API_HASH)

# 🔹 Подключение к базе данных SQLite (сохраняем обработанные сообщения)
conn = sqlite3.connect("messages.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS processed_messages (
        message_id INTEGER PRIMARY KEY
    )
""")
conn.commit()

# 🔹 Функция для проверки дубликатов
def is_duplicate(message_id):
    c.execute("SELECT 1 FROM processed_messages WHERE message_id = ?", (message_id,))
    return c.fetchone() is not None

# 🔹 Функция для сохранения обработанных сообщений
def save_message(message_id):
    c.execute("INSERT INTO processed_messages (message_id) VALUES (?)", (message_id,))
    conn.commit()

# 🔹 Обработчик новых сообщений в каналах
@client.on(events.NewMessage(chats=MONITORED_CHANNELS))
async def handler(event):
    message = event.message
    if message.text:
        lower_text = message.text.lower()
        if any(keyword.lower() in lower_text for keyword in KEYWORDS) and not is_duplicate(message.id):
            save_message(message.id)
            await bot.send_message(CHANNEL_ID, message.text, parse_mode="HTML")

            # Если есть медиа (фото, видео, документы), пересылаем их
            if message.media:
                await bot.send_file(CHANNEL_ID, message.media)

# 🔹 Функция запуска бота
async def main():
    await client.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
