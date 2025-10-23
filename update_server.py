#!/usr/bin/env python3
"""
Простой скрипт для обновления сервера EasyDrive
"""

import subprocess
import sys
import time

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            if result.stdout.strip():
                print(f"📄 Вывод: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - ошибка")
            print(f"📄 Ошибка: {result.stderr.strip()}")
            return False
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - таймаут")
        return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False
    return True

def main():
    print("🚀 Обновление сервера EasyDrive...")
    print("=" * 50)
    
    # Команды для обновления сервера
    commands = [
        ("git add .", "Добавление изменений в git"),
        ("git commit -m \"Auto-update from local\"", "Создание коммита"),
        ("git push origin main", "Отправка изменений на GitHub"),
    ]
    
    # Выполняем команды локально
    for command, description in commands:
        if not run_command(command, description):
            print("❌ Ошибка при выполнении локальных команд")
            return
    
    print("\n" + "=" * 50)
    print("📋 Инструкции для ручного обновления сервера:")
    print("=" * 50)
    print("1. Подключитесь к серверу:")
    print("   ssh root@89.23.99.152")
    print("   Пароль: dJN.wJ-YM*+J9b")
    print()
    print("2. Перейдите в папку проекта:")
    print("   cd /home/easydrive")
    print()
    print("3. Обновите код:")
    print("   git pull origin main")
    print()
    print("4. Перезагрузите nginx:")
    print("   sudo systemctl reload nginx")
    print()
    print("5. Проверьте статус сервера:")
    print("   sudo systemctl status nginx")
    print("   ps aux | grep python")
    print()
    print("✅ Инструкции готовы!")
    print("=" * 50)

if __name__ == "__main__":
    main()
