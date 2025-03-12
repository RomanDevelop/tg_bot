import asyncio
import logging
import os
import requests
from bs4 import BeautifulSoup
from aiogram import Bot
from dotenv import load_dotenv
from datetime import datetime
import pytz

# 🔹 Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")  # Токен бота
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")  # Канал, куда отправлять посты

if not TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env!")
if not TARGET_CHANNEL_ID:
    raise ValueError("❌ Ошибка: TARGET_CHANNEL_ID не найден в .env!")

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)

# 🔹 URL веб-версии Telegram канала UTEX
TELEGRAM_URL = "https://t.me/s/utex_exchange"

# 🔹 Часовой пояс Украины (UTC+2)
UKRAINE_TZ = pytz.timezone("Europe/Kiev")

bot = Bot(token=TOKEN)

# Храним уже отправленные посты, чтобы избежать дубликатов
sent_messages = set()

def fetch_latest_posts():
    """Парсит веб-версию Telegram-канала и возвращает новые посты с 'Trade'."""
    try:
        response = requests.get(TELEGRAM_URL)
        if response.status_code != 200:
            print(f"❌ Ошибка при загрузке Telegram-страницы! Код: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        posts = soup.find_all("div", class_="tgme_widget_message_text")
        
        new_posts = []
        for post in posts:
            text = post.get_text()
            if "Trade" in text or "trade" in text:
                post_id = hash(text)  # Генерируем ID на основе текста поста
                if post_id not in sent_messages:
                    new_posts.append((post_id, text))
                    sent_messages.add(post_id)
        
        return new_posts
    except Exception as e:
        print(f"🔥 Ошибка парсинга: {e}")
        return []

async def fetch_and_send():
    """Получает новые посты с 'Trade' и отправляет в Telegram-канал (только в нужное время)."""
    now = datetime.now(UKRAINE_TZ).time()  # Текущее время в Украине
    start_time = datetime.strptime("12:00", "%H:%M").time()
    end_time = datetime.strptime("22:00", "%H:%M").time()

    if start_time <= now <= end_time:
        print("✅ В рабочее время, проверяем посты...")
        new_posts = fetch_latest_posts()
        for post_id, text in new_posts:
            message = f"📢 Новость из UTEX:\n{text}"
            await bot.send_message(TARGET_CHANNEL_ID, message)
            print(f"✅ Отправлено: {text[:50]}...")
    else:
        print("⏳ Вне рабочего времени, бот ждет следующего запуска.")

async def main():
    """Запускаем бесконечный цикл парсинга каждые 30 минут с 12:00 до 22:00 (Украина)."""
    while True:
        await fetch_and_send()
        print("🔄 Ожидание 30 минут перед следующей проверкой...")
        await asyncio.sleep(1800)  # Задержка 1800 секунд (30 минут)

if __name__ == "__main__":
    asyncio.run(main())
