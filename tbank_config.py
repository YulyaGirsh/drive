# Конфигурация Т-банк для интернет-эквайринга
# Замените на реальные данные после регистрации в Т-банк Бизнес

# Данные Т-банк из config.env файла
import os
from dotenv import load_dotenv

# Загружаем переменные из config.env файла
load_dotenv('config.env')

TBANK_MERCHANT_ID = os.getenv('TBANK_MERCHANT_ID', '')  # Обязательно установите в config.env
TBANK_API_KEY = os.getenv('TBANK_API_KEY', '')  # Обязательно установите в config.env
TBANK_SECRET_KEY = os.getenv('TBANK_SECRET_KEY', '')  # Обязательно установите в config.env
TBANK_TERMINAL_KEY = os.getenv('TBANK_TERMINAL_KEY', '')  # Terminal Key для новой интеграции (в config.env)

# URL для API Т-банк из config.env
TBANK_API_URL = os.getenv('TBANK_API_URL', 'https://securepay.tinkoff.ru/v2')
TBANK_WEBHOOK_URL = os.getenv('TBANK_WEBHOOK_URL', 'https://hochupravaeasy.ru/api/tbank-webhook')

# URL для перенаправления после оплаты
TBANK_SUCCESS_URL = os.getenv('TBANK_SUCCESS_URL', 'https://hochupravaeasy.ru/success')
TBANK_FAIL_URL = os.getenv('TBANK_FAIL_URL', 'https://hochupravaeasy.ru/fail')

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
    "terminal_key": TBANK_TERMINAL_KEY,
    "api_url": TBANK_API_URL,
    "webhook_url": TBANK_WEBHOOK_URL,
    "success_url": TBANK_SUCCESS_URL,
    "fail_url": TBANK_FAIL_URL
}
