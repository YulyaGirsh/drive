# Скрипты для обновления проекта на сервере

## Описание

Созданы скрипты для автоматического обновления проекта на сервере через SSH:
- `update_server.sh` - для Linux/macOS
- `update_server.bat` - для Windows (CMD)
- `update_server.ps1` - для Windows (PowerShell)

## Параметры подключения

- **Сервер:** `89.23.99.152`
- **Пользователь:** `root`
- **Директория проекта:** `/home/easydrive`

## Использование

### Linux/macOS

```bash
chmod +x update_server.sh
./update_server.sh
```

**Требования:**
- `sshpass` (установится автоматически или установите вручную: `sudo apt-get install sshpass`)

### Windows (CMD)

```cmd
update_server.bat
```

**Требования:**
- `plink.exe` из пакета PuTTY (должен быть в PATH)
- Скачать: https://www.chiark.greenend.org.uk/~sgtatham/putty/

### Windows (PowerShell)

```powershell
.\update_server.ps1
```

**Требования:**
- `ssh` или `plink` в PATH
- Для Windows 10/11: OpenSSH обычно уже установлен

## Что делает скрипт

1. ✅ Подключается к серверу по SSH
2. ✅ Обновляет код из Git репозитория (`git pull`)
3. ✅ Останавливает старые процессы на порту 8000
4. ✅ Останавливает старые Docker контейнеры
5. ✅ Собирает новые Docker образы
6. ✅ Запускает Docker контейнеры
7. ✅ Проверяет статус и логи
8. ✅ Проверяет работоспособность сервера

## Безопасность

⚠️ **ВАЖНО:** Пароль хранится в открытом виде в скриптах!

**Рекомендации:**
1. Используйте SSH ключи вместо паролей (более безопасно)
2. Ограничьте права доступа к скриптам: `chmod 600 update_server.sh`
3. После первого подключения настройте SSH ключи:

```bash
# Генерация SSH ключа (если еще нет)
ssh-keygen -t rsa -b 4096

# Копирование ключа на сервер
ssh-copy-id root@89.23.99.152

# После этого можно убрать пароль из скриптов
```

## Альтернатива: SSH ключи

После настройки SSH ключей можно использовать упрощенный скрипт:

```bash
#!/bin/bash
ssh root@89.23.99.152 << 'EOF'
cd /home/easydrive
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose ps
docker-compose logs --tail=50
EOF
```

## Устранение проблем

### Ошибка: "sshpass not found"
```bash
# Ubuntu/Debian
sudo apt-get install sshpass

# macOS
brew install hudochenkov/sshpass/sshpass
```

### Ошибка: "Permission denied"
```bash
chmod +x update_server.sh
```

### Ошибка: "Docker Compose not found"
Убедитесь, что на сервере установлен Docker и Docker Compose:
```bash
ssh root@89.23.99.152
docker --version
docker-compose --version
```

### Ошибка: "Cannot pull with rebase"
Скрипт автоматически сохраняет изменения в stash перед pull.

## Логи и отладка

Для просмотра подробных логов на сервере:
```bash
ssh root@89.23.99.152
cd /home/easydrive
docker-compose logs -f
```

## Ручное обновление

Если скрипт не работает, можно обновить вручную:

```bash
ssh root@89.23.99.152
cd /home/easydrive
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose ps
```

