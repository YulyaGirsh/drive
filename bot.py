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

# URL приложения (HTTPS требуется для Telegram Mini App)
APP_URL = os.getenv('APP_URL', 'https://hochupravaeasy.ru')

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

    # Создаем кнопку для открытия мини-приложения
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌐 Открыть приложение", web_app={"url": APP_URL})]
    ])

    await message.answer(
        text=welcome_text,
        reply_markup=keyboard
    )

@dp.message(Command("trans"))
async def cmd_trans(message: types.Message):
    """Обработчик команды /trans для управления трансляциями"""
    # Проверяем, что это администратор
    if message.from_user.id != RECIPIENT_ID:
        await message.answer("❌ У вас нет прав для управления трансляциями.")
        return
    
    # Создаем клавиатуру для управления трансляциями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Установить дату и время", callback_data="set_datetime")],
        [InlineKeyboardButton(text="🔗 Установить ссылку", callback_data="set_link")],
        [InlineKeyboardButton(text="👁️ Посмотреть текущие данные", callback_data="view_current")],
        [InlineKeyboardButton(text="🗑️ Очистить данные", callback_data="clear_data")]
    ])
    
    await message.answer(
        text="📺 <b>Управление трансляциями</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

@dp.message()
async def handle_all_messages(message: types.Message):
    """Обработчик для всех сообщений"""
    # Проверяем, что это администратор для команд трансляций
    if message.from_user.id == RECIPIENT_ID:
        text = message.text.strip()
        
        # Проверяем, является ли сообщение датой/временем
        if text.count('-') == 2 and text.count(':') == 1 and len(text) == 16:
            try:
                # Парсим дату и время
                from datetime import datetime
                dt = datetime.strptime(text, '%Y-%m-%d %H:%M')
                
                # Загружаем существующие данные или создаем новые
                try:
                    with open('translation_data.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except FileNotFoundError:
                    data = {}
                
                # Обновляем дату и время
                data['datetime'] = text
                data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Сохраняем данные
                with open('translation_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                await message.answer(f"✅ Дата и время установлены: {text}")
                return
                
            except ValueError:
                await message.answer("❌ Неверный формат даты и времени. Используйте: YYYY-MM-DD HH:MM")
                return
        
        # Проверяем, является ли сообщение ссылкой
        elif text.startswith('http://') or text.startswith('https://'):
            try:
                # Загружаем существующие данные или создаем новые
                try:
                    with open('translation_data.json', 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except FileNotFoundError:
                    data = {}
                
                # Обновляем ссылку
                data['link'] = text
                data['updated_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Сохраняем данные
                with open('translation_data.json', 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                await message.answer(f"✅ Ссылка установлена: {text}")
                return
                
            except Exception as e:
                await message.answer(f"❌ Ошибка при сохранении ссылки: {str(e)}")
                return
    
    # Обработка данных из форм (для всех пользователей)
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

# Импорт для работы с callback'ами
from aiogram.types import CallbackQuery
from aiogram.filters import CommandStart

# Обработчики callback'ов для управления трансляциями
@dp.callback_query(lambda c: c.data == "view_current")
async def view_current_translation(callback_query: CallbackQuery):
    """Показать текущие данные о трансляции"""
    try:
        # Читаем данные из файла (если есть)
        try:
            with open('translation_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            datetime_str = data.get('datetime', 'Не установлено')
            link = data.get('link', 'Не установлено')
            updated_at = data.get('updated_at', 'Неизвестно')
            
            message_text = f"""📺 <b>Текущие данные о трансляции:</b>

📅 <b>Дата и время:</b> {datetime_str}
🔗 <b>Ссылка:</b> {link}
🕐 <b>Обновлено:</b> {updated_at}"""
            
        except FileNotFoundError:
            message_text = "📺 <b>Данные о трансляции не установлены</b>\n\nИспользуйте кнопки ниже для настройки."
        
        await callback_query.message.edit_text(
            text=message_text,
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
        )
        
    except Exception as e:
        await callback_query.answer(f"Ошибка: {str(e)}", show_alert=True)

@dp.callback_query(lambda c: c.data == "set_datetime")
async def set_datetime(callback_query: CallbackQuery):
    """Установить дату и время трансляции"""
    await callback_query.message.edit_text(
        text="📅 <b>Установка даты и времени</b>\n\nОтправьте дату и время в формате:\n<code>YYYY-MM-DD HH:MM</code>\n\nНапример: <code>2024-12-25 19:00</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
    )

@dp.callback_query(lambda c: c.data == "set_link")
async def set_link(callback_query: CallbackQuery):
    """Установить ссылку на трансляцию"""
    await callback_query.message.edit_text(
        text="🔗 <b>Установка ссылки на трансляцию</b>\n\nОтправьте ссылку на трансляцию.\nНапример: <code>https://youtube.com/watch?v=...</code>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
        ])
    )

@dp.callback_query(lambda c: c.data == "clear_data")
async def clear_data(callback_query: CallbackQuery):
    """Очистить данные о трансляции"""
    try:
        # Удаляем файл с данными
        import os
        if os.path.exists('translation_data.json'):
            os.remove('translation_data.json')
        
        await callback_query.message.edit_text(
            text="🗑️ <b>Данные о трансляции очищены</b>\n\nВсе данные о трансляции удалены.",
            parse_mode="HTML",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_menu")]
            ])
        )
        
    except Exception as e:
        await callback_query.answer(f"Ошибка: {str(e)}", show_alert=True)

@dp.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_menu(callback_query: CallbackQuery):
    """Вернуться в главное меню управления трансляциями"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Установить дату и время", callback_data="set_datetime")],
        [InlineKeyboardButton(text="🔗 Установить ссылку", callback_data="set_link")],
        [InlineKeyboardButton(text="👁️ Посмотреть текущие данные", callback_data="view_current")],
        [InlineKeyboardButton(text="🗑️ Очистить данные", callback_data="clear_data")]
    ])
    
    await callback_query.message.edit_text(
        text="📺 <b>Управление трансляциями</b>\n\nВыберите действие:",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


async def main():
    print("Бот запускается...")
    await dp.start_polling(bot, skip_updates=True)

if __name__ == "__main__":
    asyncio.run(main())
