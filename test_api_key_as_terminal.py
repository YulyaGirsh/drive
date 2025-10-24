#!/usr/bin/env python3
"""
Тестирование с API Key как TerminalKey
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

def test_with_api_key():
    """Тестирует с API Key как TerminalKey"""
    
    # Пробуем разные комбинации
    test_cases = [
        {
            "name": "API Key как TerminalKey + SecretKey",
            "terminal_key": "1761136519204",
            "secret_key": "c^A3qE_zoaH0u%gP"
        },
        {
            "name": "Merchant ID как TerminalKey + SecretKey", 
            "terminal_key": "200000001691412",
            "secret_key": "c^A3qE_zoaH0u%gP"
        },
        {
            "name": "API Key как TerminalKey + API Key как SecretKey",
            "terminal_key": "1761136519204", 
            "secret_key": "1761136519204"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}️⃣ {case['name']}")
        print("=" * 50)
        
        # Данные для инициализации платежа
        data = {
            "TerminalKey": case["terminal_key"],
            "Amount": 1000,
            "OrderId": "test_order_" + str(int(__import__('time').time())),
            "Description": "Test payment"
        }
        
        # Создаем токен
        token = create_token(data, case["secret_key"])
        data["Token"] = token
        
        print(f"TerminalKey: {case['terminal_key']}")
        print(f"SecretKey: {case['secret_key']}")
        print(f"Token: {token}")
        
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
                    print(f"✅ УСПЕХ! Правильная комбинация найдена!")
                    print(f"PaymentId: {result_data.get('PaymentId')}")
                    print(f"PaymentURL: {result_data.get('PaymentURL')}")
                    return case
                else:
                    print(f"❌ Ошибка: {result_data.get('Message')}")
                    print(f"Детали: {result_data.get('Details')}")
                    
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    print("\n❌ Ни одна комбинация не подошла")
    return None

if __name__ == "__main__":
    test_with_api_key()


