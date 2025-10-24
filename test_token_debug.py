#!/usr/bin/env python3
"""
Отладочный скрипт для проверки генерации токена Т-банк
"""
import hashlib

def test_token_generation():
    """Тестирует различные способы генерации токена"""
    
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
    
    print("🧪 Тестирование генерации токена Т-банк")
    print("=" * 60)
    
    # Способ 1: Алфавитный порядок
    print("1️⃣ Способ 1: Алфавитный порядок")
    sorted_keys = sorted(data.keys())
    token_string_1 = ""
    for key in sorted_keys:
        token_string_1 += str(data[key])
    token_string_1 += secret_key
    
    token_1 = hashlib.sha256(token_string_1.encode('utf-8')).hexdigest()
    print(f"Строка: {token_string_1}")
    print(f"Токен: {token_1}")
    print()
    
    # Способ 2: Порядок как в документации
    print("2️⃣ Способ 2: Порядок как в документации")
    token_fields = [
        "TerminalKey", "Amount", "OrderId", "Description", 
        "CustomerKey", "Language", "NotificationURL", "SuccessURL", "FailURL"
    ]
    
    token_string_2 = ""
    for field in token_fields:
        if field in data:
            token_string_2 += str(data[field])
    token_string_2 += secret_key
    
    token_2 = hashlib.sha256(token_string_2.encode('utf-8')).hexdigest()
    print(f"Строка: {token_string_2}")
    print(f"Токен: {token_2}")
    print()
    
    # Способ 3: С разделителями
    print("3️⃣ Способ 3: С разделителями")
    token_string_3 = ""
    for key in sorted_keys:
        token_string_3 += f"{key}={data[key]}&"
    token_string_3 = token_string_3.rstrip('&')
    token_string_3 += f"&SecretKey={secret_key}"
    
    token_3 = hashlib.sha256(token_string_3.encode('utf-8')).hexdigest()
    print(f"Строка: {token_string_3}")
    print(f"Токен: {token_3}")
    print()
    
    # Способ 4: Только обязательные поля
    print("4️⃣ Способ 4: Только обязательные поля")
    required_fields = ["TerminalKey", "Amount", "OrderId", "Description"]
    token_string_4 = ""
    for field in required_fields:
        token_string_4 += str(data[field])
    token_string_4 += secret_key
    
    token_4 = hashlib.sha256(token_string_4.encode('utf-8')).hexdigest()
    print(f"Строка: {token_string_4}")
    print(f"Токен: {token_4}")
    print()
    
    print("✅ Тестирование завершено")
    print("Попробуйте каждый токен в API Т-банка")

if __name__ == "__main__":
    test_token_generation()
