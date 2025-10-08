import asyncio
import logging
import json
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# Загружаем переменные окружения
load_dotenv('config.env')

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Токен бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")

# ID получателя для отправки данных форм
RECIPIENT_ID = int(os.getenv('RECIPIENT_ID', '7644513746'))

# URL приложения
APP_URL = os.getenv('APP_URL', 'http://89.23.99.152')

# Создание экземпляров бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    # Получаем имя пользователя
    username = message.from_user.first_name or "Пользователь"
    
    # Отправляем приветственное сообщение
    welcome_text = f"{username}, привет 👋\n\n📲 Это приложение EasyDrive. Здесь собраны онлайн-курсы, решение билетов и видеоразборы — всё для быстрой и уверенной сдачи на права."

    # Создаем кнопку для открытия приложения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть приложение", url=APP_URL)]
    ])

    await message.answer(
        text=welcome_text,
        reply_markup=keyboard
    )

@dp.message()
async def handle_form_data(message: types.Message):
    """Обработчик для получения данных из форм"""
    try:
        # Пытаемся распарсить JSON данные
        data = json.loads(message.text)
        
        # Проверяем тип формы
        if 'form_type' in data:
            form_type = data['form_type']
            
            if form_type == 'lawyer':
                await send_lawyer_data(data)
            elif form_type == 'psychologist':
                await send_psychologist_data(data)
            else:
                await message.answer("❌ Неизвестный тип формы")
        else:
            await message.answer("❌ Неверный формат данных")
            
    except json.JSONDecodeError:
        # Если это не JSON, обрабатываем как обычное сообщение
        await message.answer("Привет! Используйте /start для начала работы.")

async def send_lawyer_data(data):
    """Отправка данных формы автоюриста"""
    try:
        message_text = f"""
⚖️ <b>НОВАЯ ЗАЯВКА ОТ АВТОЮРИСТА</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
📞 <b>Телефон:</b> {data.get('phone', 'Не указано')}
📝 <b>Ситуация:</b> {data.get('situation', 'Не указано')}

🕐 <b>Время:</b> {data.get('timestamp', 'Не указано')}
        """
        
        await bot.send_message(
            chat_id=RECIPIENT_ID,
            text=message_text,
            parse_mode='HTML'
        )
        
        logging.info(f"Данные формы автоюриста отправлены: {data}")
        
    except Exception as e:
        logging.error(f"Ошибка отправки данных автоюриста: {e}")

async def send_psychologist_data(data):
    """Отправка данных формы автопсихолога"""
    try:
        message_text = f"""
🧠 <b>НОВАЯ ЗАЯВКА ОТ АВТОПСИХОЛОГА</b>

👤 <b>Имя:</b> {data.get('name', 'Не указано')}
📞 <b>Телефон:</b> {data.get('phone', 'Не указано')}
📝 <b>Ситуация:</b> {data.get('situation', 'Не указано')}

🕐 <b>Время:</b> {data.get('timestamp', 'Не указано')}
        """
        
        await bot.send_message(
            chat_id=RECIPIENT_ID,
            text=message_text,
            parse_mode='HTML'
        )
        
        logging.info(f"Данные формы автопсихолога отправлены: {data}")
        
    except Exception as e:
        logging.error(f"Ошибка отправки данных автопсихолога: {e}")

async def main():
    print("Бот запускается...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
