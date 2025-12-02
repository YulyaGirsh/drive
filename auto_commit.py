#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для автоматического коммита изменений в Git с русским комментарием
"""
import subprocess
import sys
import os
from datetime import datetime

def get_git_status():
    """Получает статус изменений в git"""
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, encoding='utf-8')
        return result.stdout.strip()
    except Exception as e:
        print(f"Ошибка при получении статуса git: {e}")
        return None

def get_changed_files():
    """Получает список измененных файлов"""
    try:
        result = subprocess.run(['git', 'diff', '--name-only'], 
                              capture_output=True, text=True, encoding='utf-8')
        staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], 
                              capture_output=True, text=True, encoding='utf-8')
        files = (result.stdout + staged.stdout).strip().split('\n')
        return [f for f in files if f]
    except Exception as e:
        print(f"Ошибка при получении списка файлов: {e}")
        return []

def create_commit_message(custom_message=None):
    """Создает сообщение коммита"""
    if custom_message:
        return custom_message
    
    changed_files = get_changed_files()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if changed_files:
        files_list = ', '.join(changed_files[:3])  # Первые 3 файла
        if len(changed_files) > 3:
            files_list += f" и еще {len(changed_files) - 3} файлов"
        message = f"Обновление: Изменены файлы ({files_list}) - {timestamp}"
    else:
        message = f"Обновление: Изменения в коде - {timestamp}"
    
    return message

def auto_commit(message=None, push=False):
    """Выполняет автоматический коммит"""
    # Проверяем, есть ли изменения
    status = get_git_status()
    if not status:
        print("Нет изменений для коммита")
        return False
    
    # Добавляем все изменения
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        print("✓ Файлы добавлены в индекс")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при добавлении файлов: {e}")
        return False
    
    # Создаем сообщение коммита
    commit_message = create_commit_message(message)
    
    # Делаем коммит
    try:
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        print(f"✓ Коммит создан: {commit_message}")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при создании коммита: {e}")
        return False
    
    # Пушим, если нужно
    if push:
        try:
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            print("✓ Изменения отправлены на GitHub")
        except subprocess.CalledProcessError as e:
            print(f"Ошибка при отправке на GitHub: {e}")
            return False
    
    return True

if __name__ == '__main__':
    # Проверяем аргументы командной строки
    custom_message = None
    push = False
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--push' or sys.argv[1] == '-p':
            push = True
            if len(sys.argv) > 2:
                custom_message = ' '.join(sys.argv[2:])
        elif sys.argv[1] == '--help' or sys.argv[1] == '-h':
            print("Использование:")
            print("  python auto_commit.py              - коммит без пуша")
            print("  python auto_commit.py --push       - коммит и пуш")
            print("  python auto_commit.py -p 'Сообщение' - коммит с сообщением и пуш")
            sys.exit(0)
        else:
            custom_message = ' '.join(sys.argv[1:])
    
    success = auto_commit(custom_message, push)
    sys.exit(0 if success else 1)

