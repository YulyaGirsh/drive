-- SQL скрипт для загрузки данных подписок в PostgreSQL
-- Используйте этот файл для загрузки данных на сервер
-- 
-- Использование:
-- psql -U easydrive_user -d easydrive -f load_data.sql
-- или через Docker:
-- docker-compose exec -T postgres psql -U easydrive_user -d easydrive < load_data.sql

-- Вставляем данные из paid_subscriptions.json
-- Данные из файла (user_id: 653478834, 123456789)

INSERT INTO paid_subscriptions (user_id, activated_at, amount, payment_method, status)
VALUES 
    ('653478834', '2025-11-04 00:02:02', 10.0, 'tbank', 'active'),
    ('123456789', '2025-11-03 23:32:34', 10.0, 'tbank', 'active')
ON CONFLICT (user_id) 
DO UPDATE SET 
    activated_at = EXCLUDED.activated_at,
    amount = EXCLUDED.amount,
    payment_method = EXCLUDED.payment_method,
    status = EXCLUDED.status,
    updated_at = CURRENT_TIMESTAMP;

-- Проверяем результат
SELECT * FROM paid_subscriptions ORDER BY activated_at DESC;

