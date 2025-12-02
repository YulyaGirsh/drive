#!/usr/bin/env python3
"""
Скрипт для миграции данных из paid_subscriptions.json в PostgreSQL
"""
import os
import sys
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import database

def main():
    """Основная функция миграции"""
    logger.info("Начало миграции данных из JSON в PostgreSQL")
    
    # Инициализируем БД
    if not database.init_db_pool():
        logger.error("Не удалось инициализировать пул соединений с БД")
        return False
    
    if not database.init_database():
        logger.error("Не удалось инициализировать структуру БД")
        return False
    
    # Мигрируем данные
    json_file = 'paid_subscriptions.json'
    if not os.path.exists(json_file):
        logger.warning(f"Файл {json_file} не найден. Пропускаем миграцию.")
        return True
    
    success = database.migrate_from_json(json_file)
    
    if success:
        logger.info("Миграция завершена успешно!")
        logger.info("Теперь можно удалить файл paid_subscriptions.json (данные в БД)")
    else:
        logger.error("Ошибка при миграции данных")
    
    # Закрываем пул соединений
    database.close_db_pool()
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

