#!/usr/bin/env python3
"""
Диагностика сервера для проверки работы API
"""
import requests
import json

def check_server_health():
    """Проверяет состояние сервера"""
    
    base_url = "https://hochupravaeasy.ru"
    
    print("🔍 Диагностика сервера hochupravaeasy.ru")
    print("=" * 50)
    
    # 1. Проверяем главную страницу
    print("1️⃣ Проверяем главную страницу...")
    try:
        response = requests.get(base_url, timeout=10)
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Главная страница работает")
        else:
            print("   ❌ Главная страница не работает")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 2. Проверяем API endpoint
    print("\n2️⃣ Проверяем API endpoint...")
    try:
        api_url = f"{base_url}/api/tbank-create-payment"
        response = requests.post(
            api_url,
            json={"user_id": "test", "amount": 10},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ API endpoint работает")
        elif response.status_code == 404:
            print("   ❌ API endpoint не найден (404)")
            print("   💡 Возможно, Python сервер не запущен")
        elif response.status_code == 500:
            print("   ⚠️ API endpoint работает, но есть ошибка сервера (500)")
        else:
            print(f"   ❌ Неожиданный статус: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 3. Проверяем webhook endpoint
    print("\n3️⃣ Проверяем webhook endpoint...")
    try:
        webhook_url = f"{base_url}/api/tbank-webhook"
        response = requests.post(
            webhook_url,
            json={"test": "webhook"},
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        print(f"   Статус: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Webhook endpoint работает")
        else:
            print(f"   ❌ Webhook endpoint не работает: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка: {e}")
    
    # 4. Проверяем страницы успеха/ошибки
    print("\n4️⃣ Проверяем страницы успеха/ошибки...")
    for page in ["/success", "/fail"]:
        try:
            response = requests.get(f"{base_url}{page}", timeout=10)
            print(f"   {page}: {response.status_code}")
            if response.status_code == 200:
                print(f"   ✅ {page} работает")
            else:
                print(f"   ❌ {page} не работает")
        except Exception as e:
            print(f"   ❌ {page} ошибка: {e}")

if __name__ == "__main__":
    check_server_health()
