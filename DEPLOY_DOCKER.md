# Команды для деплоя на сервер с Docker

## 1. Подключение к серверу
```bash
ssh user@your-server
cd /path/to/drive-main
```

## 2. Решение проблемы с git pull (если есть незакоммиченные изменения)

### Вариант А: Сохранить изменения во временное хранилище (stash)
```bash
git stash
git pull origin main
git stash pop  # Вернуть изменения обратно (если нужно)
```

### Вариант Б: Закоммитить изменения
```bash
git add -A
git commit -m "Локальные изменения перед обновлением"
git pull origin main
```

### Вариант В: Отменить локальные изменения (если они не нужны)
```bash
git reset --hard HEAD
git pull origin main
```

## 3. Остановка старого приложения

### Найти процесс Python (если запущен напрямую)
```bash
# Найти процесс на порту 8000
sudo lsof -i :8000
# Или
sudo netstat -tulpn | grep :8000

# Остановить процесс по PID
sudo kill <PID>

# Или найти и остановить все процессы python server.py
ps aux | grep "server.py" | grep -v grep
sudo killall python3  # Осторожно! Остановит все Python процессы
```

### Если используется systemd/supervisor
```bash
# Для systemd
sudo systemctl stop easydrive
# Или
sudo systemctl stop drive-server

# Для supervisor
sudo supervisorctl stop easydrive
```

### Если используется screen/tmux
```bash
# Найти сессии
screen -ls
# Или
tmux ls

# Остановить сессию
screen -S session_name -X quit
# Или
tmux kill-session -t session_name
```

## 4. Установка Docker и Docker Compose (если не установлены)

```bash
# Обновление пакетов
sudo apt update

# Установка Docker
sudo apt install -y docker.io docker-compose

# Добавить пользователя в группу docker (чтобы не использовать sudo)
sudo usermod -aG docker $USER
# Выйти и зайти снова, чтобы изменения вступили в силу
```

## 5. Сборка и запуск Docker контейнеров

### Вариант А: Используя Makefile (рекомендуется)
```bash
# Полная пересборка и запуск
make rebuild

# Или пошагово:
make down      # Остановить старые контейнеры
make build     # Собрать образы
make up        # Запустить контейнеры
```

### Вариант Б: Используя docker-compose напрямую
```bash
# Остановить и удалить старые контейнеры
docker-compose down

# Собрать образы (без кэша для чистой сборки)
docker-compose build --no-cache

# Запустить контейнеры в фоновом режиме
docker-compose up -d

# Или одной командой (остановить, собрать, запустить)
docker-compose down && docker-compose build --no-cache && docker-compose up -d
```

## 6. Проверка статуса

```bash
# Статус контейнеров
docker-compose ps

# Или через Makefile
make status

# Просмотр логов
docker-compose logs -f

# Или через Makefile
make logs
```

## 7. Проверка работы приложения

```bash
# Проверить, что сервер отвечает
curl http://localhost:8000/api/v2/heartbeat

# Или открыть в браузере
# http://your-server-ip:8000
```

## 8. Полезные команды

```bash
# Перезапуск контейнеров
make restart
# Или
docker-compose restart

# Просмотр логов только сервера
docker-compose logs -f easydrive-server

# Просмотр логов только БД
docker-compose logs -f postgres

# Войти в контейнер сервера
make shell
# Или
docker-compose exec easydrive-server bash

# Остановка всех контейнеров
make down
# Или
docker-compose down

# Полная очистка (удалить контейнеры, образы, volumes)
make clean
# ВНИМАНИЕ: Это удалит данные БД!
```

## 9. Обновление приложения (после изменений в коде)

```bash
# На сервере
cd /path/to/drive-main

# Решить проблему с git (если есть)
git stash  # или git commit

# Получить последние изменения
git pull origin main

# Пересобрать и перезапустить
make rebuild
# Или
docker-compose down && docker-compose build && docker-compose up -d
```

## 10. Настройка автозапуска (опционально)

### Создать systemd сервис для автозапуска Docker Compose

```bash
sudo nano /etc/systemd/system/easydrive.service
```

Содержимое файла:
```ini
[Unit]
Description=EasyDrive Docker Compose
Requires=docker.service
After=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/drive-main
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down
User=your-username

[Install]
WantedBy=multi-user.target
```

Затем:
```bash
sudo systemctl daemon-reload
sudo systemctl enable easydrive
sudo systemctl start easydrive
```

## Важные замечания

1. **config.env** должен быть на сервере с правильными настройками
2. **База данных** хранится в Docker volume `postgres_data` - данные сохраняются при перезапуске контейнеров
3. **Порт 8000** должен быть открыт в firewall
4. **Логи** можно просматривать через `docker-compose logs -f`

