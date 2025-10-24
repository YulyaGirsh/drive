#!/usr/bin/env python3
"""
Правильная генерация токена согласно документации Т-банка
"""
import hashlib
import json

def create_correct_token(data, secret_key):
    """
    Создает токен согласно официальной документации Т-банка
    """
    # Исключаем поле Token из генерации
    token_data = {k: v for k, v in data.items() if k != "Token"}
    
    # Сортируем ключи в алфавитном порядке
    sorted_keys = sorted(token_data.keys())
    
    # Создаем строку для токена
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    # Добавляем секретный ключ
    token_string += secret_key
    
    # Создаем SHA-256 хеш
    token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    
    return token, token_string

def test_tbank_api():
    """Тестирует правильную генерацию токена для Т-банк API"""
    
    # Данные для тестирования
    data = {
        "TerminalKey": "1761136519204",
        "Amount": 1000,
        "OrderId": "test_order_123",
        "Description": "Test payment",
        "CustomerKey": "123456789",
        "Language": "ru",
        "NotificationURL": "https://hochupravaeasy.ru/api/tbank-webhook",
        "SuccessURL": "https://hochupravaeasy.ru/success?user_id=123456789",
        "FailURL": "https://hochupravaeasy.ru/fail?user_id=123456789"
    }
    
    secret_key = "c^A3qE_zoaH0u%gP"
    
    print("🧪 Тестирование правильной генерации токена Т-банк")
    print("=" * 60)
    
    # Генерируем токен
    token, token_string = create_correct_token(data, secret_key)
    
    print(f"Данные для токена:")
    for key, value in sorted(data.items()):
        if key != "Token":
            print(f"  {key}: {value}")
    
    print(f"\nСтрока для токена: {token_string}")
    print(f"Сгенерированный токен: {token}")
    print(f"Длина токена: {len(token)}")
    
    # Добавляем токен к данным
    data["Token"] = token
    
    print(f"\nПолные данные для отправки:")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    
    return data

if __name__ == "__main__":
    test_tbank_api()

