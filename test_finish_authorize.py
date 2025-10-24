#!/usr/bin/env python3
"""
Тестовый скрипт для проверки завершения авторизации платежей Т-банк
"""
import json
import urllib.request
import urllib.parse

def test_finish_authorize():
    """Тестирует endpoint завершения авторизации платежа"""
    
    # Данные для тестирования
    test_data = {
        "payment_id": "test_payment_123",
        "ip_address": "192.168.1.1",
        "send_email": False,
        "source": "cards",
        "amount": 1000,  # 10₽ в копейках
        "device_channel": "02",
        "route": "ACQ",
        "info_email": "test@example.com",
        "data_params": {
            "threeDSCompInd": "Y",
            "language": "RU",
            "timezone": "-300",
            "screen_height": "1024",
            "screen_width": "967",
            "cresCallbackUrl": "https://hochupravaeasy.ru/callback",
            "colorDepth": "48",
            "javaEnabled": "false"
        }
    }
    
    # URL для тестирования
    url = "https://hochupravaeasy.ru/api/tbank-finish-authorize"
    
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
        
        print(f"Тестируем завершение авторизации: {test_data}")
        print(f"URL: {url}")
        
        # Отправляем запрос
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"Ответ сервера: {result_data}")
            
            if result_data.get('success'):
                print("✅ Завершение авторизации работает!")
                if result_data.get('acs_url'):
                    print(f"🔐 Требуется 3DS аутентификация: {result_data.get('acs_url')}")
            else:
                print(f"❌ Ошибка: {result_data.get('error', 'Неизвестная ошибка')}")
                
    except urllib.error.HTTPError as e:
        error_response = e.read().decode('utf-8')
        print(f"❌ HTTP ошибка {e.code}: {error_response}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_complete_payment_flow():
    """Тестирует полный цикл платежа"""
    
    print("\n🔄 Тестируем полный цикл платежа")
    print("=" * 50)
    
    # 1. Инициализация платежа
    print("1️⃣ Инициализация платежа...")
    init_data = {
        "user_id": 123456789,
        "amount": 10,
        "description": "Тестовая подписка",
        "payment_method": "tpay"
    }
    
    init_url = "https://hochupravaeasy.ru/api/tbank-init-payment"
    
    try:
        json_data = json.dumps(init_data).encode('utf-8')
        req = urllib.request.Request(
            init_url,
            data=json_data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            if result_data.get('success'):
                payment_id = result_data.get('payment_id')
                print(f"✅ Платеж инициализирован: {payment_id}")
                
                # 2. Завершение авторизации (если требуется)
                print("2️⃣ Завершение авторизации...")
                finish_data = {
                    "payment_id": payment_id,
                    "ip_address": "192.168.1.1",
                    "source": "cards",
                    "amount": 1000
                }
                
                finish_url = "https://hochupravaeasy.ru/api/tbank-finish-authorize"
                
                json_data = json.dumps(finish_data).encode('utf-8')
                req = urllib.request.Request(
                    finish_url,
                    data=json_data,
                    headers={'Content-Type': 'application/json'}
                )
                
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    result_data = json.loads(result)
                    
                    if result_data.get('success'):
                        print("✅ Авторизация завершена!")
                        if result_data.get('acs_url'):
                            print(f"🔐 Требуется 3DS: {result_data.get('acs_url')}")
                    else:
                        print(f"❌ Ошибка авторизации: {result_data.get('error')}")
                        
            else:
                print(f"❌ Ошибка инициализации: {result_data.get('error')}")
                
    except Exception as e:
        print(f"❌ Ошибка в полном цикле: {e}")

if __name__ == "__main__":
    print("🧪 Тестирование завершения авторизации Т-банк")
    print("=" * 60)
    
    # Тестируем завершение авторизации
    test_finish_authorize()
    
    # Тестируем полный цикл
    test_complete_payment_flow()
    
    print("\n✅ Тестирование завершено")
