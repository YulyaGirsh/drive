# Инструкция: Обновление кода на сервере с PostgreSQL

## Текущая ситуация

✅ **Код уже обновлен на сервере** (git pull выполнен успешно)  
❌ **Проблема**: Лимит Docker Hub не позволяет скачать образ PostgreSQL

## Решение 1: Авторизация в Docker Hub (рекомендуется)

### Шаг 1: Создайте бесплатный аккаунт Docker Hub
1. Перейдите на https://hub.docker.com/
2. Нажмите "Sign Up"
3. Зарегистрируйтесь (бесплатно)

### Шаг 2: Авторизуйтесь на сервере

**Вариант A: Через скрипт (Windows)**
```powershell
.\docker_login_on_server.ps1
# Введите логин и пароль Docker Hub
```

**Вариант B: Вручную через SSH**
```bash
ssh root@89.23.99.152
docker login
# Введите логин и пароль Docker Hub
cd /home/easydrive
docker-compose up -d
```

### Шаг 3: Проверка
```bash
docker-compose ps
docker-compose logs -f
```

## Решение 2: Подождать

Лимит Docker Hub обновляется каждые 6 часов. Подождите 30-60 минут и выполните:

```powershell
.\update_server_postgres.ps1
```

## Решение 3: Использовать уже скачанный образ (если есть)

Если образ PostgreSQL уже был скачан ранее, можно проверить:

```bash
ssh root@89.23.99.152
docker images | grep postgres
cd /home/easydrive
docker-compose up -d
```

## Проверка статуса после обновления

```bash
# Статус контейнеров
docker-compose ps

# Логи PostgreSQL
docker-compose logs postgres

# Логи приложения
docker-compose logs easydrive-server

# Проверка работы сервера
curl http://localhost:8000/api/v2/heartbeat
```

## Важно

- **PostgreSQL остается** - мы не переходим на SQLite
- **Код обновлен** - все изменения из GitHub уже на сервере
- **Нужно только запустить контейнеры** - после решения проблемы с Docker Hub

