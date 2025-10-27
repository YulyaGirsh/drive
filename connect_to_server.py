#!/usr/bin/env python3
"""
Автоматическое подключение к серверу по SSH
"""
import subprocess
import sys

host = "89.23.99.152"
username = "root"
password = "dJN.wJ-YM*+J9b"

print("🔌 Подключение к серверу...")
print(f"Хост: {host}")
print(f"Пользователь: {username}")
print()

# Команды для проверки
commands = [
    "cd /home/easydrive && pwd",
    "cd /home/easydrive && git status",
    "ps aux | grep 'python.*server.py' | grep -v grep",
    "cd /home/easydrive && grep -n 'def init_tbank_payment' server.py",
    "cd /home/easydrive && git log --oneline -3",
]

# Используем putty/plink если доступен, иначе обычный ssh
try:
    # Попробуем через plink (Putty)
    for cmd in commands:
        print("="*60)
        print(f"Выполняем: {cmd}")
        print("="*60)
        
        result = subprocess.run(
            ['plink', '-ssh', '-pw', password, f'{username}@{host}', cmd],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"Ошибка: {result.stderr}")
        print()
        
except FileNotFoundError:
    print("❌ plink не найден. Попробуем через обычный SSH...")
    
    # Альтернатива: используем ssh с паролем через stdin
    print("\nВыполняем команды через обычный SSH...")
    print("ПРИМЕЧАНИЕ: Потребуется ввести пароль вручную")
    
    # Первая команда
    cmd = "cd /home/easydrive && echo 'GIT STATUS:' && git status && echo '' && echo 'SERVER:' && ps aux | grep server.py | grep -v grep && echo '' && echo 'HANDLER:' && grep -n 'def init_tbank_payment' server.py && echo '' && echo 'COMMITS:' && git log --oneline -3"
    
    print(f"\nВыполните на сервере следующую команду:\n{cmd}\n")
    print("Или подключитесь так:")
    print(f"ssh {username}@{host}")
    print(f"Пароль: {password}")

