#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Финальный тест с тестовым терминалом T-Bank
"""

import requests
import json
import time
import hashlib

def create_correct_token(data, secret_key):
    """Создает токен согласно официальной документации Т-банка"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    
    # Создаем строку для токена согласно примеру от техподдержки
    token_string = ""
    
    # Amount
    if "Amount" in token_data and token_data["Amount"] is not None:
        token_string += str(token_data["Amount"])
    
    # Description  
    if "Description" in token_data and token_data["Description"] is not None:
        token_string += str(token_data["Description"])
    
    # FailURL
    if "FailURL" in token_data and token_data["FailURL"] is not None:
        token_string += str(token_data["FailURL"])
    
    # OrderId
    if "OrderId" in token_data and token_data["OrderId"] is not None:
        token_string += str(token_data["OrderId"])
    
    # SuccessURL
    if "SuccessURL" in token_data and token_data["SuccessURL"] is not None:
        token_string += str(token_data["SuccessURL"])
    
    # TerminalKey
    if "TerminalKey" in token_data and token_data["TerminalKey"] is not None:
        token_string += str(token_data["TerminalKey"])
    
    # Password (секретный ключ)
    token_string += secret_key
    
    print(f"Строка для токена: {token_string}")
    
    # Создаем SHA-256 хеш
    token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    
    return token

def test_demo_terminal():
    """Тестирует тестовый терминал"""
    print("Тестирование тестового терминала T-Bank")
    print("=" * 50)
    
    # Тестовые данные с новым терминалом
    test_data = {
        "TerminalKey": "1761136519162DEMO",
        "Amount": 100,
        "OrderId": f"demo_test_{int(time.time())}",
        "Description": "Test payment with demo terminal",
        "SuccessURL": "https://hochupravaeasy.ru/success",
        "FailURL": "https://hochupravaeasy.ru/fail"
    }
    
    secret_key = "TY#iAnEUV*3CS&Bl"
    
    print("Тестовые данные:")
    for key, value in test_data.items():
        print(f"  {key}: {value}")
    print(f"  Secret Key: {secret_key}")
    print()
    
    # Генерируем токен
    token = create_correct_token(test_data, secret_key)
    test_data["Token"] = token
    
    print(f"Сгенерированный токен: {token}")
    print()
    
    # Тестируем API
    try:
        response = requests.post(
            "https://securepay.tinkoff.ru/v2/Init",
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Ответ сервера: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Результат: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get("Success"):
                print("УСПЕХ! Тестовый терминал работает!")
                return True
            else:
                print(f"Ошибка: {result.get('Message', 'Unknown error')}")
                print(f"Детали: {result.get('Details', 'No details')}")
                return False
        else:
            print(f"HTTP ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"Ошибка запроса: {str(e)}")
        return False

if __name__ == "__main__":
    test_demo_terminal()
