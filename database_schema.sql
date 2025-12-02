-- Схема базы данных для EasyDrive
-- Этот файл для справки, структура создается автоматически через database.py

-- Таблица подписок
CREATE TABLE IF NOT EXISTS paid_subscriptions (
    user_id VARCHAR(255) PRIMARY KEY,
    activated_at TIMESTAMP NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id 
ON paid_subscriptions(user_id);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status 
ON paid_subscriptions(status);

-- Комментарии к таблице
COMMENT ON TABLE paid_subscriptions IS 'Таблица оплаченных подписок пользователей';
COMMENT ON COLUMN paid_subscriptions.user_id IS 'Telegram user ID';
COMMENT ON COLUMN paid_subscriptions.activated_at IS 'Дата и время активации подписки';
COMMENT ON COLUMN paid_subscriptions.amount IS 'Сумма оплаты';
COMMENT ON COLUMN paid_subscriptions.payment_method IS 'Способ оплаты (tbank, card и т.д.)';
COMMENT ON COLUMN paid_subscriptions.status IS 'Статус подписки (active, expired, cancelled)';

