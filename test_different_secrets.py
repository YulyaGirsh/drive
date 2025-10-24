#!/usr/bin/env python3
"""
Тестирование с разными SecretKey
"""
import urllib.request
import json
import hashlib

def create_token(data, secret_key):
    """Создает токен"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    sorted_keys = sorted(token_data.keys())
    
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    token_string += secret_key
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

def test_secret_keys():
    """Тестирует разные SecretKey"""
    
    # Данные для инициализации платежа
    data = {
        "TerminalKey": "1761136519204",
        "Amount": 1000,
        "OrderId": "test_order_" + str(int(__import__('time').time())),
        "Description": "Test payment"
    }
    
    # Разные варианты SecretKey
    secret_keys = [
        "c^A3qE_zoaH0u%gP",  # Пароль с карточки
        "TY#iAnEUV*3CS&Bl",  # Старый из конфига
        "1761136519204",     # TerminalKey как SecretKey
        "200000001691412",   # Merchant ID как SecretKey
    ]
    
    print("🧪 Тестирование разных SecretKey")
    print("=" * 60)
    print(f"TerminalKey: {data['TerminalKey']}")
    print()
    
    for i, secret_key in enumerate(secret_keys, 1):
        print(f"{i}️⃣ Тестируем SecretKey: {secret_key}")
        
        token = create_token(data, secret_key)
        data["Token"] = token
        
        try:
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
                    print(f"PaymentURL: {result_data.get('PaymentURL')}")
                    return secret_key
                else:
                    print(f"❌ Ошибка: {result_data.get('Message')}")
                    print(f"Детали: {result_data.get('Details')}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print()
    
    print("❌ Ни один SecretKey не подошел")
    return None

if __name__ == "__main__":
    test_secret_keys()

