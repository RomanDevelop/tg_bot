import asyncio
import logging
import os
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from telethon import TelegramClient, events
from dotenv import load_dotenv

# 🔹 Загружаем переменные из .env
load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# 🔹 Список каналов для мониторинга (из .env)
MONITORED_CHANNELS = list(map(int, os.getenv("MONITORED_CHANNELS").split(",")))

# 🔹 Ключевые слова (из .env)
KEYWORDS = os.getenv("KEYWORDS").split(",")

# 🔹 Настройки бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 🔹 Настройки Telethon (используем обычный Telegram-аккаунт)
client = TelegramClient("my_bot_session", API_ID, API_HASH)

# 🔹 Подключение к SQLite для хранения обработанных сообщений
conn = sqlite3.connect("messages.db")
c = conn.cursor()
c.execute("""
    CREATE TABLE IF NOT EXISTS processed_messages (
        message_id INTEGER PRIMARY KEY
    )
""")
conn.commit()

# 🔹 Проверка дубликатов
def is_duplicate(message_id):
    c.execute("SELECT 1 FROM processed_messages WHERE message_id = ?", (message_id,))
    return c.fetchone() is not None

# 🔹 Сохранение обработанных сообщений
def save_message(message_id):
    c.execute("INSERT INTO processed_messages (message_id) VALUES (?)", (message_id,))
    conn.commit()

# 🔹 Обработчик новых сообщений
@client.on(events.NewMessage(chats=MONITORED_CHANNELS))
async def handler(event):
    message = event.message
    text = message.text or ""
    chat_id = message.chat_id
    message_id = message.id

    # 🔹 Проверяем, содержит ли сообщение ключевое слово
    contains_keyword = any(keyword.lower() in text.lower() for keyword in KEYWORDS)

    # 🔹 Проверяем, является ли сообщение аудиофайлом
    is_audio = message.audio is not None

    # 🔹 Если нет ключевого слова и это не аудиофайл — пропускаем
    if not contains_keyword and not is_audio:
        return

    # 🔹 Проверяем, было ли уже обработано сообщение
    if is_duplicate(message.id):
        return

    # 🔹 Сохраняем сообщение как обработанное
    save_message(message.id)
    logging.info(f"✅ Найдено нужное сообщение (ключевое слово или аудиофайл): {text[:50]}...")

    # 🔹 Создаём ссылку на оригинальный пост
    original_post_url = f"https://t.me/c/{str(chat_id)[4:]}/{message_id}"  # Убираем "-100" из chat_id

    # 🔹 Добавляем кнопку "Открыть оригинал"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📌 Открыть оригинал", url=original_post_url)]
    ])

    try:
        # 🔹 Если есть текст, отправляем его
        if text:
            await bot.send_message(
                CHANNEL_ID,
                f"📢 Новость из канала:\n{text}",
                parse_mode="HTML",
                reply_markup=keyboard  # 🔹 Добавляем кнопку
            )
            logging.info(f"✅ Текстовое сообщение отправлено в канал {CHANNEL_ID}")

        # 🔹 Если есть аудиофайл, отправляем его
        if is_audio:
            await bot.send_file(CHANNEL_ID, message.audio, caption="🎵 Аудиофайл:", reply_markup=keyboard)
            logging.info(f"✅ Аудиофайл отправлен в канал {CHANNEL_ID}")

    except Exception as e:
        logging.error(f"❌ Ошибка при отправке сообщения: {e}")

# 🔹 Функция запуска бота
async def run_bot():
    while True:
        try:
            await client.start()  # Авторизация (в первый раз запросит код)
            logging.info("✅ Бот успешно запущен!")
            await dp.start_polling(bot)
        except Exception as e:
            logging.error(f"🔥 Ошибка: {e}")
            await asyncio.sleep(5)  # Ожидание перед перезапуском

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_bot())
