# Миграция на PostgreSQL

## Обзор

Приложение теперь использует PostgreSQL вместо JSON файла для хранения подписок. Это обеспечивает:
- Надежность и целостность данных
- Масштабируемость
- Производительность
- Транзакционность

## Настройка

### 1. Добавьте переменные в config.env

```env
# PostgreSQL настройки
DB_HOST=localhost
DB_PORT=5432
DB_NAME=easydrive
DB_USER=easydrive_user
DB_PASSWORD=your_secure_password_here
```

### 2. Для Docker (docker-compose.yml)

Переменные БД уже настроены в docker-compose.yml. Можно переопределить через переменные окружения:

```bash
export DB_NAME=easydrive
export DB_USER=easydrive_user
export DB_PASSWORD=your_password
docker-compose up -d
```

### 3. Миграция данных из JSON (только один раз!)

**Важно:** Скрипт миграции нужен только для переноса существующих данных из JSON в БД. После миграции все новые пользователи автоматически записываются в БД.

Если у вас есть данные в `paid_subscriptions.json`, выполните миграцию один раз:

```bash
# Локально
python migrate_to_db.py

# В Docker контейнере
docker-compose exec easydrive-server python migrate_to_db.py
```

После успешной миграции скрипт больше не нужен - все новые подписки автоматически сохраняются в PostgreSQL.

## Структура БД

### Таблица: paid_subscriptions

| Поле | Тип | Описание |
|------|-----|----------|
| user_id | VARCHAR(255) | Telegram user ID (PRIMARY KEY) |
| activated_at | TIMESTAMP | Дата и время активации |
| amount | DECIMAL(10,2) | Сумма оплаты |
| payment_method | VARCHAR(50) | Способ оплаты |
| status | VARCHAR(20) | Статус (active, expired, cancelled) |
| created_at | TIMESTAMP | Дата создания записи |
| updated_at | TIMESTAMP | Дата последнего обновления |

## Резервное копирование

### Экспорт данных

```bash
# Через Docker
docker-compose exec postgres pg_dump -U easydrive_user easydrive > backup.sql

# Локально
pg_dump -U easydrive_user -d easydrive > backup.sql
```

### Восстановление

```bash
# Через Docker
docker-compose exec -T postgres psql -U easydrive_user easydrive < backup.sql

# Локально
psql -U easydrive_user -d easydrive < backup.sql
```

## Важно

- **База данных НЕ отправляется на GitHub** (хранится в Docker volume)
- Данные сохраняются между перезапусками контейнеров
- Для production используйте надежные пароли
- Регулярно делайте резервные копии

## Управление через Docker

```bash
# Просмотр логов PostgreSQL
docker-compose logs postgres

# Вход в PostgreSQL
docker-compose exec postgres psql -U easydrive_user -d easydrive

# Остановка и удаление (данные сохраняются в volume)
docker-compose down

# Полное удаление с данными
docker-compose down -v
```

## Миграция существующих данных

Данные из `paid_subscriptions.json` автоматически мигрируются при первом запуске через скрипт `migrate_to_db.py`.

После успешной миграции файл `paid_subscriptions.json` можно удалить (данные уже в БД).

