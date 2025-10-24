#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Исправление генерации токена T-Bank согласно ответу техподдержки
"""

import requests
import json
import time
import hashlib
from datetime import datetime
from tbank_config import REAL_CONFIG

def create_correct_token(data, secret_key):
    """
    Создает токен согласно официальной документации Т-банка
    """
    # Исключаем поле Token из генерации
    token_data = {k: v for k, v in data.items() if k != "Token"}
    
    # Сортируем ключи в алфавитном порядке
    sorted_keys = sorted(token_data.keys())
    
    # Создаем строку для токена согласно инструкции техподдержки:
    # "Все корневые объекты массива отсортированы в алфавитном порядке по ключу, 
    # и значения конкатенированы в одну строку"
    
    # Сортируем ключи в алфавитном порядке
    sorted_keys = sorted(token_data.keys())
    
    # Конкатенируем значения в алфавитном порядке ключей
    token_string = ""
    for key in sorted_keys:
        if token_data[key] is not None:
            token_string += str(token_data[key])
    
    # Добавляем секретный ключ в конец
    token_string += secret_key
    
    print(f"Строка для токена: {token_string}")
    
    # Создаем SHA-256 хеш
    token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
    
    return token, token_string

def test_corrected_token():
    """Тестирует исправленную генерацию токена"""
    print("Тестирование исправленной генерации токена T-Bank")
    print("=" * 60)
    
    # Тестовые данные (точно как в примере техподдержки)
    test_data = {
        "TerminalKey": "1761136519204",
        "Amount": 100,
        "OrderId": "test_1761296823",
        "Description": "Test payment",
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
    token, token_string = create_correct_token(test_data, secret_key)
    
    print(f"Сгенерированный токен: {token}")
    print()
    
    # Тестируем API
    test_data["Token"] = token
    
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
                print("Успешно! Токен работает корректно")
                return True
            else:
                print(f"Ошибка: {result.get('Message', 'Unknown error')}")
                return False
        else:
            print(f"HTTP ошибка: {response.status_code}")
            print(f"Ответ: {response.text}")
            return False
            
    except Exception as e:
        print(f"Ошибка запроса: {str(e)}")
        return False

def update_tbank_payment():
    """Обновляет tbank_payment.py с правильной генерацией токена"""
    print("Обновление tbank_payment.py...")
    
    # Читаем текущий файл
    with open('tbank_payment.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Заменяем функцию генерации токена
    old_function = '''    def _create_simple_token(self, data):
        """
        Создает упрощенный токен для T-Pay
        """
        # Согласно документации Т-банка, токен создается из полей в алфавитном порядке
        # Исключаем поле Token из генерации
        token_data = {k: v for k, v in data.items() if k != "Token"}
        
        # Сортируем ключи в алфавитном порядке
        sorted_keys = sorted(token_data.keys())
        
        # Создаем строку для токена
        token_string = ""
        for key in sorted_keys:
            if token_data[key] is not None:
                token_string += str(token_data[key])
        
        # Добавляем секретный ключ
        token_string += self.secret_key
        
        print(f"Строка для токена: {token_string}")
        
        # Создаем SHA-256 хеш
        token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
        
        return token'''
    
    new_function = '''    def _create_simple_token(self, data):
        """
        Создает токен согласно официальной документации Т-банка
        """
        # Исключаем поле Token из генерации
        token_data = {k: v for k, v in data.items() if k != "Token"}
        
        # Сортируем ключи в алфавитном порядке
        sorted_keys = sorted(token_data.keys())
        
        # Создаем строку для токена (только значения, без ключей)
        token_string = ""
        for key in sorted_keys:
            if token_data[key] is not None:
                token_string += str(token_data[key])
        
        # Добавляем секретный ключ в конец
        token_string += self.secret_key
        
        print(f"Строка для токена: {token_string}")
        
        # Создаем SHA-256 хеш
        token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
        
        return token'''
    
    # Заменяем функцию
    updated_content = content.replace(old_function, new_function)
    
    # Сохраняем обновленный файл
    with open('tbank_payment.py', 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("tbank_payment.py обновлен")

def main():
    """Основная функция"""
    print("Исправление генерации токена T-Bank")
    print("=" * 60)
    
    # Тестируем исправленную генерацию
    success = test_corrected_token()
    
    if success:
        print("\nТокен работает корректно!")
        # Обновляем tbank_payment.py
        update_tbank_payment()
    else:
        print("\nТокен все еще не работает, нужна дополнительная диагностика")
    
    return success

if __name__ == "__main__":
    main()
