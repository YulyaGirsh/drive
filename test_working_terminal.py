#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тест с рабочим терминалом Т-банка
"""

import requests
import json
import time
import hashlib

def create_correct_token(data, secret_key):
    """Создает токен согласно официальной документации Т-банка"""
    token_data = {k: v for k, v in data.items() if k != "Token"}
    
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
    
    token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    
    return token

def test_working_terminal():
    """Тестирует рабочий терминал"""
    print("Тестирование рабочего терминала T-Bank")
    print("=" * 50)
    
    # Данные с рабочего терминала
    test_data = {
        "TerminalKey": "1761136519204",
        "Amount": 100,
        "OrderId": f"working_test_{int(time.time())}",
        "Description": "Test payment with working terminal",
        "SuccessURL": "https://hochupravaeasy.ru/success",
        "FailURL": "https://hochupravaeasy.ru/fail"
    }
    
    secret_key = "c^A3qE_zoaH0u%gP"
    
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
                print("✅ УСПЕХ! Рабочий терминал работает!")
                return True
            else:
                print(f"❌ Ошибка: {result.get('Message', 'Unknown error')}")
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
    test_working_terminal()
