import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")  # Канал, куда пересылаем новости

if not TOKEN:
    raise ValueError("❌ Ошибка: BOT_TOKEN не найден в .env!")
if not TARGET_CHANNEL_ID:
    raise ValueError("❌ Ошибка: TARGET_CHANNEL_ID не найден в .env!")

TARGET_CHANNEL_ID = int(TARGET_CHANNEL_ID)  # Преобразуем в число

# 🔹 Список каналов, откуда берем новости (замени на реальные ID)
MONITORED_CHANNELS = {
    "russians_in_marbella": -1001998381194, 
    "malagabaraholka": -1001582518638, 
    "costadelsolvida": -1001865891347,
    "malaga_community": -1001668845214,
    "1926": -1001866948591, 
    "marbellaespana_chat": -1002142873301,
    "Seamen'sClubStudio": -1002250547491
}

# Ключевые слова для поиска
KEYWORDS = [
    "Сниму", "Аренда", "Длительно", "Посуточно", "Квартира", "Дом", "Апартаменты", "посредников",
    "Недвижимость", "Вилла", "Инвестицию", "Жилье", "Студия", "Зніму", "Оренда", "Довгостроково",
    "Подобово", "Квартира", "Будинок", "Апартаменти", "Посередників", "Нерухомість", "Вілла",
    "Інвестицію", "Житло", "Студія", "Сдам"
]

# Создаем бота и диспетчер
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def filter_channel_messages(message: types.Message):
    """Фильтруем сообщения из каналов и пересылаем новости по ключевым словам в твой канал"""
    
    # Логируем все сообщения, даже если бот их не обрабатывает
    print(f"📩 Получено сообщение из {message.chat.id}: {message.text if message.text else '[Не текстовое сообщение]'}")

    # Проверяем, отслеживается ли этот канал
    if message.chat.id not in MONITORED_CHANNELS.values():
        print(f"🚫 Канал {message.chat.id} не в списке мониторинга. Игнорируем.")
        return

    text = message.text.lower() if message.text else ""

    for keyword in KEYWORDS:
        if keyword.lower() in text:
            print(f"✅ Найдено ключевое слово: {keyword}")

            channel_name = next((name for name, chat_id in MONITORED_CHANNELS.items() if chat_id == message.chat.id), "Неизвестный канал")
            chat_info = f"📢 Новость из канала @{channel_name}"
            message_text = f"\n{text}"

            # Отправляем сообщение в твой канал
            await bot.send_message(TARGET_CHANNEL_ID, f"{chat_info}\n{message_text}")
            return  # Останавливаем проверку после первого совпадения

# Бот отслеживает только текстовые сообщения из каналов
dp.message.register(filter_channel_messages, F.text)

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
