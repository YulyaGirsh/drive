#!/usr/bin/env python3
"""
Тестирование с разными ключами
"""
import urllib.request
import json
import hashlib

def create_token(data, secret_key):
    """Создает токен согласно документации Т-банка"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    sorted_keys = sorted(token_data.keys())
    
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    token_string += secret_key
    token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    
    return token

def test_with_different_keys():
    """Тестирует с разными комбинациями ключей"""
    
    # Данные для инициализации платежа
    data = {
        "TerminalKey": "1761136519204",
        "Amount": 1000,
        "OrderId": "test_order_" + str(int(__import__('time').time())),
        "Description": "Test payment",
        "CustomerKey": "123456789",
        "Language": "ru",
        "NotificationURL": "https://hochupravaeasy.ru/api/tbank-webhook",
        "SuccessURL": "https://hochupravaeasy.ru/success?user_id=123456789",
        "FailURL": "https://hochupravaeasy.ru/fail?user_id=123456789"
    }
    
    # Разные варианты SecretKey для тестирования
    secret_keys = [
        "c^A3qE_zoaH0u%gP",  # Текущий
        "TY#iAnEUV*3CS&Bl",  # Старый из конфига
        "1761136519204",     # API Key как SecretKey
        "200000001691412",   # Merchant ID как SecretKey
    ]
    
    print("🧪 Тестирование с разными SecretKey")
    print("=" * 60)
    
    for i, secret_key in enumerate(secret_keys, 1):
        print(f"\n{i}️⃣ Тестируем SecretKey: {secret_key}")
        
        # Создаем токен
        token = create_token(data, secret_key)
        data["Token"] = token
        
        try:
            # Отправляем запрос в Т-банк
            url = "https://securepay.tinkoff.ru/v2/Init"
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                if result_data.get('Success'):
                    print(f"✅ УСПЕХ! SecretKey: {secret_key}")
                    print(f"PaymentId: {result_data.get('PaymentId')}")
                    return secret_key
                else:
                    print(f"❌ Ошибка: {result_data.get('Message')}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n❌ Ни один SecretKey не подошел")
    return None

if __name__ == "__main__":
    test_with_different_keys()

