#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Проверка URL настроек T-Bank
"""

def check_tbank_urls():
    """Проверяет правильность URL для T-Bank"""
    
    print("Проверка URL настроек T-Bank")
    print("=" * 50)
    
    # Текущие настройки из кода
    current_success_url = "https://hochupravaeasy.ru/success"
    current_fail_url = "https://hochupravaeasy.ru/fail"
    current_webhook_url = "https://hochupravaeasy.ru/api/tbank-webhook"
    
    # Что указано в настройках T-Bank (из скриншота)
    tbank_website = "t.me/easy_drive_study_bot"
    
    print("ТЕКУЩИЕ НАСТРОЙКИ В КОДЕ:")
    print(f"Success URL: {current_success_url}")
    print(f"Fail URL: {current_fail_url}")
    print(f"Webhook URL: {current_webhook_url}")
    print()
    
    print("НАСТРОЙКИ В T-BANK (из скриншота):")
    print(f"Сайт: {tbank_website}")
    print()
    
    print("ПРОБЛЕМА:")
    print("В настройках T-Bank указана ссылка на Telegram бота")
    print("А в коде используются URL мини-приложения")
    print("Это может быть причиной ошибки 204!")
    print()
    
    print("РЕШЕНИЕ:")
    print("1. В личном кабинете T-Bank нужно изменить:")
    print(f"   Сайт: {tbank_website}")
    print(f"   НА: https://hochupravaeasy.ru")
    print()
    print("2. Или изменить URL в коде на:")
    print(f"   Success URL: {tbank_website}/success")
    print(f"   Fail URL: {tbank_website}/fail")
    print()
    
    print("РЕКОМЕНДАЦИЯ:")
    print("Лучше изменить настройки в T-Bank на:")
    print("   Сайт: https://hochupravaeasy.ru")
    print("   Это позволит использовать мини-приложение для оплаты")

def test_url_accessibility():
    """Проверяет доступность URL"""
    import requests
    
    print("\nПроверка доступности URL:")
    print("-" * 30)
    
    urls_to_check = [
        "https://hochupravaeasy.ru/success",
        "https://hochupravaeasy.ru/fail", 
        "https://hochupravaeasy.ru/api/tbank-webhook",
        "https://hochupravaeasy.ru"
    ]
    
    for url in urls_to_check:
        try:
            response = requests.get(url, timeout=5)
            status = "Доступен" if response.status_code == 200 else f"Ошибка {response.status_code}"
            print(f"{url}: {status}")
        except Exception as e:
            print(f"{url}: Недоступен ({str(e)[:50]}...)")

if __name__ == "__main__":
    check_tbank_urls()
    test_url_accessibility()
