"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv('config.env')

# Конфигурация бота из переменных окружения
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения! Установите его в config.env")

# ID получателя для уведомлений (админ)
ADMIN_CHAT_ID = int(os.getenv('RECIPIENT_ID', os.getenv('ADMIN_CHAT_ID', '5292692434')))

# Порт сервера
PORT = 8000

