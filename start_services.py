#!/usr/bin/env python3
"""
Скрипт для запуска веб-сервера и бота одновременно
"""
import subprocess
import sys
import time
import os
from threading import Thread

def run_server():
    """Запускает веб-сервер"""
    print("🌐 Запускаем веб-сервер...")
    subprocess.run([sys.executable, "server.py"])

def run_bot():
    """Запускает Telegram бота"""
    print("🤖 Запускаем Telegram бота...")
    subprocess.run([sys.executable, "bot.py"])

if __name__ == "__main__":
    print("🚀 Запуск сервисов EasyDrive...")
    
    # Запускаем веб-сервер в отдельном потоке
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()
    
    # Ждем немного, чтобы сервер запустился
    time.sleep(2)
    
    # Запускаем бота в основном потоке
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n🛑 Остановка сервисов...")
        sys.exit(0)
