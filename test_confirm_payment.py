#!/usr/bin/env python3
"""
Тестовый скрипт для проверки подтверждения платежей Т-банк
"""
import json
import urllib.request
import urllib.parse

def test_confirm_payment():
    """Тестирует endpoint подтверждения платежа"""
    
    # Данные для тестирования
    test_data = {
        "payment_id": "test_payment_123",
        "amount": 1000,  # 10₽ в копейках
        "ip_address": "192.168.1.1"
    }
    
    # URL для тестирования
    url = "https://hochupravaeasy.ru/api/tbank-confirm-payment"
    
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
        
        print(f"Тестируем подтверждение платежа: {test_data}")
        print(f"URL: {url}")
        
        # Отправляем запрос
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"Ответ сервера: {result_data}")
            
            if result_data.get('success'):
                print("✅ Подтверждение платежа работает!")
            else:
                print(f"❌ Ошибка: {result_data.get('error', 'Неизвестная ошибка')}")
                
    except urllib.error.HTTPError as e:
        error_response = e.read().decode('utf-8')
        print(f"❌ HTTP ошибка {e.code}: {error_response}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_init_payment():
    """Тестирует endpoint инициализации платежа"""
    
    # Данные для тестирования
    test_data = {
        "user_id": 123456789,
        "amount": 10,
        "description": "Тестовая подписка",
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
        
        print(f"\nТестируем инициализацию платежа: {test_data}")
        print(f"URL: {url}")
        
        # Отправляем запрос
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"Ответ сервера: {result_data}")
            
            if result_data.get('success'):
                print("✅ Инициализация платежа работает!")
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

if __name__ == "__main__":
    print("🧪 Тестирование API Т-банк")
    print("=" * 50)
    
    # Тестируем инициализацию платежа
    payment_id = test_init_payment()
    
    # Если получили payment_id, тестируем подтверждение
    if payment_id:
        print(f"\n🔄 Тестируем подтверждение платежа {payment_id}")
        test_confirm_payment()
    
    print("\n✅ Тестирование завершено")
