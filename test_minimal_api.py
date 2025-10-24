#!/usr/bin/env python3
"""
Тестирование с минимальным набором полей
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

def test_minimal_request():
    """Тестирует с минимальным набором полей"""
    
    # Минимальные данные для инициализации платежа
    data = {
        "TerminalKey": "1761136519204",
        "Amount": 1000,
        "OrderId": "test_order_" + str(int(__import__('time').time())),
        "Description": "Test payment"
    }
    
    secret_key = "c^A3qE_zoaH0u%gP"
    
    # Создаем токен
    token = create_token(data, secret_key)
    data["Token"] = token
    
    print("🧪 Тестирование с минимальным набором полей")
    print("=" * 60)
    print(f"Данные: {json.dumps(data, indent=2, ensure_ascii=False)}")
    
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
        
        print(f"\nОтправляем запрос на: {url}")
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"\nОтвет от Т-банка:")
            print(json.dumps(result_data, indent=2, ensure_ascii=False))
            
            if result_data.get('Success'):
                print("\n✅ УСПЕХ! Платеж инициализирован!")
                print(f"PaymentId: {result_data.get('PaymentId')}")
                print(f"PaymentURL: {result_data.get('PaymentURL')}")
            else:
                print(f"\n❌ ОШИБКА: {result_data.get('Message')}")
                print(f"Код ошибки: {result_data.get('ErrorCode')}")
                print(f"Детали: {result_data.get('Details')}")
                
    except urllib.error.HTTPError as e:
        error_response = e.read().decode('utf-8')
        print(f"\n❌ HTTP ошибка {e.code}: {error_response}")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    test_minimal_request()


