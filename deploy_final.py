#!/usr/bin/env python3
"""
Финальный скрипт автоматического деплоя для EasyDrive приложения
Поддерживает Windows (WSL) и Linux
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

def check_wsl():
    """Проверяет наличие WSL"""
    success, _ = run_command("wsl --version")
    return success

def check_sshpass():
    """Проверяет наличие sshpass в WSL"""
    success, _ = run_command("wsl which sshpass")
    return success

def install_sshpass():
    """Устанавливает sshpass в WSL"""
    print("📦 Устанавливаем sshpass в WSL...")
    commands = [
        "sudo apt-get update",
        "sudo apt-get install -y sshpass"
    ]
    
    for cmd in commands:
        success, output = run_command(f"wsl {cmd}")
        if not success:
            print(f"❌ Ошибка установки sshpass: {output}")
            return False
    
    print("✅ sshpass установлен")
    return True

def update_server_wsl():
    """Обновляет код на сервере через WSL"""
    print("🔄 Обновляем код на сервере через WSL...")
    
    # Команды для выполнения на сервере
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

def update_server_linux():
    """Обновляет код на сервере (Linux)"""
    print("🔄 Обновляем код на сервере...")
    
    # Команды для выполнения на сервере
    commands = [
        f"cd {SERVER_PATH}",
        "git pull origin main",
        "sudo systemctl reload nginx",
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

def update_server():
    """Пытается обновить сервер разными способами"""
    print("🔄 Пытаемся подключиться к серверу...")
    
    # Проверяем WSL (Windows)
    if check_wsl():
        print("✅ WSL найден, используем WSL...")
        
        # Проверяем sshpass в WSL
        if not check_sshpass():
            print("📦 Устанавливаем sshpass в WSL...")
            if not install_sshpass():
                print("❌ Не удалось установить sshpass")
                return False
        
        return update_server_wsl()
    
    # Проверяем sshpass (Linux)
    else:
        print("🐧 Linux система, проверяем sshpass...")
        success, _ = run_command("which sshpass")
        if not success:
            print("📦 Устанавливаем sshpass...")
            success, output = run_command("sudo apt-get update && sudo apt-get install -y sshpass")
            if not success:
                print(f"❌ Ошибка установки sshpass: {output}")
                return False
        
        return update_server_linux()

def show_manual_instructions():
    """Показывает инструкции для ручного обновления"""
    print("\n" + "="*60)
    print("📋 РУЧНОЕ ОБНОВЛЕНИЕ СЕРВЕРА:")
    print("="*60)
    print("1. Подключитесь к серверу:")
    print(f"   ssh {SERVER_USER}@{SERVER_HOST}")
    print("2. Перейдите в папку проекта:")
    print(f"   cd {SERVER_PATH}")
    print("3. Обновите код:")
    print("   git pull origin main")
    print("4. Перезагрузите nginx:")
    print("   sudo systemctl reload nginx")
    print("="*60)
    print(f"🔑 Пароль для подключения: {SERVER_PASSWORD}")
    print("="*60)

def main():
    """Основная функция деплоя"""
    print("🚀 Запуск автоматического деплоя EasyDrive...")
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
        print("⚠️ Не удалось автоматически обновить сервер")
        show_manual_instructions()
        return
    
    print("-" * 50)
    print("🎉 Деплой завершен успешно!")
    print(f"⏰ Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
