#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестирование ограничений тестового терминала T-Bank
"""

import requests
import json
import time
import hashlib

def create_token(data, secret_key):
    """Создает токен с алфавитной сортировкой"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    sorted_keys = sorted(token_data.keys())
    
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    token_string += secret_key
    return hashlib.sha256(token_string.encode('utf-8')).hexdigest()

def test_minimal_request():
    """Тестирует минимальный запрос"""
    print("=== ТЕСТ 1: Минимальный запрос ===")
    
    data = {
        "TerminalKey": "1761136519162DEMO",
        "Amount": 100,
        "OrderId": f"minimal_{int(time.time())}"
    }
    
    secret_key = "TY#iAnEUV*3CS&Bl"
    data["Token"] = create_token(data, secret_key)
    
    print(f"Данные: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "https://securepay.tinkoff.ru/v2/Init",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Статус: {response.status_code}")
        result = response.json()
        print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result.get("Success", False)
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_with_customer_key():
    """Тестирует с CustomerKey"""
    print("\n=== ТЕСТ 2: С CustomerKey ===")
    
    data = {
        "TerminalKey": "1761136519162DEMO",
        "Amount": 100,
        "OrderId": f"customer_{int(time.time())}",
        "CustomerKey": "test_user_123"
    }
    
    secret_key = "TY#iAnEUV*3CS&Bl"
    data["Token"] = create_token(data, secret_key)
    
    print(f"Данные: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "https://securepay.tinkoff.ru/v2/Init",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Статус: {response.status_code}")
        result = response.json()
        print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result.get("Success", False)
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_with_language():
    """Тестирует с Language параметром"""
    print("\n=== ТЕСТ 3: С Language ===")
    
    data = {
        "TerminalKey": "1761136519162DEMO",
        "Amount": 100,
        "OrderId": f"lang_{int(time.time())}",
        "Language": "ru"
    }
    
    secret_key = "TY#iAnEUV*3CS&Bl"
    data["Token"] = create_token(data, secret_key)
    
    print(f"Данные: {json.dumps(data, indent=2)}")
    
    try:
        response = requests.post(
            "https://securepay.tinkoff.ru/v2/Init",
            json=data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Статус: {response.status_code}")
        result = response.json()
        print(f"Ответ: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return result.get("Success", False)
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def test_different_amounts():
    """Тестирует разные суммы"""
    print("\n=== ТЕСТ 4: Разные суммы ===")
    
    amounts = [1, 100, 1000, 10000]  # 1 копейка, 1 рубль, 10 рублей, 100 рублей
    
    for amount in amounts:
        print(f"\n--- Сумма: {amount} копеек ---")
        
        data = {
            "TerminalKey": "1761136519162DEMO",
            "Amount": amount,
            "OrderId": f"amount_{amount}_{int(time.time())}"
        }
        
        secret_key = "TY#iAnEUV*3CS&Bl"
        data["Token"] = create_token(data, secret_key)
        
        try:
            response = requests.post(
                "https://securepay.tinkoff.ru/v2/Init",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            result = response.json()
            print(f"Сумма {amount}: {result.get('Message', 'Unknown')}")
            
            if result.get("Success"):
                print("✅ УСПЕХ!")
                return True
                
        except Exception as e:
            print(f"Ошибка для суммы {amount}: {e}")
    
    return False

def test_api_status():
    """Проверяет статус API"""
    print("\n=== ТЕСТ 5: Статус API ===")
    
    try:
        # Пробуем получить информацию о терминале
        response = requests.get(
            "https://securepay.tinkoff.ru/v2/GetState",
            timeout=10
        )
        print(f"GetState статус: {response.status_code}")
        
        # Пробуем ping
        response = requests.get(
            "https://securepay.tinkoff.ru/v2/",
            timeout=10
        )
        print(f"Ping статус: {response.status_code}")
        
    except Exception as e:
        print(f"Ошибка API: {e}")

def main():
    """Основная функция"""
    print("Тестирование ограничений тестового терминала T-Bank")
    print("=" * 60)
    
    # Тест 1: Минимальный запрос
    success1 = test_minimal_request()
    
    # Тест 2: С CustomerKey
    success2 = test_with_customer_key()
    
    # Тест 3: С Language
    success3 = test_with_language()
    
    # Тест 4: Разные суммы
    success4 = test_different_amounts()
    
    # Тест 5: Статус API
    test_api_status()
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    print(f"Минимальный запрос: {'УСПЕХ' if success1 else 'ПРОВАЛ'}")
    print(f"С CustomerKey: {'УСПЕХ' if success2 else 'ПРОВАЛ'}")
    print(f"С Language: {'УСПЕХ' if success3 else 'ПРОВАЛ'}")
    print(f"Разные суммы: {'УСПЕХ' if success4 else 'ПРОВАЛ'}")
    
    if not any([success1, success2, success3, success4]):
        print("\nВСЕ ТЕСТЫ ПРОВАЛИЛИСЬ")
        print("Возможные причины:")
        print("1. Тестовый терминал не активирован")
        print("2. Неправильные учетные данные")
        print("3. Терминал требует активации основного терминала")
        print("4. Ограничения тестового режима")
    else:
        print("\nНАЙДЕН РАБОЧИЙ ВАРИАНТ!")

if __name__ == "__main__":
    main()
