# Инструкция по подключению к серверу и деплою

## Вариант 1: Загрузить скрипт и выполнить на сервере

### Шаг 1: Подключиться к серверу

```bash
ssh root@89.23.99.152
# Введите пароль: dJN.wJ-YM*+J9b
```

### Шаг 2: Перейти в директорию проекта и обновить код

```bash
cd /home/easydrive
git pull origin main
```

### Шаг 3: Выполнить скрипт установки Docker (если еще не установлен)

```bash
sudo bash FIX_DOCKER_INSTALL.sh
```

### Шаг 4: Выполнить полный скрипт деплоя

```bash
sudo bash deploy_to_server.sh
```

## Вариант 2: Выполнить команды вручную

### 1. Подключение к серверу

```bash
ssh root@89.23.99.152
```

### 2. Исправление установки Docker

```bash
# Удалить конфликтующие пакеты
apt remove -y containerd containerd.io docker docker-engine docker.io
apt autoremove -y

# Установить Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Установить Docker Compose
apt update
apt install -y docker-compose

# Запустить Docker
systemctl start docker
systemctl enable docker
```

### 3. Обновить код и запустить приложение

```bash
cd /home/easydrive

# Обновить код
git stash  # если есть изменения
git pull origin main

# Остановить старое приложение
lsof -t -i:8000 | xargs -r kill 2>/dev/null || true
ps aux | grep "server.py" | grep -v grep | awk '{print $2}' | xargs -r kill 2>/dev/null || true

# Запустить Docker контейнеры
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Проверить статус
docker-compose ps
docker-compose logs -f
```

## Вариант 3: Использовать одну команду через SSH (без интерактивного подключения)

Если на вашем локальном компьютере установлен `sshpass`, можно выполнить:

```bash
# Сначала загрузить скрипт на сервер
scp deploy_to_server.sh root@89.23.99.152:/home/easydrive/

# Затем выполнить его
sshpass -p 'dJN.wJ-YM*+J9b' ssh root@89.23.99.152 'cd /home/easydrive && git pull origin main && sudo bash deploy_to_server.sh'
```

## Важные замечания

1. **Безопасность**: Пароль в команде виден в истории. После установки рекомендуется:
   - Настроить SSH ключи
   - Изменить пароль root
   - Использовать sudo для обычного пользователя вместо root

2. **Проверка**: После деплоя проверьте:
   - `docker-compose ps` - контейнеры должны быть в статусе "Up"
   - `curl http://localhost:8000/api/v2/heartbeat` - сервер должен отвечать

3. **Логи**: Если что-то не работает:
   ```bash
   docker-compose logs -f easydrive-server
   docker-compose logs -f postgres
   ```

## Быстрая команда для копирования (после подключения к серверу)

```bash
cd /home/easydrive && git pull origin main && apt remove -y containerd containerd.io docker docker-engine docker.io 2>/dev/null || true && curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh && rm get-docker.sh && apt update && apt install -y docker-compose && systemctl start docker && systemctl enable docker && lsof -t -i:8000 | xargs -r kill 2>/dev/null || true && docker-compose down && docker-compose build --no-cache && docker-compose up -d && sleep 5 && docker-compose ps && docker-compose logs --tail=50
```

