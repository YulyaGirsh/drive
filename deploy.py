#!/usr/bin/env python3
"""
Автоматический скрипт деплоя для EasyDrive приложения
Автоматически пушит изменения в git и обновляет код на сервере
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
SERVER_PATH = "/var/www/easydrive"  # Путь к проекту на сервере

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

def update_server():
    """Обновляет код на сервере через SSH"""
    print("🔄 Обновляем код на сервере...")
    
    # Команды для выполнения на сервере
    commands = [
        f"cd {SERVER_PATH}",
        "git pull origin main",
        "sudo systemctl reload nginx",  # Перезагружаем nginx для сброса кеша
        "echo 'Deploy completed successfully'"
    ]
    
    # Объединяем команды
    ssh_command = f"sshpass -p '{SERVER_PASSWORD}' ssh -o StrictHostKeyChecking=no {SERVER_USER}@{SERVER_HOST} '{';'.join(commands)}'"
    
    success, output = run_command(ssh_command)
    if not success:
        print(f"❌ Ошибка при обновлении сервера: {output}")
        return False
    
    print("✅ Сервер успешно обновлен")
    print(f"📋 Вывод сервера: {output}")
    return True

def check_sshpass():
    """Проверяет наличие sshpass"""
    success, _ = run_command("which sshpass")
    if not success:
        print("❌ sshpass не найден. Устанавливаем...")
        success, output = run_command("sudo apt-get update && sudo apt-get install -y sshpass")
        if not success:
            print(f"❌ Ошибка установки sshpass: {output}")
            return False
    return True

def main():
    """Основная функция деплоя"""
    print("🚀 Запуск автоматического деплоя EasyDrive...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 50)
    
    # Проверяем sshpass
    if not check_sshpass():
        sys.exit(1)
    
    # Этап 1: Git операции
    if not git_add_and_commit():
        print("⚠️ Нет изменений для коммита или ошибка git")
        return
    
    if not git_push():
        sys.exit(1)
    
    # Этап 2: Обновление сервера
    if not update_server():
        sys.exit(1)
    
    print("-" * 50)
    print("🎉 Деплой завершен успешно!")
    print(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
