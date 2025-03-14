import logging
import sqlite3
import os
import asyncio
from aiogram import Bot, Dispatcher, types
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 🔹 Загружаем переменные из .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))  # API ID из my.telegram.org
API_HASH = os.getenv("API_HASH")  # API HASH из my.telegram.org
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Токен Telegram-бота
GROUP_ID = int(os.getenv("GROUP_ID"))  # ID группы/канала, откуда парсим
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # ID канала, куда пересылать
KEYWORD = os.getenv("KEYWORD").lower()  # Ключевое слово для поиска

# 🔹 Настройки бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔹 Настройки Telethon
client = TelegramClient("session_name", API_ID, API_HASH)

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

# 🔹 Обработчик новых сообщений в группе/канале
@client.on(events.NewMessage(chats=GROUP_ID))
async def handler(event):
    message = event.message
    if message.text and KEYWORD in message.text.lower() and not is_duplicate(message.id):
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
