#!/usr/bin/env python3
"""
Автоматический мониторинг изменений файлов и деплой
Запускает деплой при каждом изменении файлов проекта
"""

import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class DeployHandler(FileSystemEventHandler):
    """Обработчик изменений файлов для автоматического деплоя"""
    
    def __init__(self):
        self.last_deploy = 0
        self.deploy_delay = 5  # Задержка между деплоями в секундах
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
    
    def deploy(self):
        """Запускает процесс деплоя"""
        print("🚀 Запуск автоматического деплоя...")
        try:
            result = subprocess.run([sys.executable, "deploy.py"], 
                                  capture_output=True, text=True, timeout=60)
            if result.returncode == 0:
                print("✅ Деплой завершен успешно!")
            else:
                print(f"❌ Ошибка деплоя: {result.stderr}")
        except subprocess.TimeoutExpired:
            print("⏰ Таймаут деплоя")
        except Exception as e:
            print(f"❌ Ошибка запуска деплоя: {e}")

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
    import sys
    main()
