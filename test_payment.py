#!/usr/bin/env python3
"""
Тест для проверки работы API оплаты
"""
import requests
import json

def test_payment_api():
    """Тестирует API создания платежа"""
    
    # URL для тестирования
    api_url = "https://hochupravaeasy.ru/api/tbank-create-payment"
    
    # Тестовые данные
    test_data = {
        "user_id": "test_user_123",
        "amount": 10,
        "payment_method": "tbank"
    }
    
    print(f"🧪 Тестируем API: {api_url}")
    print(f"📤 Отправляем данные: {test_data}")
    
    try:
        # Отправляем POST запрос
        response = requests.post(
            api_url,
            json=test_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Статус ответа: {response.status_code}")
        print(f"📋 Заголовки: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Успешный ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            print(f"📄 Текст ответа: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Запуск теста API оплаты...")
    success = test_payment_api()
    
    if success:
        print("✅ API работает корректно!")
    else:
        print("❌ API не работает. Проверьте настройки сервера.")
