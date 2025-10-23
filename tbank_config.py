# Конфигурация Т-банк для интернет-эквайринга
# Замените на реальные данные после регистрации в Т-банк Бизнес

# Данные Т-банк из config.env файла
import os
from pathlib import Path

# Загружаем переменные из config.env файла
config_file = Path('config.env')
if config_file.exists():
    with open(config_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

TBANK_MERCHANT_ID = os.getenv('TBANK_MERCHANT_ID', '200000001691412')
TBANK_API_KEY = os.getenv('TBANK_API_KEY', '1761136519162DEMO')
TBANK_SECRET_KEY = os.getenv('TBANK_SECRET_KEY', 'TY#iAnEUV*3CS&Bl')

# URL для API Т-банк из config.env
TBANK_API_URL = os.getenv('TBANK_API_URL', 'https://api.tbank.ru/v1/payments')
TBANK_WEBHOOK_URL = os.getenv('TBANK_WEBHOOK_URL', 'https://hochupravaeasy.ru/api/tbank-webhook')

# Настройки платежа
PAYMENT_CURRENCY = "RUB"
PAYMENT_DESCRIPTION = "Подписка на видеоуроки EasyDrive"

# Тестовые данные для демонстрации
TEST_CARD_DATA = {
    "number": "4111111111111111",  # Тестовая карта Visa
    "expiry": "12/25",
    "cvv": "123",
    "holder": "TEST USER"
}

# Реальные данные из config.env
REAL_CONFIG = {
    "merchant_id": TBANK_MERCHANT_ID,
    "api_key": TBANK_API_KEY,
    "secret_key": TBANK_SECRET_KEY,
    "api_url": TBANK_API_URL,
    "webhook_url": TBANK_WEBHOOK_URL
}
