#!/usr/bin/env python3
"""
Финальный тест с правильными данными
"""
import urllib.request
import json
import hashlib

def create_token_v1(data, secret_key):
    """Версия 1: Алфавитный порядок"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    sorted_keys = sorted(token_data.keys())
    
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    token_string += secret_key
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

def create_token_v2(data, secret_key):
    """Версия 2: Порядок как в документации"""
    token_fields = [
        "TerminalKey", "Amount", "OrderId", "Description", 
        "CustomerKey", "Language", "NotificationURL", "SuccessURL", "FailURL"
    ]
    
    token_string = ""
    for field in token_fields:
        if field in data and data[field] is not None:
            token_string += str(data[field])
    
    token_string += secret_key
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

def create_token_v3(data, secret_key):
    """Версия 3: Только обязательные поля"""
    required_fields = ["TerminalKey", "Amount", "OrderId", "Description"]
    
    token_string = ""
    for field in required_fields:
        if field in data:
            token_string += str(data[field])
    
    token_string += secret_key
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

def test_api_call(data, token, version):
    """Тестирует API вызов"""
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
                print(f"✅ УСПЕХ! Версия {version} работает!")
                print(f"PaymentId: {result_data.get('PaymentId')}")
                print(f"PaymentURL: {result_data.get('PaymentURL')}")
                return True
            else:
                print(f"❌ Версия {version}: {result_data.get('Message')}")
                return False
                
    except Exception as e:
        print(f"❌ Версия {version}: {e}")
        return False

def test_all_versions():
    """Тестирует все версии генерации токена"""
    
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
    
    secret_key = "c^A3qE_zoaH0u%gP"
    
    print("🧪 Финальный тест с правильными данными")
    print("=" * 60)
    print(f"TerminalKey: {data['TerminalKey']}")
    print(f"SecretKey: {secret_key}")
    print()
    
    # Тестируем все версии
    versions = [
        ("Алфавитный порядок", create_token_v1),
        ("Порядок документации", create_token_v2),
        ("Только обязательные поля", create_token_v3)
    ]
    
    for i, (name, create_func) in enumerate(versions, 1):
        print(f"{i}️⃣ Тестируем: {name}")
        token = create_func(data, secret_key)
        print(f"Токен: {token}")
        
        if test_api_call(data.copy(), token, i):
            print(f"🎉 Найдена рабочая версия: {name}")
            return create_func
        
        print()
    
    print("❌ Ни одна версия не сработала")
    return None

if __name__ == "__main__":
    test_all_versions()


