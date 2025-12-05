# Решение проблемы с лимитом Docker Hub

## Проблема
При попытке скачать образ PostgreSQL появляется ошибка:
```
error from registry: You have reached your unauthenticated pull rate limit
```

## Решение 1: Авторизация в Docker Hub (рекомендуется)

### На сервере выполните:

```bash
# 1. Авторизуйтесь в Docker Hub
docker login

# Введите:
# Username: ваш_логин_docker_hub
# Password: ваш_пароль_docker_hub

# 2. После авторизации запустите контейнеры
cd /home/easydrive
docker-compose up -d
```

### Создание бесплатного аккаунта Docker Hub:
1. Перейдите на https://hub.docker.com/
2. Зарегистрируйтесь (бесплатно)
3. Авторизуйтесь на сервере через `docker login`

## Решение 2: Подождать

Лимит обновляется каждые 6 часов. Подождите 30-60 минут и попробуйте снова:

```bash
cd /home/easydrive
docker-compose pull postgres:15-alpine
docker-compose up -d
```

## Решение 3: Использовать альтернативный реестр

Можно использовать другие реестры (например, GitHub Container Registry), но это требует изменения `docker-compose.yml`.

## Проверка лимита

Чтобы проверить, сколько запросов осталось:

```bash
# Проверка через API Docker Hub
curl -I https://registry-1.docker.io/v2/ 2>&1 | grep -i "ratelimit"
```

## Автоматическая авторизация через скрипт

Если у вас есть учетные данные Docker Hub, можно добавить их в `config.env`:

```env
DOCKER_HUB_USERNAME=ваш_логин
DOCKER_HUB_PASSWORD=ваш_пароль
```

И затем в скрипте обновления добавить:
```bash
echo $DOCKER_HUB_PASSWORD | docker login -u $DOCKER_HUB_USERNAME --password-stdin
```

