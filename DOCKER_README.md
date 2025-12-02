# Docker контейнеризация EasyDrive

## Быстрый старт

### 1. Сборка и запуск через docker-compose (рекомендуется)

```bash
# Сборка и запуск
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### 2. Ручная сборка и запуск

```bash
# Сборка образа
docker build -t easydrive:latest .

# Запуск контейнера
docker run -d \
  --name easydrive-server \
  -p 8000:8000 \
  -v $(pwd)/config.env:/app/config.env:ro \
  -v $(pwd)/paid_subscriptions.json:/app/paid_subscriptions.json \
  -v $(pwd)/images:/app/images:ro \
  -v $(pwd)/data.json:/app/data.json:ro \
  easydrive:latest
```

## Конфигурация

### Переменные окружения

Файл `config.env` должен содержать:
```env
BOT_TOKEN=your_bot_token
RECIPIENT_ID=your_admin_chat_id
TBANK_TERMINAL_KEY=your_terminal_key
TBANK_SECRET_KEY=your_secret_key
# ... другие настройки
```

**Важно:** Файл `config.env` монтируется как read-only (`:ro`) для безопасности.

## Volumes (тома)

Docker-compose автоматически монтирует:
- `config.env` - конфигурация (read-only)
- `paid_subscriptions.json` - данные подписок (read-write)
- `translation_data.json` - данные трансляций (read-write)
- `images/` - изображения (read-only)
- `conspects/` - PDF конспекты (read-only)
- `data.json` и другие JSON с вопросами (read-only)

## Полезные команды

```bash
# Пересборка образа
docker-compose build --no-cache

# Перезапуск контейнера
docker-compose restart

# Просмотр статуса
docker-compose ps

# Вход в контейнер
docker-compose exec easydrive-server bash

# Просмотр логов
docker-compose logs -f easydrive-server

# Остановка и удаление
docker-compose down

# Остановка и удаление с volumes
docker-compose down -v
```

## Health Check

Контейнер имеет встроенную проверку здоровья через endpoint `/api/v2/heartbeat`. Проверка выполняется каждые 30 секунд.

## Проблемы и решения

### Порт уже занят

Если порт 8000 занят, измените в `docker-compose.yml`:
```yaml
ports:
  - "8001:8000"  # Внешний:Внутренний
```

### Ошибка при монтировании файлов

Убедитесь, что файлы существуют:
```bash
touch paid_subscriptions.json translation_data.json
```

### Проблемы с правами доступа

На Linux/Mac может потребоваться:
```bash
chmod 644 config.env
chmod 666 paid_subscriptions.json
```

## Production

Для production рекомендуется:
1. Использовать переменные окружения вместо файла config.env
2. Настроить reverse proxy (nginx) перед контейнером
3. Использовать Docker secrets для чувствительных данных
4. Настроить логирование в отдельный volume
5. Использовать health checks для автоматического перезапуска

### Пример с переменными окружения:

```yaml
environment:
  - BOT_TOKEN=${BOT_TOKEN}
  - RECIPIENT_ID=${RECIPIENT_ID}
  - TBANK_TERMINAL_KEY=${TBANK_TERMINAL_KEY}
  - TBANK_SECRET_KEY=${TBANK_SECRET_KEY}
```

## Обновление

```bash
# Остановить контейнер
docker-compose down

# Обновить код (git pull)

# Пересобрать и запустить
docker-compose up -d --build
```

