#!/usr/bin/env python3
"""
Автоматический скрипт деплоя для EasyDrive приложения (Windows версия)
Использует plink (PuTTY) для SSH подключения
"""

import subprocess
import sys
import os
import time
from datetime import datetime

# Конфигурация сервера
SERVER_HOST = "89.23.99.152"
SERVER_USER = "root"
SERVER_PASSWORD = "dJN.wJ-YM*+J9b"
SERVER_PATH = "/var/www/easydrive"

def run_command(command, cwd=None):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def git_add_and_commit():
    """Добавляет все изменения в git и создает коммит"""
    print("📝 Добавляем изменения в git...")
    
    # Добавляем все файлы
    success, output = run_command("git add .")
    if not success:
        print(f"❌ Ошибка при добавлении файлов: {output}")
        return False
    
    # Создаем коммит с текущим временем
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_message = f"Auto-deploy: {timestamp}"
    
    success, output = run_command(f'git commit -m "{commit_message}"')
    if not success and "nothing to commit" not in output.lower():
        print(f"❌ Ошибка при создании коммита: {output}")
        return False
    
    print("✅ Изменения добавлены в git")
    return True

def git_push():
    """Пушит изменения в удаленный репозиторий"""
    print("🚀 Отправляем изменения в git...")
    
    success, output = run_command("git push origin main")
    if not success:
        print(f"❌ Ошибка при push: {output}")
        return False
    
    print("✅ Изменения отправлены в git")
    return True

def check_plink():
    """Проверяет наличие plink (PuTTY)"""
    success, _ = run_command("plink -V")
    if not success:
        print("❌ plink не найден. Скачайте PuTTY с https://www.putty.org/")
        print("📁 Распакуйте plink.exe в папку с проектом или добавьте в PATH")
        return False
    return True

def update_server_plink():
    """Обновляет код на сервере через plink (PuTTY)"""
    print("🔄 Обновляем код на сервере через plink...")
    
    # Команды для выполнения на сервере
    commands = [
        f"cd {SERVER_PATH}",
        "git pull origin main",
        "sudo systemctl reload nginx",
        "echo 'Deploy completed successfully'"
    ]
    
    # Создаем временный файл с командами
    script_file = "server_commands.sh"
    with open(script_file, 'w') as f:
        f.write('\n'.join(commands))
    
    try:
        # Выполняем команды через plink
        plink_command = f'plink -ssh -pw "{SERVER_PASSWORD}" {SERVER_USER}@{SERVER_HOST} -m {script_file}'
        
        success, output = run_command(plink_command)
        if not success:
            print(f"❌ Ошибка при обновлении сервера: {output}")
            return False
        
        print("✅ Сервер успешно обновлен")
        print(f"📋 Вывод сервера: {output}")
        return True
    
    finally:
        # Удаляем временный файл
        if os.path.exists(script_file):
            os.remove(script_file)

def update_server_wsl():
    """Обновляет код на сервере через WSL"""
    print("🔄 Обновляем код на сервере через WSL...")
    
    # Команды для выполнения на сервере через WSL
    commands = [
        f"cd {SERVER_PATH}",
        "git pull origin main",
        "sudo systemctl reload nginx",
        "echo 'Deploy completed successfully'"
    ]
    
    # Объединяем команды для WSL
    wsl_command = f"wsl sshpass -p '{SERVER_PASSWORD}' ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_HOST} '{';'.join(commands)}'"
    
    success, output = run_command(wsl_command)
    if not success:
        print(f"❌ Ошибка при обновлении сервера: {output}")
        return False
    
    print("✅ Сервер успешно обновлен")
    print(f"📋 Вывод сервера: {output}")
    return True

def update_server():
    """Пытается обновить сервер разными способами"""
    print("🔄 Пытаемся подключиться к серверу...")
    
    # Сначала пробуем WSL
    print("1️⃣ Пробуем WSL...")
    success, output = run_command("wsl --version")
    if success:
        print("✅ WSL найден, пробуем через WSL...")
        if update_server_wsl():
            return True
        print("⚠️ WSL не сработал, пробуем plink...")
    
    # Потом пробуем plink
    print("2️⃣ Пробуем plink...")
    if check_plink():
        if update_server_plink():
            return True
    
    print("❌ Не удалось подключиться к серверу")
    print("💡 Установите WSL или скачайте PuTTY (plink.exe)")
    return False

def main():
    """Основная функция деплоя"""
    print("🚀 Запуск автоматического деплоя EasyDrive (Windows)...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Этап 1: Git операции
    if not git_add_and_commit():
        print("⚠️ Нет изменений для коммита или ошибка git")
        return
    
    if not git_push():
        sys.exit(1)
    
    # Этап 2: Обновление сервера
    if not update_server():
        print("⚠️ Не удалось обновить сервер, но git push выполнен успешно")
        print("💡 Обновите сервер вручную: git pull origin main")
        return
    
    print("-" * 50)
    print("🎉 Деплой завершен успешно!")
    print(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
