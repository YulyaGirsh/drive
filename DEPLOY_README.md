# 🚀 Автоматический деплой EasyDrive

Система автоматического деплоя для приложения EasyDrive с интеграцией Git и обновлением на сервере.

## 📋 Возможности

- ✅ Автоматический git add, commit и push
- ✅ SSH подключение к серверу и обновление кода
- ✅ Автоматический сброс кеша nginx
- ✅ Мониторинг изменений файлов в реальном времени
- ✅ Поддержка Windows (PowerShell, Batch) и Linux (Python)

## 🛠️ Установка

### 1. Установите зависимости

```bash
pip install -r requirements.txt
```

### 2. Установите sshpass (для SSH подключения)

**Windows (WSL или Git Bash):**
```bash
sudo apt-get update
sudo apt-get install sshpass
```

**Linux:**
```bash
sudo apt-get install sshpass
```

## 🚀 Использование

### Ручной деплой

**Windows:**
```cmd
deploy.bat
```
или
```powershell
.\deploy.ps1
```

**Linux/Mac:**
```bash
python deploy.py
```

### Автоматический мониторинг

**Windows:**
```cmd
auto_deploy.bat
```
или
```powershell
.\deploy.ps1 -Auto
```

**Linux/Mac:**
```bash
python auto_deploy.py
```

## ⚙️ Конфигурация

Настройки сервера находятся в файлах:
- `deploy.py` (строки 12-15)
- `deploy.ps1` (строки 8-11)

```python
SERVER_HOST = "89.23.99.152"
SERVER_USER = "root"
SERVER_PASSWORD = "dJN.wJ-YM*+J9b"
SERVER_PATH = "/var/www/easydrive"
```

## 📁 Отслеживаемые файлы

Система автоматически отслеживает изменения в:
- `.html` файлах
- `.css` файлах
- `.js` файлах
- `.py` файлах

Игнорируются:
- Служебные файлы (`.pyc`, `.log`, `.tmp`, etc.)
- Скрытые папки (`.git`, `__pycache__`, etc.)
- Папки IDE (`.vscode`, `.idea`)

## 🔄 Процесс деплоя

1. **Git операции:**
   - `git add .` - добавляет все изменения
   - `git commit -m "Auto-deploy: timestamp"` - создает коммит
   - `git push origin main` - отправляет в репозиторий

2. **Обновление сервера:**
   - SSH подключение к серверу
   - `cd /var/www/easydrive`
   - `git pull origin main`
   - `sudo systemctl reload nginx`

## 🛡️ Безопасность

- SSH подключение использует `StrictHostKeyChecking=no` для автоматизации
- Пароль передается через `sshpass`
- Рекомендуется использовать SSH ключи для продакшена

## 🐛 Устранение неполадок

### Ошибка "sshpass not found"
```bash
# Ubuntu/Debian
sudo apt-get install sshpass

# Windows (WSL)
wsl
sudo apt-get install sshpass
```

### Ошибка SSH подключения
- Проверьте правильность IP адреса и пароля
- Убедитесь, что сервер доступен
- Проверьте права доступа к папке проекта

### Ошибка git push
- Проверьте настройки git remote
- Убедитесь, что у вас есть права на push в репозиторий

## 📝 Логи

Все операции логируются в консоль с цветовой индикацией:
- 🟢 Зеленый - успешные операции
- 🔴 Красный - ошибки
- 🟡 Желтый - предупреждения
- 🔵 Синий - информационные сообщения

## 🔧 Настройка для продакшена

Для продакшена рекомендуется:

1. **Использовать SSH ключи вместо паролей:**
```bash
ssh-keygen -t rsa -b 4096
ssh-copy-id root@89.23.99.152
```

2. **Настроить webhook для автоматического деплоя:**
```python
# Вместо мониторинга файлов использовать webhook
```

3. **Добавить уведомления:**
```python
# Email, Slack, Telegram уведомления о статусе деплоя
```

## 📞 Поддержка

При возникновении проблем проверьте:
1. Логи в консоли
2. Настройки подключения к серверу
3. Права доступа к файлам и папкам
4. Статус сервисов на сервере
