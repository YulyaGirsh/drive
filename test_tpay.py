#!/usr/bin/env python3
"""
Тестовый скрипт для проверки T-Pay интеграции
"""
import json
import urllib.request
import urllib.parse

def test_tpay_init():
    """Тестирует инициализацию T-Pay платежа"""
    
    # Данные для тестирования
    test_data = {
        "user_id": 123456789,
        "amount": 10,
        "description": "Тестовая подписка T-Pay",
        "payment_method": "tpay"
    }
    
    # URL для тестирования
    url = "https://hochupravaeasy.ru/api/tbank-init-payment"
    
    try:
        # Подготавливаем данные
        json_data = json.dumps(test_data).encode('utf-8')
        
        # Создаем запрос
        req = urllib.request.Request(
            url,
            data=json_data,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        
        print(f"Тестируем инициализацию T-Pay: {test_data}")
        print(f"URL: {url}")
        
        # Отправляем запрос
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"Ответ сервера: {result_data}")
            
            if result_data.get('success'):
                print("✅ T-Pay инициализация работает!")
                print(f"🔗 Payment URL: {result_data.get('payment_url')}")
                return result_data.get('payment_id')
            else:
                print(f"❌ Ошибка: {result_data.get('error', 'Неизвестная ошибка')}")
                return None
                
    except urllib.error.HTTPError as e:
        error_response = e.read().decode('utf-8')
        print(f"❌ HTTP ошибка {e.code}: {error_response}")
        return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_direct_tpay():
    """Тестирует прямой вызов T-Pay API"""
    
    print("\n🔧 Тестируем прямой вызов T-Pay API")
    print("=" * 50)
    
    # Импортируем модуль для прямого тестирования
    try:
        from tbank_payment import TbankPayment
        
        payment = TbankPayment()
        result = payment.init_tpay_payment(10, 123456789, "Прямой тест T-Pay")
        
        print(f"Результат прямого вызова: {result}")
        
        if result and result.get('success'):
            print("✅ Прямой вызов T-Pay работает!")
            return result.get('payment_id')
        else:
            print(f"❌ Ошибка прямого вызова: {result.get('error', 'Неизвестная ошибка')}")
            return None
            
    except Exception as e:
        print(f"❌ Ошибка импорта/вызова: {e}")
        return None

def test_token_generation():
    """Тестирует генерацию токена"""
    
    print("\n🔐 Тестируем генерацию токена")
    print("=" * 50)
    
    try:
        from tbank_payment import TbankPayment
        
        payment = TbankPayment()
        
        # Тестовые данные
        test_data = {
            "TerminalKey": "200000001691412",
            "Amount": 1000,
            "OrderId": "test_order_123",
            "Description": "Тест",
            "CustomerKey": "123456789",
            "Language": "ru",
            "NotificationURL": "https://hochupravaeasy.ru/api/tbank-webhook",
            "SuccessURL": "https://hochupravaeasy.ru/success?user_id=123456789",
            "FailURL": "https://hochupravaeasy.ru/fail?user_id=123456789"
        }
        
        token = payment._create_simple_token(test_data)
        print(f"Сгенерированный токен: {token}")
        print(f"Длина токена: {len(token)}")
        
        if token and len(token) == 64:  # SHA-256 дает 64 символа
            print("✅ Генерация токена работает!")
        else:
            print("❌ Ошибка генерации токена")
            
    except Exception as e:
        print(f"❌ Ошибка тестирования токена: {e}")

if __name__ == "__main__":
    print("🧪 Тестирование T-Pay интеграции")
    print("=" * 60)
    
    # Тестируем генерацию токена
    test_token_generation()
    
    # Тестируем прямой вызов
    payment_id = test_direct_tpay()
    
    # Тестируем через API
    if payment_id:
        print(f"\n🔄 Payment ID получен: {payment_id}")
    else:
        print("\n🔄 Тестируем через API...")
        test_tpay_init()
    
    print("\n✅ Тестирование завершено")
