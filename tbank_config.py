# Конфигурация Т-банк для интернет-эквайринга
# Замените на реальные данные после регистрации в Т-банк Бизнес

# Данные Т-банк из переменных окружения
import os

TBANK_MERCHANT_ID = os.getenv('TBANK_MERCHANT_ID', '200000001691412')
TBANK_API_KEY = os.getenv('TBANK_API_KEY', '1761136519162DEMO')
TBANK_SECRET_KEY = os.getenv('TBANK_SECRET_KEY', 'TY#iAnEUV*3CS&Bl')

# URL для API Т-банк
TBANK_API_URL = "https://api.tbank.ru/v1/payments"  # Реальный URL
TBANK_WEBHOOK_URL = "https://hochupravaeasy.ru/api/tbank-webhook"  # URL для уведомлений

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

# Реальные данные (заполнены)
REAL_CONFIG = {
    "merchant_id": "200000001691412",  # Заполнено
    "api_key": "1761136519162DEMO",    # Заполнено
    "secret_key": "TY#iAnEUV*3CS&Bl", # Заполнено
    "api_url": "https://api.tbank.ru/v1/payments",  # Реальный URL
    "webhook_url": "https://hochupravaeasy.ru/api/tbank-webhook"
}
