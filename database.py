"""
Модуль для работы с PostgreSQL базой данных
"""
import psycopg2
import psycopg2.extras
from psycopg2 import pool
from contextlib import contextmanager
from config import DB_CONFIG
import logging

logger = logging.getLogger(__name__)

# Пул соединений
connection_pool = None


def init_db_pool():
    """Инициализирует пул соединений с БД"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1,  # Минимум соединений
            10,  # Максимум соединений
            **DB_CONFIG
        )
        if connection_pool:
            logger.info("Пул соединений с БД успешно создан")
            return True
    except Exception as e:
        logger.error(f"Ошибка при создании пула соединений: {e}")
        return False


@contextmanager
def get_db_connection():
    """Контекстный менеджер для получения соединения с БД"""
    global connection_pool
    conn = None
    try:
        if connection_pool:
            conn = connection_pool.getconn()
            yield conn
            conn.commit()
        else:
            # Fallback: прямое соединение
            conn = psycopg2.connect(**DB_CONFIG)
            yield conn
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"Ошибка при работе с БД: {e}")
        raise
    finally:
        if conn:
            if connection_pool:
                connection_pool.putconn(conn)
            else:
                conn.close()


def init_database():
    """Инициализирует структуру БД (создает таблицы)"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Создаем таблицу подписок
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS paid_subscriptions (
                        user_id VARCHAR(255) PRIMARY KEY,
                        activated_at TIMESTAMP NOT NULL,
                        amount DECIMAL(10, 2) NOT NULL,
                        payment_method VARCHAR(50) NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'active',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                
                # Создаем индекс для быстрого поиска
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id 
                    ON paid_subscriptions(user_id);
                """)
                
                # Создаем индекс для поиска по статусу
                cur.execute("""
                    CREATE INDEX IF NOT EXISTS idx_subscriptions_status 
                    ON paid_subscriptions(status);
                """)
                
                logger.info("Структура БД успешно инициализирована")
                return True
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        return False


def check_user_subscription(user_id):
    """Проверяет, есть ли у пользователя активная подписка"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM paid_subscriptions 
                    WHERE user_id = %s AND status = 'active'
                """, (str(user_id),))
                
                result = cur.fetchone()
                return result is not None
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}")
        return False


def activate_subscription(user_id, amount, payment_method):
    """Активирует подписку для пользователя"""
    try:
        from utils import get_current_timestamp
        
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Используем INSERT ... ON CONFLICT для обновления существующей записи
                cur.execute("""
                    INSERT INTO paid_subscriptions 
                    (user_id, activated_at, amount, payment_method, status, updated_at)
                    VALUES (%s, %s, %s, %s, 'active', CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        activated_at = EXCLUDED.activated_at,
                        amount = EXCLUDED.amount,
                        payment_method = EXCLUDED.payment_method,
                        status = 'active',
                        updated_at = CURRENT_TIMESTAMP
                """, (str(user_id), get_current_timestamp(), float(amount), payment_method))
                
                logger.info(f"Подписка активирована для пользователя {user_id}")
                return True
    except Exception as e:
        logger.error(f"Ошибка при активации подписки: {e}")
        return False


def get_subscription(user_id):
    """Получает информацию о подписке пользователя"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM paid_subscriptions 
                    WHERE user_id = %s
                """, (str(user_id),))
                
                return cur.fetchone()
    except Exception as e:
        logger.error(f"Ошибка при получении подписки: {e}")
        return None


def migrate_from_json(json_file_path='paid_subscriptions.json'):
    """Мигрирует данные из JSON файла в PostgreSQL"""
    import json
    from utils import load_json_file
    
    try:
        subscriptions = load_json_file(json_file_path, default={})
        
        if not subscriptions:
            logger.info("Нет данных для миграции")
            return True
        
        migrated_count = 0
        for user_id, subscription_data in subscriptions.items():
            try:
                success = activate_subscription(
                    user_id,
                    subscription_data.get('amount', 0),
                    subscription_data.get('payment_method', 'unknown')
                )
                if success:
                    migrated_count += 1
            except Exception as e:
                logger.error(f"Ошибка при миграции подписки для {user_id}: {e}")
        
        logger.info(f"Мигрировано {migrated_count} подписок из JSON")
        return True
    except Exception as e:
        logger.error(f"Ошибка при миграции данных: {e}")
        return False


def close_db_pool():
    """Закрывает пул соединений"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("Пул соединений закрыт")

