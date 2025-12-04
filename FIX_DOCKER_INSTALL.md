# Решение проблемы с установкой Docker (конфликт containerd)

## Проблема
Ошибка: `containerd.io Conflicts: containerd`

Это происходит, когда на системе уже установлен старый `containerd` из репозиториев Ubuntu, а Docker пытается установить свой `containerd.io`.

## Решение

### Вариант 1: Удалить старый containerd и установить Docker правильно

```bash
# 1. Удалить старый containerd (если установлен)
sudo apt remove -y containerd

# 2. Удалить старые пакеты Docker (если есть)
sudo apt remove -y docker docker-engine docker.io containerd runc

# 3. Очистить кэш пакетов
sudo apt autoremove -y
sudo apt autoclean

# 4. Установить Docker через официальный скрипт (рекомендуется)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 5. Установить Docker Compose
sudo apt install -y docker-compose

# 6. Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# 7. Проверить установку
docker --version
docker-compose --version
```

### Вариант 2: Установить только docker.io (без containerd.io)

```bash
# 1. Удалить проблемные пакеты
sudo apt remove -y containerd containerd.io

# 2. Установить только docker.io (из репозиториев Ubuntu)
sudo apt update
sudo apt install -y docker.io docker-compose

# 3. Запустить Docker
sudo systemctl start docker
sudo systemctl enable docker

# 4. Добавить пользователя в группу docker
sudo usermod -aG docker $USER
newgrp docker

# 5. Проверить
docker --version
docker-compose --version
```

### Вариант 3: Использовать Docker из официального репозитория (рекомендуется)

```bash
# 1. Удалить все старые версии Docker и containerd
sudo apt remove -y docker docker-engine docker.io containerd containerd.io runc

# 2. Установить необходимые пакеты
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release

# 3. Добавить официальный GPG ключ Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# 4. Добавить репозиторий Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 5. Обновить список пакетов
sudo apt update

# 6. Установить Docker (без containerd.io, используя системный containerd)
sudo apt install -y docker-ce docker-ce-cli docker-compose-plugin

# 7. Если нужен старый docker-compose (не плагин)
sudo apt install -y docker-compose

# 8. Запустить Docker
sudo systemctl start docker
sudo systemctl enable docker

# 9. Добавить пользователя в группу
sudo usermod -aG docker $USER
newgrp docker

# 10. Проверить
docker --version
docker compose version  # или docker-compose --version
```

## Быстрое решение (одна команда)

```bash
# Удалить конфликтующие пакеты и установить Docker через официальный скрипт
sudo apt remove -y containerd containerd.io docker docker-engine docker.io 2>/dev/null || true
curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh && rm get-docker.sh
sudo apt install -y docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

## Проверка после установки

```bash
# Проверить версии
docker --version
docker-compose --version

# Проверить статус
sudo systemctl status docker

# Проверить работу (должно работать без sudo после newgrp)
docker ps
```

## Если все еще не работает

```bash
# Полная очистка и переустановка
sudo apt remove -y docker docker-engine docker.io containerd containerd.io runc docker-ce docker-ce-cli docker-compose docker-compose-plugin
sudo apt autoremove -y
sudo apt autoclean
sudo rm -rf /var/lib/docker
sudo rm -rf /etc/docker

# Затем используйте Вариант 3 выше
```

