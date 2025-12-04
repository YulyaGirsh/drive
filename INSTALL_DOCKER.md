# Установка Docker и Docker Compose на сервере

## Для Ubuntu/Debian

### 1. Установка Docker

```bash
# Обновить список пакетов
sudo apt update

# Установить необходимые пакеты
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавить официальный GPG ключ Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Добавить репозиторий Docker
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Обновить список пакетов
sudo apt update

# Установить Docker
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Проверить установку
sudo docker --version
```

### 2. Установка Docker Compose (если не установлен через плагин)

```bash
# Установить Docker Compose через apt (простой способ)
sudo apt install -y docker-compose

# Или установить последнюю версию вручную
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Сделать исполняемым
sudo chmod +x /usr/local/bin/docker-compose

# Проверить установку
docker-compose --version
```

### 3. Настройка прав доступа (чтобы не использовать sudo)

```bash
# Добавить текущего пользователя в группу docker
sudo usermod -aG docker $USER

# Применить изменения (выйти и зайти снова, или выполнить)
newgrp docker

# Проверить, что работает без sudo
docker ps
```

### 4. Включить автозапуск Docker

```bash
sudo systemctl enable docker
sudo systemctl start docker
sudo systemctl status docker
```

## Быстрая установка (одной командой)

```bash
# Для Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt install -y docker-compose
sudo usermod -aG docker $USER
newgrp docker
```

## Проверка установки

```bash
# Проверить версию Docker
docker --version

# Проверить версию Docker Compose
docker-compose --version

# Или для новой версии (плагин)
docker compose version

# Проверить, что Docker работает
sudo systemctl status docker
docker ps
```

## Если используется новая версия Docker Compose (плагин)

В новых версиях Docker Compose встроен как плагин. Используйте:

```bash
# Вместо docker-compose используйте:
docker compose build
docker compose up -d
docker compose down
```

## Обновление существующей установки

```bash
# Обновить Docker
sudo apt update
sudo apt upgrade docker-ce docker-ce-cli containerd.io

# Обновить Docker Compose
sudo apt upgrade docker-compose
```

## Устранение проблем

### Если команда docker-compose не найдена после установки:

```bash
# Проверить, где установлен
which docker-compose

# Если не найден, создать симлинк
sudo ln -s /usr/bin/docker-compose /usr/local/bin/docker-compose

# Или использовать docker compose (плагин)
docker compose version
```

### Если нужны права без sudo:

```bash
# Добавить пользователя в группу docker
sudo usermod -aG docker $USER

# Выйти из сессии и зайти снова, или:
newgrp docker
```

