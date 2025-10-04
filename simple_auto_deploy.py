#!/usr/bin/env python3
"""
Упрощенный автоматический деплой для EasyDrive приложения
Только git push без SSH подключения к серверу
"""

import subprocess
import sys
import os
import time
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Конфигурация
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

def show_manual_instructions():
    """Показывает инструкции для ручного обновления сервера"""
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

class DeployHandler(FileSystemEventHandler):
    """Обработчик изменений файлов для автоматического деплоя"""
    
    def __init__(self):
        self.last_deploy = 0
        self.deploy_delay = 3  # Задержка между деплоями в секундах
        self.ignored_extensions = {'.pyc', '.pyo', '.pyd', '.log', '.tmp', '.swp', '.DS_Store'}
        self.ignored_dirs = {'.git', '__pycache__', 'node_modules', '.vscode', '.idea'}
    
    def should_ignore(self, path):
        """Проверяет, нужно ли игнорировать файл"""
        # Игнорируем скрытые файлы и папки
        if any(part.startswith('.') for part in path.split(os.sep)):
            return True
        
        # Игнорируем определенные расширения
        if any(path.endswith(ext) for ext in self.ignored_extensions):
            return True
        
        # Игнорируем определенные папки
        if any(ignored_dir in path for ignored_dir in self.ignored_dirs):
            return True
        
        return False
    
    def on_modified(self, event):
        """Обрабатывает изменения файлов"""
        if event.is_directory:
            return
        
        if self.should_ignore(event.src_path):
            return
        
        current_time = time.time()
        if current_time - self.last_deploy < self.deploy_delay:
            return
        
        print(f"\n📁 Изменен файл: {event.src_path}")
        print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        
        self.last_deploy = current_time
        self.deploy()
    
    def on_created(self, event):
        """Обрабатывает создание новых файлов"""
        if event.is_directory:
            return
        
        if self.should_ignore(event.src_path):
            return
        
        current_time = time.time()
        if current_time - self.last_deploy < self.deploy_delay:
            return
        
        print(f"\n📁 Создан файл: {event.src_path}")
        print(f"⏰ Время: {datetime.now().strftime('%H:%M:%S')}")
        
        self.last_deploy = current_time
        self.deploy()
    
    def deploy(self):
        """Запускает процесс деплоя"""
        print("🚀 Запуск автоматического деплоя...")
        
        # Git операции
        if not git_add_and_commit():
            print("⚠️ Нет изменений для коммита")
            return
        
        if not git_push():
            print("❌ Ошибка git push")
            return
        
        print("✅ Деплой завершен успешно!")
        print("💡 Обновите сервер вручную при необходимости")
        show_manual_instructions()

def main():
    """Основная функция мониторинга"""
    print("👀 Запуск автоматического мониторинга изменений...")
    print("📁 Отслеживаемые файлы: .html, .css, .js, .py (кроме служебных)")
    print("🔄 Деплой будет запускаться автоматически при изменениях")
    print("⏹️  Для остановки нажмите Ctrl+C")
    print("-" * 60)
    
    # Создаем обработчик событий
    event_handler = DeployHandler()
    observer = Observer()
    
    # Настраиваем наблюдение за текущей директорией
    observer.schedule(event_handler, ".", recursive=True)
    
    # Запускаем наблюдение
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️ Остановка мониторинга...")
        observer.stop()
    
    observer.join()
    print("👋 Мониторинг остановлен")

if __name__ == "__main__":
    main()
