import asyncio
import logging
import os
import requests
from aiogram import Bot
from dotenv import load_dotenv

# 🔹 Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")  # Токен бота
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")  # Канал, куда отправлять посты
TGSTAT_API_KEY = os.getenv("TGSTAT_API_KEY")  # API-ключ TGStat

if not TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env!")
if not TARGET_CHANNEL_ID:
    raise ValueError("❌ Ошибка: TARGET_CHANNEL_ID не найден в .env!")
if not TGSTAT_API_KEY:
    raise ValueError("❌ Ошибка: TGSTAT_API_KEY не найден в .env!")

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)

# 🔹 ID канала UTEX
CHANNEL_ID = "@utex_exchange"

# 🔹 URL для получения постов через TGStat API
TGSTAT_URL = f"https://api.tgstat.ru/channels/posts?channelId={CHANNEL_ID}&limit=10"
HEADERS = {"Authorization": f"Bearer {TGSTAT_API_KEY}"}

bot = Bot(token=TOKEN)

# Храним ID уже отправленных постов, чтобы не дублировать
sent_messages = set()

async def fetch_and_send():
    """Проверяет новые посты и отправляет только с 'Trade'."""
    response = requests.get(TGSTAT_URL, headers=HEADERS)
    data = response.json()
    
    if "response" in data and "items" in data["response"]:
        for post in data["response"]["items"]:
            text = post["text"]
            post_id = post["date"]  # Используем дату как уникальный ID поста
            
            if "Trade" in text or "trade" in text:  # Фильтр по слову
                if post_id not in sent_messages:  # Проверяем, не отправляли ли этот пост ранее
                    message = f"📢 Новость из UTEX:\n{text}"
                    await bot.send_message(TARGET_CHANNEL_ID, message)
                    sent_messages.add(post_id)  # Добавляем в список отправленных
                    print(f"✅ Отправлено: {text[:50]}...")  
            else:
                print(f"⏩ Пропущено: {text[:50]}...")  
    else:
        print("❌ Ошибка при получении данных!")

async def main():
    """Запускаем цикл проверки новых постов каждые 5 минут."""
    while True:
        await fetch_and_send()
        print("🔄 Ожидание 5 минут перед следующей проверкой...")
        await asyncio.sleep(300)  # Задержка 300 секунд (5 минут)

if __name__ == "__main__":
    asyncio.run(main())
